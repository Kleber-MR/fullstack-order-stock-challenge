import { BrowserRouter, Routes, Route, NavLink } from "react-router-dom";
import ProductListPage from "./pages/ProductListPage";
import ProductCreatePage from "./pages/ProductCreatePage";
import OrderCreatePage from "./pages/OrderCreatePage";

export default function App() {
  return (
    <BrowserRouter>
      <nav style={styles.nav}>
        <span style={styles.brand}>📦 Logistics</span>
        <NavLink to="/" end style={navStyle}>
          Produtos
        </NavLink>
        <NavLink to="/products/new" style={navStyle}>
          Novo Produto
        </NavLink>
        <NavLink to="/orders/new" style={navStyle}>
          Novo Pedido
        </NavLink>
      </nav>

      <main style={styles.main}>
        <Routes>
          <Route path="/" element={<ProductListPage />} />
          <Route path="/products/new" element={<ProductCreatePage />} />
          <Route path="/orders/new" element={<OrderCreatePage />} />
        </Routes>
      </main>
    </BrowserRouter>
  );
}

const navStyle = ({
  isActive,
}: {
  isActive: boolean;
}): React.CSSProperties => ({
  padding: "8px 16px",
  borderRadius: 6,
  textDecoration: "none",
  color: isActive ? "#fff" : "#cbd5e1",
  background: isActive ? "#3b82f6" : "transparent",
  fontWeight: isActive ? 600 : 400,
});

const styles: Record<string, React.CSSProperties> = {
  nav: {
    display: "flex",
    alignItems: "center",
    gap: 8,
    padding: "12px 24px",
    background: "#1e293b",
    borderBottom: "1px solid #334155",
  },
  brand: {
    color: "#f1f5f9",
    fontWeight: 700,
    fontSize: 18,
    marginRight: 16,
  },
  main: {
    padding: "32px 24px",
    maxWidth: 900,
    margin: "0 auto",
  },
};
