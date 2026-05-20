import { apiFetch } from './client';
import type { Product } from '../types/product';

export function listProducts(): Promise<Product[]> {
  return apiFetch('/products/');
}