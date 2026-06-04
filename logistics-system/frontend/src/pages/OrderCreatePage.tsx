import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { productService } from "../services/productService";
import { orderService } from "../services/orderService";
import type { Product, OrderItem } from "../types";
import {
  PageTitle,
  Card,
  Button,
  Field,
  inputStyle,
  ErrorMessage,
  Loading,
  Empty,
} from "../components/ui";

export default function OrderCreatePage() {
  const navigate = useNavigate();

  // Produtos disponíveis para seleção
  const [products, setProducts] = useState<Product[]>([]);
  const [loadingProducts, setLoadingProducts] = useState(true);

  // Itens do pedido em construção
  const [items, setItems] = useState<OrderItem[]>([
    { produto_id: 0, quantidade: 1 },
  ]);

  const [apiError, setApiError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    productService
      .list(0, 100)
      .then((res) => setProducts(res.items))
      .finally(() => setLoadingProducts(false));
  }, []);

  function addItem() {
    setItems((prev) => [...prev, { produto_id: 0, quantidade: 1 }]);
  }

  function removeItem(index: number) {
    setItems((prev) => prev.filter((_, i) => i !== index));
  }

  function updateItem(index: number, field: keyof OrderItem, value: number) {
    setItems((prev) =>
      prev.map((item, i) => (i === index ? { ...item, [field]: value } : item))
    );
  }

  // Calcula total estimado com base nos preços atuais
  function getEstimatedTotal(): number {
    return items.reduce((acc, item) => {
      const product = products.find((p) => p.id === item.produto_id);
      return acc + (product ? product.preco * item.quantidade : 0);
    }, 0);
  }

  function validate(): string | null {
    if (items.length === 0) return "Adicione ao menos um item";
    for (const [i, item] of items.entries()) {
      if (!item.produto_id) return `Item ${i + 1}: selecione um produto`;
      if (item.quantidade < 1) return `Item ${i + 1}: quantidade mínima é 1`;
      const product = products.find((p) => p.id === item.produto_id);
      if (product && item.quantidade > product.quantidade_estoque) {
        return `Item ${i + 1}: estoque insuficiente (disponível: ${
          product.quantidade_estoque
        })`;
      }
    }
    // Verifica produtos duplicados
    const ids = items.map((i) => i.produto_id);
    if (new Set(ids).size !== ids.length)
      return "Produtos duplicados no pedido";
    return null;
  }

  async function handleSubmit() {
    const validationError = validate();
    if (validationError) {
      setApiError(validationError);
      return;
    }

    setSubmitting(true);
    setApiError("");
    try {
      await orderService.create({ itens: items });
      alert("Pedido criado com sucesso!");
      navigate("/");
    } catch (e: unknown) {
      setApiError(e instanceof Error ? e.message : "Erro ao criar pedido");
    } finally {
      setSubmitting(false);
    }
  }

  if (loadingProducts) return <Loading text="Carregando produtos..." />;

  return (
    <div>
      <PageTitle>Novo Pedido</PageTitle>

      {apiError && <ErrorMessage message={apiError} />}

      {products.length === 0 ? (
        <Empty text="Nenhum produto disponível. Cadastre produtos primeiro." />
      ) : (
        <>
          {items.map((item, index) => {
            const selected = products.find((p) => p.id === item.produto_id);
            return (
              <Card key={index}>
                <div style={styles.itemHeader}>
                  <strong style={{ color: "#94a3b8" }}>Item {index + 1}</strong>
                  {items.length > 1 && (
                    <Button variant="danger" onClick={() => removeItem(index)}>
                      Remover
                    </Button>
                  )}
                </div>

                <Field label="Produto *">
                  <select
                    style={inputStyle}
                    value={item.produto_id || ""}
                    onChange={(e) =>
                      updateItem(index, "produto_id", Number(e.target.value))
                    }
                  >
                    <option value="">Selecione um produto</option>
                    {products.map((p) => (
                      <option
                        key={p.id}
                        value={p.id}
                        disabled={p.quantidade_estoque === 0}
                      >
                        {p.nome} — R$ {Number(p.preco).toFixed(2)} (estoque:{" "}
                        {p.quantidade_estoque})
                      </option>
                    ))}
                  </select>
                </Field>

                <Field label="Quantidade *">
                  <input
                    style={inputStyle}
                    type="number"
                    min={1}
                    max={selected?.quantidade_estoque ?? 9999}
                    value={item.quantidade}
                    onChange={(e) =>
                      updateItem(
                        index,
                        "quantidade",
                        parseInt(e.target.value) || 1
                      )
                    }
                  />
                </Field>

                {selected && (
                  <div style={styles.subtotal}>
                    Subtotal:{" "}
                    <strong>
                      R$ {(selected.preco * item.quantidade).toFixed(2)}
                    </strong>
                  </div>
                )}
              </Card>
            );
          })}

          <div style={styles.actions}>
            <Button variant="ghost" onClick={addItem}>
              + Adicionar Item
            </Button>
          </div>

          {/* Resumo */}
          <Card>
            <div style={styles.total}>
              Total estimado:{" "}
              <strong style={{ color: "#4ade80", fontSize: 18 }}>
                R$ {getEstimatedTotal().toFixed(2)}
              </strong>
            </div>
            <div style={{ display: "flex", gap: 12, marginTop: 16 }}>
              <Button onClick={handleSubmit} disabled={submitting}>
                {submitting ? "Criando..." : "Criar Pedido"}
              </Button>
              <Button variant="ghost" onClick={() => navigate("/")}>
                Cancelar
              </Button>
            </div>
          </Card>
        </>
      )}
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  itemHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 16,
  },
  subtotal: {
    fontSize: 13,
    color: "#94a3b8",
    marginTop: -8,
  },
  actions: { marginBottom: 16 },
  total: { fontSize: 15, color: "#cbd5e1" },
};
