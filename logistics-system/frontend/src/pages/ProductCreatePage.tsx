import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { productService } from "../services/productService";
import type { ProductCreate } from "../types";
import {
  PageTitle,
  Card,
  Button,
  Field,
  inputStyle,
  ErrorMessage,
} from "../components/ui";

const EMPTY: ProductCreate = {
  nome: "",
  sku: "",
  preco: 0,
  quantidade_estoque: 0,
};

type Errors = Partial<Record<keyof ProductCreate, string>>;

export default function ProductCreatePage() {
  const navigate = useNavigate();
  const [form, setForm] = useState<ProductCreate>(EMPTY);
  const [errors, setErrors] = useState<Errors>({});
  const [apiError, setApiError] = useState("");
  const [loading, setLoading] = useState(false);

  function set<K extends keyof ProductCreate>(key: K, value: ProductCreate[K]) {
    setForm((prev) => ({ ...prev, [key]: value }));
    setErrors((prev) => ({ ...prev, [key]: undefined }));
  }

  function validate(): boolean {
    const e: Errors = {};
    if (!form.nome.trim()) e.nome = "Nome é obrigatório";
    if (!form.sku.trim()) e.sku = "SKU é obrigatório";
    if (form.preco <= 0) e.preco = "Preço deve ser maior que zero";
    if (form.quantidade_estoque < 0)
      e.quantidade_estoque = "Estoque não pode ser negativo";
    setErrors(e);
    return Object.keys(e).length === 0;
  }

  async function handleSubmit() {
    if (!validate()) return;
    setLoading(true);
    setApiError("");
    try {
      await productService.create({
        ...form,
        preco: Number(form.preco),
        quantidade_estoque: Number(form.quantidade_estoque),
      });
      navigate("/");
    } catch (e: unknown) {
      setApiError(e instanceof Error ? e.message : "Erro ao cadastrar produto");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <PageTitle>Novo Produto</PageTitle>

      {apiError && <ErrorMessage message={apiError} />}

      <Card>
        <Field label="Nome *" error={errors.nome}>
          <input
            style={inputStyle}
            placeholder="Ex: Camiseta Básica"
            value={form.nome}
            onChange={(e) => set("nome", e.target.value)}
          />
        </Field>

        <Field label="SKU *" error={errors.sku}>
          <input
            style={inputStyle}
            placeholder="Ex: CAM-001"
            value={form.sku}
            onChange={(e) => set("sku", e.target.value.toUpperCase())}
          />
        </Field>

        <Field label="Preço (R$) *" error={errors.preco}>
          <input
            style={inputStyle}
            type="number"
            min="0.01"
            step="0.01"
            placeholder="0,00"
            value={form.preco || ""}
            onChange={(e) => set("preco", parseFloat(e.target.value) || 0)}
          />
        </Field>

        <Field
          label="Quantidade em Estoque *"
          error={errors.quantidade_estoque}
        >
          <input
            style={inputStyle}
            type="number"
            min="0"
            step="1"
            placeholder="0"
            value={form.quantidade_estoque || ""}
            onChange={(e) =>
              set("quantidade_estoque", parseInt(e.target.value) || 0)
            }
          />
        </Field>

        <div style={{ display: "flex", gap: 12, marginTop: 8 }}>
          <Button onClick={handleSubmit} disabled={loading}>
            {loading ? "Salvando..." : "Salvar Produto"}
          </Button>
          <Button variant="ghost" onClick={() => navigate("/")}>
            Cancelar
          </Button>
        </div>
      </Card>
    </div>
  );
}
