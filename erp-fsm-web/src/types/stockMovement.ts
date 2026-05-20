export type StockMovement = {
  id: number;
  material_id: number;
  quantity: number;
  movement_type: 'consumption' | 'receipt' | 'adjustment';
  reference: string | null;
  created_at: string;
};