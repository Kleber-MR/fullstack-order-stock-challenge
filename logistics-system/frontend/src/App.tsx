import {
  BrowserRouter,
  Routes,
  Route,
  NavLink,
  useLocation,
} from "react-router-dom";
import type { CSSProperties } from "react";

import DashboardPage from "./pages/DashboardPage";
import ProductListPage from "./pages/ProductListPage";
import ProductCreatePage from "./pages/ProductCreatePage";
import OrderListPage from "./pages/OrderListPage";
import OrderCreatePage from "./pages/OrderCreatePage";
import LogPage from "./pages/LogPage";

// ─── Ícones SVG inline ────────────────────────────────────────────────────────

const Icon = {
  dashboard: (
    <svg
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <rect x="3" y="3" width="7" height="7" />
      <rect x="14" y="3" width="7" height="7" />
      <rect x="14" y="14" width="7" height="7" />
      <rect x="3" y="14" width="7" height="7" />
    </svg>
  ),
  products: (
    <svg
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" />
    </svg>
  ),
  newProduct: (
    <svg
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <circle cx="12" cy="12" r="10" />
      <line x1="12" y1="8" x2="12" y2="16" />
      <line x1="8" y1="12" x2="16" y2="12" />
    </svg>
  ),
  orders: (
    <svg
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M9 17H7A5 5 0 0 1 7 7h2" />
      <path d="M15 7h2a5 5 0 1 1 0 10h-2" />
      <line x1="8" y1="12" x2="16" y2="12" />
    </svg>
  ),
  newOrder: (
    <svg
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
      <polyline points="14 2 14 8 20 8" />
      <line x1="12" y1="18" x2="12" y2="12" />
      <line x1="9" y1="15" x2="15" y2="15" />
    </svg>
  ),
  logs: (
    <svg
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
      <polyline points="14 2 14 8 20 8" />
      <line x1="16" y1="13" x2="8" y2="13" />
      <line x1="16" y1="17" x2="8" y2="17" />
      <polyline points="10 9 9 9 8 9" />
    </svg>
  ),
  logo: (
    <svg
      width="20"
      height="20"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M1 3h15v13H1z" />
      <path d="M16 8h4l3 3v5h-7V8z" />
      <circle cx="5.5" cy="18.5" r="2.5" />
      <circle cx="18.5" cy="18.5" r="2.5" />
    </svg>
  ),
};

// ─── Grupos de navegação ──────────────────────────────────────────────────────

const NAV_GROUPS = [
  {
    label: "VISÃO GERAL",
    items: [{ to: "/", label: "Dashboard", icon: Icon.dashboard, end: true }],
  },
  {
    label: "CATÁLOGO",
    items: [
      { to: "/products", label: "Produtos", icon: Icon.products, end: true },
      {
        to: "/products/new",
        label: "Novo Produto",
        icon: Icon.newProduct,
        end: false,
      },
    ],
  },
  {
    label: "OPERAÇÕES",
    items: [
      { to: "/orders", label: "Pedidos", icon: Icon.orders, end: true },
      {
        to: "/orders/new",
        label: "Novo Pedido",
        icon: Icon.newOrder,
        end: false,
      },
    ],
  },
  {
    label: "SISTEMA",
    items: [{ to: "/logs", label: "Auditoria", icon: Icon.logs, end: false }],
  },
];

// ─── Sidebar ──────────────────────────────────────────────────────────────────

function Sidebar() {
  return (
    <aside style={styles.sidebar}>
      {/* Logo */}
      <div style={styles.brand}>
        <div style={styles.brandIcon}>{Icon.logo}</div>
        <div>
          <div style={styles.brandName}>Logistics</div>
          <div style={styles.brandSub}>MANAGEMENT SUITE</div>
        </div>
      </div>

      {/* Nav */}
      <nav style={styles.nav}>
        {NAV_GROUPS.map((group) => (
          <div key={group.label} style={styles.navGroup}>
            <div style={styles.navGroupLabel}>{group.label}</div>
            {group.items.map(({ to, label, icon, end }) => (
              <NavLink
                key={to}
                to={to}
                end={end}
                style={({ isActive }) => ({
                  ...styles.navItem,
                  ...(isActive ? styles.navItemActive : {}),
                })}
              >
                <span style={styles.navIcon}>{icon}</span>
                {label}
              </NavLink>
            ))}
          </div>
        ))}
      </nav>

      {/* Footer */}
      <div style={styles.sidebarFooter}>
        <div style={styles.footerAvatar}>OR</div>
        <div>
          <div style={styles.footerName}>Operações BR</div>
          <div style={styles.footerEmail}>admin@logistics.os</div>
        </div>
      </div>
    </aside>
  );
}

// ─── Header ───────────────────────────────────────────────────────────────────

function Header() {
  const location = useLocation();

  const PAGE_TITLES: Record<string, string> = {
    "/": "Dashboard",
    "/products": "Produtos",
    "/products/new": "Novo Produto",
    "/orders": "Pedidos",
    "/orders/new": "Novo Pedido",
    "/logs": "Auditoria",
  };

  const title = PAGE_TITLES[location.pathname] ?? "Logistics";

  return (
    <header style={styles.header}>
      <div style={styles.headerBreadcrumb}>
        <span style={styles.headerBreadcrumbRoot}>Cargo OS</span>
        <span style={styles.headerBreadcrumbSep}>/</span>
        <span style={styles.headerBreadcrumbCurrent}>{title}</span>
      </div>
      <div style={styles.headerActions}>
        <div style={styles.searchBox}>
          <svg
            width="14"
            height="14"
            viewBox="0 0 24 24"
            fill="none"
            stroke="#64748b"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <circle cx="11" cy="11" r="8" />
            <line x1="21" y1="21" x2="16.65" y2="16.65" />
          </svg>
          <span style={{ color: "#475569", fontSize: 13 }}>
            Buscar pedido, SKU, cliente...
          </span>
        </div>
        <button style={styles.notifBtn}>
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
            <path d="M13.73 21a2 2 0 0 1-3.46 0" />
          </svg>
        </button>
      </div>
    </header>
  );
}

