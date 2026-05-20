import { apiFetch } from './client';
import type { Material } from '../types/material';
import type { StockMovement } from '../types/stockMovement';

export function listMaterials(): Promise<Material[]> {
  return apiFetch('/materials/');
}

export function receiveMaterialStock(
  id: number,
  quantity: number,
  reference: string | null,
): Promise<StockMovement> {
  return apiFetch(`/materials/${id}/receive`, {
    method: 'POST',
    body: JSON.stringify({ quantity, reference }),
  });
}

export function listStockMovements(id: number): Promise<StockMovement[]> {
  return apiFetch(`/materials/${id}/stock-movements`);
}

export function createMaterial(data: {
  sku: string;
  name: string;
  unit: string;
  unit_cost: number;
  quantity_on_hand: number;
}): Promise<Material> {
  return apiFetch('/materials/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}