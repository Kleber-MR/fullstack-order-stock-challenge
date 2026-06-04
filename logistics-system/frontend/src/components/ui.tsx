import type { ReactNode } from "react";

// ─── Loading ──────────────────────────────────────────────────────────────────

export function Loading({ text = "Carregando..." }: { text?: string }) {
  return <p style={{ color: "#94a3b8", padding: "16px 0" }}>{text}</p>;
}

// ─── Error ────────────────────────────────────────────────────────────────────

export function ErrorMessage({ message }: { message: string }) {
  return (
    <div style={styles.error}>
      <strong>Erro:</strong> {message}
    </div>
  );
}

// ─── Empty ────────────────────────────────────────────────────────────────────

export function Empty({ text }: { text: string }) {
  return <p style={{ color: "#64748b", padding: "16px 0" }}>{text}</p>;
}

// ─── Card ─────────────────────────────────────────────────────────────────────

export function Card({ children }: { children: ReactNode }) {
  return <div style={styles.card}>{children}</div>;
}

// ─── Button ───────────────────────────────────────────────────────────────────

type ButtonVariant = "primary" | "danger" | "ghost";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
}

export function Button({ variant = "primary", style, ...props }: ButtonProps) {
  return (
    <button
      {...props}
      style={{ ...styles.btn, ...styles[variant], ...style }}
    />
  );
}

// ─── Form Field ───────────────────────────────────────────────────────────────

interface FieldProps {
  label: string;
  children: ReactNode;
  error?: string;
}

export function Field({ label, children, error }: FieldProps) {
  return (
    <div style={styles.field}>
      <label style={styles.label}>{label}</label>
      {children}
      {error && <span style={styles.fieldError}>{error}</span>}
    </div>
  );
}

export const inputStyle: React.CSSProperties = {
  width: "100%",
  padding: "8px 12px",
  borderRadius: 6,
  border: "1px solid #334155",
  background: "#1e293b",
  color: "#e2e8f0",
  outline: "none",
};

// ─── Page Title ───────────────────────────────────────────────────────────────

export function PageTitle({ children }: { children: ReactNode }) {
  return <h1 style={styles.title}>{children}</h1>;
}

// ─── Styles ───────────────────────────────────────────────────────────────────

const styles: Record<string, React.CSSProperties> = {
  error: {
    background: "#450a0a",
    border: "1px solid #7f1d1d",
    color: "#fca5a5",
    padding: "12px 16px",
    borderRadius: 8,
    margin: "8px 0",
  },
  card: {
    background: "#1e293b",
    border: "1px solid #334155",
    borderRadius: 10,
    padding: 24,
    marginBottom: 16,
  },
  btn: {
    padding: "8px 18px",
    borderRadius: 6,
    border: "none",
    cursor: "pointer",
    fontWeight: 600,
    fontSize: 14,
    transition: "opacity 0.15s",
  },
  primary: { background: "#3b82f6", color: "#fff" },
  danger: { background: "#dc2626", color: "#fff" },
  ghost: { background: "#334155", color: "#e2e8f0" },
  field: { display: "flex", flexDirection: "column", gap: 6, marginBottom: 16 },
  label: { fontSize: 13, fontWeight: 600, color: "#94a3b8" },
  fieldError: { fontSize: 12, color: "#f87171" },
  title: { fontSize: 22, fontWeight: 700, marginBottom: 24, color: "#f1f5f9" },
};
