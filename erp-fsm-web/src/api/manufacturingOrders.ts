import { apiFetch } from './client';
import type { ManufacturingOrder } from '../types/manufacturingOrder';

export function listManufacturingOrders(): Promise<ManufacturingOrder[]> {
  return apiFetch('/manufacturing-orders/');
}

export function updateManufacturingOrderStatus(
  id: number,
  status: string,
): Promise<ManufacturingOrder> {
  return apiFetch(`/manufacturing-orders/${id}/status`, {
    method: 'PATCH',
    body: JSON.stringify({ status }),
  });
}

export function consumeManufacturingOrder(id: number): Promise<unknown> {
  return apiFetch(`/manufacturing-orders/${id}/consume`, { method: 'POST' });
}

export function createManufacturingOrder(data: {
  reference: string;
  customer_id: number;
  product_id: number;
  quantity: number;
  description: string | null;
}): Promise<ManufacturingOrder> {
  return apiFetch('/manufacturing-orders/', {
    method: 'POST',
    body: JSON.stringify({ ...data, status: 'draft' }),
  });
}