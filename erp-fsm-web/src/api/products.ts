import { apiFetch } from './client';
import type { Product } from '../types/product';

export function listProducts(): Promise<Product[]> {
  return apiFetch('/products/');
}

export function createProduct(data: {
  sku: string;
  name: string;
  unit: string;
  width: number | null;
  height: number | null;
  depth: number | null;
}): Promise<Product> {
  return apiFetch('/products/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}