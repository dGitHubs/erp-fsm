export type Material = {
  id: number;
  sku: string;
  name: string;
  description: string | null;
  unit: string;
  unit_cost: number;
  quantity_on_hand: number;
  created_at: string;
};