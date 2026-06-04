import { useEffect, useState } from "react";
import { orderService } from "../services/orderService";
import type { Order } from "../types";
import {
  PageTitle,
  Card,
  Button,
  Loading,
  ErrorMessage,
  Empty,
} from "../components/ui";

export default function OrderListPage() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [total, setTotal] = useState(0);
  const [skip, setSkip] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const LIMIT = 10;

  async function load(newSkip = 0) {
    setLoading(true);
    setError("");
    try {
      const res = await orderService.list(newSkip, LIMIT);
      setOrders(res.items);
      setTotal(res.total_count);
      setSkip(newSkip);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Erro ao carregar pedidos");
    } finally {
      setLoading(false);
    }
  }

  async function handleCancel(id: number) {
    if (!confirm(`Cancelar pedido #${id}?`)) return;
    try {
      await orderService.cancel(id);
      load(skip);
    } catch (e: unknown) {
      alert(e instanceof Error ? e.message : "Erro ao cancelar");
    }
  }

  useEffect(() => {
    load();
  }, []);

  return (
    <div>
      <PageTitle>Pedidos ({total})</PageTitle>
      {error && <ErrorMessage message={error} />}
      {loading && <Loading />}
      {!loading && orders.length === 0 && (
        <Empty text="Nenhum pedido encontrado." />
      )}

      {orders.map((o) => (
        <Card key={o.id}>
          <div style={styles.row}>
            <div>
              <div style={styles.header}>
                <span style={styles.id}>Pedido #{o.id}</span>
                <span
                  style={{
                    ...styles.badge,
                    background:
                      o.status === "cancelado" ? "#450a0a" : "#052e16",
                    color: o.status === "cancelado" ? "#fca5a5" : "#4ade80",
                  }}
                >
                  {o.status}
                </span>
              </div>
              <div style={styles.meta}>
                {o.itens.length} {o.itens.length === 1 ? "item" : "itens"} ·{" "}
                Total:{" "}
                <strong style={{ color: "#4ade80" }}>
                  R$ {Number(o.valor_total).toFixed(2)}
                </strong>
              </div>
              <div style={styles.date}>
                {new Date(o.data_criacao).toLocaleString("pt-BR")}
              </div>
            </div>
            {o.status === "pendente" && (
              <Button variant="danger" onClick={() => handleCancel(o.id)}>
                Cancelar
              </Button>
            )}
          </div>
        </Card>
      ))}

      {total > LIMIT && (
        <div style={styles.pagination}>
          <Button
            variant="ghost"
            disabled={skip === 0}
            onClick={() => load(skip - LIMIT)}
          >
            ← Anterior
          </Button>
          <span style={{ color: "#94a3b8", fontSize: 13 }}>
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
  header: { display: "flex", alignItems: "center", gap: 10, marginBottom: 6 },
  id: { fontSize: 15, fontWeight: 600, color: "#f1f5f9" },
  badge: {
    fontSize: 11,
    fontWeight: 600,
    padding: "2px 8px",
    borderRadius: 20,
  },
  meta: { fontSize: 13, color: "#94a3b8", marginBottom: 4 },
  date: { fontSize: 12, color: "#475569" },
  pagination: { display: "flex", alignItems: "center", gap: 12, marginTop: 16 },
};
