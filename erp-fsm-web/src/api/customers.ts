import { apiFetch } from './client';
import type { Customer } from '../types/customer';

export function listCustomers(): Promise<Customer[]> {
  return apiFetch('/customers/');
}