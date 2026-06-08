import { useEffect, useState } from "react";
import { logService } from "../services/logService";
import type { Log } from "../types";
import {
  PageTitle,
  Card,
  Loading,
  ErrorMessage,
  Empty,
  Button,
} from "../components/ui";

const ACTION_COLORS: Record<string, string> = {
  criado: "#4ade80",
  atualizado: "#60a5fa",
  estoque_decrementado: "#f97316",
  estoque_estornado: "#a78bfa",
  cancelado: "#f87171",
};

export default function LogPage() {
  const [logs, setLogs] = useState<Log[]>([]);
  const [total, setTotal] = useState(0);
  const [skip, setSkip] = useState(0);
  const [filter, setFilter] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const LIMIT = 20;

  async function load(newSkip = 0, entidade_tipo?: string) {
    setLoading(true);
    setError("");
    try {
      const res = await logService.list(
        newSkip,
        LIMIT,
        entidade_tipo ? { entidade_tipo } : undefined
      );
      setLogs(res.items);
      setTotal(res.total_count);
      setSkip(newSkip);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Erro ao carregar logs");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load(0, filter || undefined);
  }, [filter]);

  return (
    <div>
      <PageTitle>Logs de Auditoria ({total})</PageTitle>

      {/* Filtro por tipo */}
      <div style={{ marginBottom: 20, display: "flex", gap: 8 }}>
        {["", "produto", "pedido"].map((tipo) => (
          <Button
            key={tipo}
            variant={filter === tipo ? "primary" : "ghost"}
            onClick={() => setFilter(tipo)}
          >
            {tipo === ""
              ? "Todos"
              : tipo.charAt(0).toUpperCase() + tipo.slice(1)}
          </Button>
        ))}
      </div>

      {error && <ErrorMessage message={error} />}
      {loading && <Loading />}
      {!loading && logs.length === 0 && <Empty text="Nenhum log encontrado." />}

      {logs.map((log) => (
        <Card key={log.id}>
          <div style={styles.row}>
            <div style={{ flex: 1 }}>
              <div style={styles.header}>
                <span style={styles.entity}>
                  {log.entidade_tipo} #{log.entidade_id}
                </span>
                <span
                  style={{
                    ...styles.action,
                    color: ACTION_COLORS[log.acao] ?? "#94a3b8",
                  }}
                >
                  {log.acao.replace(/_/g, " ")}
                </span>
              </div>
              {log.detalhes && (
                <pre style={styles.detail}>
                  {JSON.stringify(JSON.parse(log.detalhes), null, 2)}
                </pre>
              )}
            </div>
            <div style={styles.date}>
              {new Date(log.criado_em).toLocaleString("pt-BR")}
            </div>
          </div>
        </Card>
      ))}

      {total > LIMIT && (
        <div style={styles.pagination}>
          <Button
            variant="ghost"
            disabled={skip === 0}
            onClick={() => load(skip - LIMIT, filter || undefined)}
          >
            ← Anterior
          </Button>
          <span style={{ color: "#94a3b8", fontSize: 13 }}>
            {skip + 1}–{Math.min(skip + LIMIT, total)} de {total}
          </span>
          <Button
            variant="ghost"
            disabled={skip + LIMIT >= total}
            onClick={() => load(skip + LIMIT, filter || undefined)}
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
  entity: { fontSize: 14, fontWeight: 600, color: "#f1f5f9" },
  action: {
    fontSize: 12,
    fontWeight: 600,
    textTransform: "uppercase",
    letterSpacing: "0.05em",
  },
  detail: {
    fontSize: 11,
    background: "#0f172a",
    border: "1px solid #1e293b",
    borderRadius: 6,
    padding: "8px 12px",
    color: "#94a3b8",
    overflow: "auto",
    margin: 0,
  },
  date: { fontSize: 12, color: "#475569", whiteSpace: "nowrap" },
  pagination: { display: "flex", alignItems: "center", gap: 12, marginTop: 16 },
};
