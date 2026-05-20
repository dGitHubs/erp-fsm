export type Product = {
  id: number;
  sku: string;
  name: string;
  description: string | null;
  unit: string;
  width: number | null;
  height: number | null;
  depth: number | null;
  created_at: string;
};