import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { productService } from "../services/productService";
import { orderService } from "../services/orderService";
import type { Product, OrderCreate } from "../types";
import { PageTitle, Card, Button, ErrorMessage } from "../components/ui";

interface ItemForm {
  produto_id: number;
  quantidade: number;
}

export default function OrderCreatePage() {
  const navigate = useNavigate();
  const [products, setProducts] = useState<Product[]>([]);
  const [itens, setItens] = useState<ItemForm[]>([
    { produto_id: 0, quantidade: 1 },
  ]);
  const [apiError, setApiError] = useState("");
  const [loading, setLoading] = useState(false);
  const [loadingProducts, setLoadingProducts] = useState(true);

  // Carrega produtos disponíveis para o select
  useEffect(() => {
    productService
      .list({ in_stock: true, limit: 100 })
      .then((res) => setProducts(res.items))
      .catch(() => setApiError("Erro ao carregar produtos"))
      .finally(() => setLoadingProducts(false));
  }, []);

  function addItem() {
    setItens((prev) => [...prev, { produto_id: 0, quantidade: 1 }]);
  }

  function removeItem(index: number) {
    setItens((prev) => prev.filter((_, i) => i !== index));
  }

  function updateItem(index: number, field: keyof ItemForm, value: number) {
    setItens((prev) =>
      prev.map((item, i) => (i === index ? { ...item, [field]: value } : item))
    );
  }

  // Calcula preview do total com base nos preços dos produtos
  function calcTotal(): number {
    return itens.reduce((acc, item) => {
      const product = products.find((p) => p.id === item.produto_id);
      return acc + (product ? product.preco * item.quantidade : 0);
    }, 0);
  }

  function validate(): string | null {
    if (itens.length === 0) return "Adicione pelo menos um item";
    for (const item of itens) {
      if (!item.produto_id) return "Selecione um produto em todos os itens";
      if (item.quantidade < 1) return "Quantidade mínima é 1";
    }
    // Verifica duplicatas
    const ids = itens.map((i) => i.produto_id);
    if (new Set(ids).size !== ids.length) return "Não repita o mesmo produto";
    return null;
  }

  async function handleSubmit() {
    const erro = validate();
    if (erro) {
      setApiError(erro);
      return;
    }

    setLoading(true);
    setApiError("");

    const payload: OrderCreate = {
      itens: itens.map((i) => ({
        produto_id: i.produto_id,
        quantidade: i.quantidade,
      })),
    };

    try {
      await orderService.create(payload);
      navigate("/orders");
    } catch (e: unknown) {
      setApiError(e instanceof Error ? e.message : "Erro ao criar pedido");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <PageTitle>Novo Pedido</PageTitle>

      {apiError && <ErrorMessage message={apiError} />}

      <Card>
        {loadingProducts ? (
          <p style={{ color: "#94a3b8" }}>Carregando produtos...</p>
        ) : products.length === 0 ? (
          <p style={{ color: "#f87171" }}>
            Nenhum produto com estoque disponível.
          </p>
        ) : (
          <>
            {/* Lista de itens */}
            {itens.map((item, index) => {
              const productSelecionado = products.find(
                (p) => p.id === item.produto_id
              );
              return (
                <div key={index} style={styles.itemRow}>
                  {/* Select de produto */}
                  <div style={{ flex: 2 }}>
                    <label style={styles.label}>Produto</label>
                    <select
                      style={styles.select}
                      value={item.produto_id}
                      onChange={(e) =>
                        updateItem(index, "produto_id", Number(e.target.value))
                      }
                    >
                      <option value={0}>Selecione...</option>
                      {products.map((p) => (
                        <option key={p.id} value={p.id}>
                          {p.nome} — R$ {Number(p.preco).toFixed(2)} (estoque:{" "}
                          {p.quantidade_estoque})
                        </option>
                      ))}
                    </select>
                  </div>

                  {/* Quantidade */}
                  <div style={{ flex: 1 }}>
                    <label style={styles.label}>Quantidade</label>
                    <input
                      style={styles.input}
                      type="number"
                      min={1}
                      max={productSelecionado?.quantidade_estoque ?? 999}
                      value={item.quantidade}
                      onChange={(e) =>
                        updateItem(
                          index,
                          "quantidade",
                          Math.max(1, parseInt(e.target.value) || 1)
                        )
                      }
                    />
                  </div>

                  {/* Subtotal */}
                  <div style={{ flex: 1 }}>
                    <label style={styles.label}>Subtotal</label>
                    <div style={styles.subtotal}>
                      R${" "}
                      {productSelecionado
                        ? (productSelecionado.preco * item.quantidade).toFixed(
                            2
                          )
                        : "0.00"}
                    </div>
                  </div>

                  {/* Remover */}
                  {itens.length > 1 && (
                    <button
                      style={styles.removeBtn}
                      onClick={() => removeItem(index)}
                    >
                      ✕
                    </button>
                  )}
                </div>
              );
            })}

            {/* Total geral */}
            <div style={styles.totalRow}>
              <span style={{ color: "#94a3b8" }}>Total estimado:</span>
              <strong style={{ color: "#4ade80", fontSize: 18 }}>
                R$ {calcTotal().toFixed(2)}
              </strong>
            </div>

            {/* Ações */}
            <div style={styles.actions}>
              <Button variant="ghost" onClick={addItem}>
                + Adicionar Item
              </Button>
              <div style={{ display: "flex", gap: 12 }}>
                <Button onClick={handleSubmit} disabled={loading}>
                  {loading ? "Criando..." : "Criar Pedido"}
                </Button>
                <Button variant="ghost" onClick={() => navigate("/orders")}>
                  Cancelar
                </Button>
              </div>
            </div>
          </>
        )}
      </Card>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  itemRow: {
    display: "flex",
    gap: 12,
    alignItems: "flex-end",
    marginBottom: 16,
    paddingBottom: 16,
    borderBottom: "1px solid #1e293b",
  },
  label: {
    display: "block",
    fontSize: 12,
    color: "#94a3b8",
    marginBottom: 6,
  },
  select: {
    width: "100%",
    background: "#0f172a",
    border: "1px solid #334155",
    borderRadius: 8,
    color: "#f1f5f9",
    padding: "10px 12px",
    fontSize: 14,
  },
  input: {
    width: "100%",
    background: "#0f172a",
    border: "1px solid #334155",
    borderRadius: 8,
    color: "#f1f5f9",
    padding: "10px 12px",
    fontSize: 14,
    boxSizing: "border-box",
  },
  subtotal: {
    padding: "10px 12px",
    background: "#0f172a",
    border: "1px solid #1e293b",
    borderRadius: 8,
    color: "#4ade80",
    fontSize: 14,
    fontWeight: 600,
  },
  removeBtn: {
    background: "#450a0a",
    border: "none",
    borderRadius: 8,
    color: "#fca5a5",
    cursor: "pointer",
    padding: "10px 14px",
    fontSize: 14,
    alignSelf: "flex-end",
  },
  totalRow: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "12px 0",
    marginBottom: 16,
  },
  actions: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    flexWrap: "wrap",
    gap: 12,
  },
};