// ─── App ──────────────────────────────────────────────────────────────────────

export default function App() {
  return (
    <BrowserRouter>
      <div style={styles.shell}>
        <Sidebar />
        <div style={styles.main}>
          <Header />
          <main style={styles.content}>
            <Routes>
              <Route path="/" element={<DashboardPage />} />
              <Route path="/products" element={<ProductListPage />} />
              <Route path="/products/new" element={<ProductCreatePage />} />
              <Route path="/orders" element={<OrderListPage />} />
              <Route path="/orders/new" element={<OrderCreatePage />} />
              <Route path="/logs" element={<LogPage />} />
            </Routes>
          </main>
        </div>
      </div>
    </BrowserRouter>
  );
}

// ─── Estilos ──────────────────────────────────────────────────────────────────

const styles: Record<string, CSSProperties> = {
  shell: {
    display: "flex",
    height: "100vh",
    background: "#080d14",
    fontFamily: "'DM Sans', 'Segoe UI', sans-serif",
    overflow: "hidden",
  },

  // Sidebar
  sidebar: {
    width: 220,
    minWidth: 220,
    background: "#0d1520",
    borderRight: "1px solid #1a2535",
    display: "flex",
    flexDirection: "column",
    padding: "0 0 16px 0",
  },
  brand: {
    display: "flex",
    alignItems: "center",
    gap: 10,
    padding: "20px 18px 20px",
    borderBottom: "1px solid #1a2535",
    marginBottom: 8,
  },
  brandIcon: {
    width: 36,
    height: 36,
    background: "linear-gradient(135deg, #0ea5e9, #06b6d4)",
    borderRadius: 8,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    color: "#fff",
    flexShrink: 0,
  },
  brandName: {
    fontSize: 14,
    fontWeight: 700,
    color: "#f1f5f9",
    letterSpacing: "0.02em",
  },
  brandSub: {
    fontSize: 9,
    color: "#475569",
    letterSpacing: "0.12em",
    fontWeight: 600,
  },
  nav: {
    flex: 1,
    padding: "0 10px",
    overflowY: "auto",
  },
  navGroup: {
    marginBottom: 24,
  },
  navGroupLabel: {
    fontSize: 9,
    fontWeight: 700,
    color: "#334155",
    letterSpacing: "0.12em",
    padding: "0 8px",
    marginBottom: 4,
  },
  navItem: {
    display: "flex",
    alignItems: "center",
    gap: 10,
    padding: "8px 10px",
    borderRadius: 7,
    textDecoration: "none",
    color: "#64748b",
    fontSize: 13,
    fontWeight: 500,
    transition: "all 0.15s",
    marginBottom: 1,
  },
  navItemActive: {
    background: "rgba(14, 165, 233, 0.12)",
    color: "#38bdf8",
  },
  navIcon: {
    opacity: 0.8,
    flexShrink: 0,
  },
  sidebarFooter: {
    display: "flex",
    alignItems: "center",
    gap: 10,
    padding: "12px 18px",
    borderTop: "1px solid #1a2535",
    marginTop: "auto",
  },
  footerAvatar: {
    width: 32,
    height: 32,
    borderRadius: 8,
    background: "linear-gradient(135deg, #0ea5e9, #8b5cf6)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontSize: 11,
    fontWeight: 700,
    color: "#fff",
    flexShrink: 0,
  },
  footerName: { fontSize: 12, fontWeight: 600, color: "#94a3b8" },
  footerEmail: { fontSize: 10, color: "#334155" },

  // Main area
  main: {
    flex: 1,
    display: "flex",
    flexDirection: "column",
    overflow: "hidden",
  },
  header: {
    height: 56,
    minHeight: 56,
    background: "#0d1520",
    borderBottom: "1px solid #1a2535",
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    padding: "0 28px",
    gap: 16,
  },
  headerBreadcrumb: {
    display: "flex",
    alignItems: "center",
    gap: 8,
    fontSize: 13,
  },
  headerBreadcrumbRoot: { color: "#334155" },
  headerBreadcrumbSep: { color: "#1e293b" },
  headerBreadcrumbCurrent: { color: "#94a3b8", fontWeight: 500 },
  headerActions: {
    display: "flex",
    alignItems: "center",
    gap: 10,
  },
  searchBox: {
    display: "flex",
    alignItems: "center",
    gap: 8,
    background: "#0a1120",
    border: "1px solid #1a2535",
    borderRadius: 8,
    padding: "7px 14px",
    cursor: "text",
    minWidth: 240,
  },
  notifBtn: {
    width: 36,
    height: 36,
    background: "#0a1120",
    border: "1px solid #1a2535",
    borderRadius: 8,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    color: "#475569",
    cursor: "pointer",
  },
  content: {
    flex: 1,
    overflowY: "auto",
    padding: "28px 32px",
    background: "#080d14",
  },
};
