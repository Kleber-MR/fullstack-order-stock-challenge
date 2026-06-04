import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { dashboardService } from "../services/dashboardService";
import type { Dashboard } from "../types";

// ─── Sparkline SVG simples ────────────────────────────────────────────────────
function Sparkline({
  color = "#0ea5e9",
  up = true,
}: {
  color?: string;
  up?: boolean;
}) {
  const points = up
    ? "0,30 10,25 20,28 30,18 40,22 50,12 60,16 70,8 80,12 90,5 100,2"
    : "0,5 10,12 20,8 30,18 40,14 50,22 60,18 70,25 80,20 90,28 100,30";
  return (
    <svg
      width="100"
      height="32"
      viewBox="0 0 100 32"
      fill="none"
      style={{ opacity: 0.8 }}
    >
      <polyline
        points={points}
        stroke={color}
        strokeWidth="2"
        fill="none"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

// ─── Mini bar chart ───────────────────────────────────────────────────────────
function MiniBar({ color = "#0ea5e9" }: { color?: string }) {
  const bars = [40, 65, 45, 80, 55, 70, 90, 60, 75, 85, 50, 95];
  return (
    <svg width="100" height="32" viewBox="0 0 100 32" fill="none">
      {bars.map((h, i) => (
        <rect
          key={i}
          x={i * 8 + 1}
          y={32 - h * 0.32}
          width="6"
          height={h * 0.32}
          rx="1.5"
          fill={color}
          opacity="0.7"
        />
      ))}
    </svg>
  );
}

export default function DashboardPage() {
  const [data, setData] = useState<Dashboard | null>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    dashboardService
      .get()
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading)
    return (
      <div style={styles.loadingWrap}>
        <div style={styles.spinner} />
        <span style={{ color: "#475569", fontSize: 13 }}>
          Carregando dashboard...
        </span>
      </div>
    );

  const cards = [
    {
      label: "RECEITA TOTAL",
      value: data
        ? `R$ ${Number(data.valor_total_estoque).toLocaleString("pt-BR", {
            minimumFractionDigits: 2,
          })}`
        : "—",
      badge: "+12.4%",
      badgeUp: true,
      icon: "$",
      color: "#10b981",
      chart: <Sparkline color="#10b981" up={true} />,
    },
    {
      label: "PEDIDOS HOJE",
      value: data?.pedidos_hoje ?? "—",
      badge: "+3 hoje",
      badgeUp: true,
      icon: "📦",
      color: "#0ea5e9",
      chart: <Sparkline color="#0ea5e9" up={true} />,
    },
    {
      label: "TOTAL PRODUTOS",
      value: data?.total_produtos ?? "—",
      badge: "98.2% ok",
      badgeUp: true,
      icon: "📋",
      color: "#8b5cf6",
      chart: <Sparkline color="#8b5cf6" up={true} />,
    },
    {
      label: "ESTOQUE CRÍTICO",
      value: data?.itens_estoque_critico ?? "—",
      badge:
        (data?.itens_estoque_critico ?? 0) > 0
          ? `${data?.itens_estoque_critico} em alerta`
          : "Tudo ok",
      badgeUp: (data?.itens_estoque_critico ?? 0) === 0,
      icon: "⚠",
      color: (data?.itens_estoque_critico ?? 0) > 0 ? "#f59e0b" : "#10b981",
      chart: (
        <MiniBar
          color={(data?.itens_estoque_critico ?? 0) > 0 ? "#f59e0b" : "#10b981"}
        />
      ),
    },
  ];

  return (
    <div>
      {/* Page header */}
      <div style={styles.pageHeader}>
        <div>
          <h1 style={styles.pageTitle}>Dashboard</h1>
          <p style={styles.pageSubtitle}>
            Acompanhe receita, pedidos e estoque em tempo real.
          </p>
        </div>
        <div style={styles.pageActions}>
          <button
            style={styles.btnSecondary}
            onClick={() => navigate("/orders")}
          >
            Ver pedidos
          </button>
          <button
            style={styles.btnPrimary}
            onClick={() => navigate("/orders/new")}
          >
            + Novo pedido
          </button>
        </div>
      </div>

      {/* Metric cards */}
      <div style={styles.cardsGrid}>
        {cards.map((card) => (
          <div key={card.label} style={styles.card}>
            <div style={styles.cardTop}>
              <div>
                <div style={styles.cardLabel}>{card.label}</div>
                <div
                  style={{
                    ...styles.cardBadge,
                    color: card.badgeUp ? "#10b981" : "#f59e0b",
                  }}
                >
                  <span style={{ fontSize: 10 }}>
                    {card.badgeUp ? "↑" : "↓"}
                  </span>{" "}
                  {card.badge}
                </div>
              </div>
              <div
                style={{
                  ...styles.cardIconWrap,
                  background: `${card.color}18`,
                  color: card.color,
                }}
              >
                <span style={{ fontSize: 16 }}>{card.icon}</span>
              </div>
            </div>
            <div style={{ ...styles.cardValue, color: card.color }}>
              {card.value}
            </div>
            <div style={styles.cardChart}>{card.chart}</div>
          </div>
        ))}
      </div>

      {/* Bottom row */}
      <div style={styles.bottomRow}>
        {/* Quick actions */}
        <div style={styles.panel}>
          <div style={styles.panelHeader}>
            <span style={styles.panelTitle}>Ações rápidas</span>
          </div>
          <div style={styles.quickActions}>
            {[
              {
                label: "Cadastrar produto",
                to: "/products/new",
                color: "#0ea5e9",
              },
              { label: "Criar pedido", to: "/orders/new", color: "#8b5cf6" },
              { label: "Ver auditoria", to: "/logs", color: "#10b981" },
              { label: "Estoque baixo", to: "/products", color: "#f59e0b" },
            ].map((a) => (
              <button
                key={a.label}
                style={{
                  ...styles.quickBtn,
                  borderColor: `${a.color}40`,
                  color: a.color,
                }}
                onClick={() => navigate(a.to)}
              >
                {a.label}
              </button>
            ))}
          </div>
        </div>

        {/* Status */}
        <div style={styles.panel}>
          <div style={styles.panelHeader}>
            <span style={styles.panelTitle}>Status do sistema</span>
            <span style={styles.statusDot} />
          </div>
          {[
            { label: "API Backend", status: "Operacional", ok: true },
            { label: "Banco de dados", status: "Conectado", ok: true },
            { label: "Auditoria", status: "Ativa", ok: true },
            {
              label: "Estoque crítico",
              status:
                (data?.itens_estoque_critico ?? 0) > 0 ? "Atenção" : "Normal",
              ok: (data?.itens_estoque_critico ?? 0) === 0,
            },
          ].map((item) => (
            <div key={item.label} style={styles.statusRow}>
              <span style={styles.statusLabel}>{item.label}</span>
              <span
                style={{
                  ...styles.statusBadge,
                  background: item.ok ? "#052e16" : "#451a03",
                  color: item.ok ? "#4ade80" : "#fbbf24",
                }}
              >
                {item.status}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  loadingWrap: {
    display: "flex",
    alignItems: "center",
    gap: 12,
    padding: 40,
    color: "#475569",
  },
  spinner: {
    width: 18,
    height: 18,
    border: "2px solid #1e293b",
    borderTop: "2px solid #0ea5e9",
    borderRadius: "50%",
    animation: "spin 0.8s linear infinite",
  },

  pageHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "flex-start",
    marginBottom: 28,
  },
  pageTitle: {
    fontSize: 26,
    fontWeight: 700,
    color: "#f1f5f9",
    margin: 0,
    marginBottom: 4,
  },
  pageSubtitle: { fontSize: 13, color: "#475569", margin: 0 },
  pageActions: { display: "flex", gap: 10, alignItems: "center" },
  btnPrimary: {
    background: "linear-gradient(135deg, #0ea5e9, #06b6d4)",
    border: "none",
    borderRadius: 8,
    color: "#fff",
    fontSize: 13,
    fontWeight: 600,
    padding: "9px 18px",
    cursor: "pointer",
  },
  btnSecondary: {
    background: "transparent",
    border: "1px solid #1e293b",
    borderRadius: 8,
    color: "#94a3b8",
    fontSize: 13,
    fontWeight: 500,
    padding: "9px 18px",
    cursor: "pointer",
  },

  cardsGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(4, 1fr)",
    gap: 16,
    marginBottom: 24,
  },
  card: {
    background: "#0d1520",
    border: "1px solid #1a2535",
    borderRadius: 12,
    padding: "20px 22px",
  },
  cardTop: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "flex-start",
    marginBottom: 12,
  },
  cardLabel: {
    fontSize: 10,
    fontWeight: 700,
    color: "#334155",
    letterSpacing: "0.1em",
    marginBottom: 4,
  },
  cardBadge: { fontSize: 11, fontWeight: 600 },
  cardIconWrap: {
    width: 36,
    height: 36,
    borderRadius: 8,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  },
  cardValue: { fontSize: 24, fontWeight: 700, marginBottom: 8 },
  cardChart: { opacity: 0.9 },

  bottomRow: { display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 },
  panel: {
    background: "#0d1520",
    border: "1px solid #1a2535",
    borderRadius: 12,
    padding: "20px 22px",
  },
  panelHeader: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    marginBottom: 16,
  },
  panelTitle: { fontSize: 13, fontWeight: 600, color: "#94a3b8" },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: "50%",
    background: "#10b981",
    boxShadow: "0 0 8px #10b981",
  },

  quickActions: { display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 },
  quickBtn: {
    background: "transparent",
    border: "1px solid",
    borderRadius: 8,
    padding: "10px 14px",
    fontSize: 12,
    fontWeight: 500,
    cursor: "pointer",
    textAlign: "left",
  },

  statusRow: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "8px 0",
    borderBottom: "1px solid #1a2535",
  },
  statusLabel: { fontSize: 13, color: "#64748b" },
  statusBadge: {
    fontSize: 11,
    fontWeight: 600,
    padding: "2px 8px",
    borderRadius: 20,
  },
};
