// ─── Produto ──────────────────────────────────────────────────────────────────

export interface Product {
  id: number;
  nome: string;
  sku: string;
  preco: number;
  quantidade_estoque: number;
  data_criacao: string;
}

export interface ProductCreate {
  nome: string;
  sku: string;
  preco: number;
  quantidade_estoque: number;
}

export interface ProductUpdate {
  nome?: string;
  preco?: number;
  quantidade_estoque?: number;
}

export interface ProductLowStock {
  id: number;
  nome: string;
  sku: string;
  quantidade_estoque: number;
  threshold: number;
}

// ─── Pedido ───────────────────────────────────────────────────────────────────

export interface OrderItem {
  produto_id: number;
  quantidade: number;
}

export interface OrderItemResponse {
  id: number;
  produto_id: number;
  quantidade: number;
  preco_unitario: number;
}

export type OrderStatus = "PENDENTE" | "CANCELADO";

export interface Order {
  id: number;
  status: OrderStatus;
  total: number; // era valor_total — campo real do model
  data_criacao: string;
  itens: OrderItemResponse[];
}

export interface OrderCreate {
  itens: OrderItem[];
}

// ─── Log ──────────────────────────────────────────────────────────────────────

export interface Log {
  id: number;
  acao: string; // era entidade_tipo/entidade_id — model real tem só acao
  detalhe: string; // era detalhes — campo real do model
  data_criacao: string; // era criado_em — campo real do model
}

// ─── Dashboard ────────────────────────────────────────────────────────────────

export interface Dashboard {
  total_produtos: number;
  pedidos_hoje: number;
  valor_total_estoque: number;
  itens_estoque_critico: number;
}

// ─── Paginação ────────────────────────────────────────────────────────────────

export interface Paginated<T> {
  items: T[];
  total_count: number;
  skip: number;
  limit: number;
}
