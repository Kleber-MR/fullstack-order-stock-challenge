import { useEffect, useState } from "react";
import { productService } from "../services/productService";
import type { Product } from "../types";
import {
  PageTitle,
  Card,
  Button,
  Loading,
  ErrorMessage,
  Empty,
} from "../components/ui";

export default function ProductListPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [total, setTotal] = useState(0);
  const [skip, setSkip] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const LIMIT = 10;

  async function load(newSkip = 0) {
    setLoading(true);
    setError("");
    try {
      const res = await productService.list(newSkip, LIMIT);
      setProducts(res.items);
      setTotal(res.total);
      setSkip(newSkip);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Erro ao carregar produtos");
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete(id: number, nome: string) {
    if (!confirm(`Deletar "${nome}"?`)) return;
    try {
      await productService.remove(id);
      load(skip);
    } catch (e: unknown) {
      alert(e instanceof Error ? e.message : "Erro ao deletar");
    }
  }

  useEffect(() => {
    load();
  }, []);

  return (
    <div>
      <PageTitle>Produtos ({total})</PageTitle>

      {error && <ErrorMessage message={error} />}
      {loading && <Loading />}

      {!loading && products.length === 0 && (
        <Empty text="Nenhum produto cadastrado." />
      )}

      {products.map((p) => (
        <Card key={p.id}>
          <div style={styles.row}>
            <div>
              <div style={styles.nome}>{p.nome}</div>
              <div style={styles.meta}>
                SKU: <strong>{p.sku}</strong> · Preço:{" "}
                <strong>R$ {Number(p.preco).toFixed(2)}</strong> · Estoque:{" "}
                <strong
                  style={{
                    color: p.quantidade_estoque === 0 ? "#f87171" : "#4ade80",
                  }}
                >
                  {p.quantidade_estoque}
                </strong>
              </div>
              <div style={styles.date}>
                Criado em {new Date(p.data_criacao).toLocaleDateString("pt-BR")}
              </div>
            </div>
            <Button variant="danger" onClick={() => handleDelete(p.id, p.nome)}>
              Deletar
            </Button>
          </div>
        </Card>
      ))}

      {/* Paginação */}
      {total > LIMIT && (
        <div style={styles.pagination}>
          <Button
            variant="ghost"
            disabled={skip === 0}
            onClick={() => load(skip - LIMIT)}
          >
            ← Anterior
          </Button>
          <span style={styles.pageInfo}>
            {skip + 1}–{Math.min(skip + LIMIT, total)} de {total}
          </span>
          <Button
            variant="ghost"
            disabled={skip + LIMIT >= total}
            onClick={() => load(skip + LIMIT)}
          >
            Próximo →
          </Button>
        </div>
      )}
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  row: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "flex-start",
    gap: 16,
  },
  nome: { fontSize: 16, fontWeight: 600, color: "#f1f5f9", marginBottom: 6 },
  meta: { fontSize: 13, color: "#94a3b8", marginBottom: 4 },
  date: { fontSize: 12, color: "#475569" },
  pagination: {
    display: "flex",
    alignItems: "center",
    gap: 12,
    marginTop: 16,
  },
  pageInfo: { fontSize: 13, color: "#94a3b8" },
};
