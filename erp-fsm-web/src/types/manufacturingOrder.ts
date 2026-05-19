export type ManufacturingOrder = {
  id: number;
  reference: string;
  customer_id: number;
  product_id: number;
  quantity: number;
  description: string | null;
  status: string;
  created_at: string;
};

export type MaterialRequirementLine = {
  material_id: number;
  quantity_per_product: number;
  required_quantity: number;
};

export type ManufacturingOrderMaterialRequirements = {
  manufacturing_order_id: number;
  product_id: number;
  order_quantity: number;
  lines: MaterialRequirementLine[];
};

export type MaterialAvailabilityLine = {
  material_id: number;
  required_quantity: number;
  available_quantity: number;
  missing_quantity: number;
};

export type ManufacturingOrderMaterialAvailability = {
  manufacturing_order_id: number;
  product_id: number;
  order_quantity: number;
  can_produce: boolean;
  lines: MaterialAvailabilityLine[];
};