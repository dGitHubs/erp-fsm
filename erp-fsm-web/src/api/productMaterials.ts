import { apiFetch } from './client';
import type { ProductMaterial } from '../types/productMaterial';

export function listProductMaterials(): Promise<ProductMaterial[]> {
  return apiFetch('/product-materials/');
}

export function createProductMaterial(data: {
  product_id: number;
  material_id: number;
  quantity: number;
}): Promise<ProductMaterial> {
  return apiFetch('/product-materials/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}