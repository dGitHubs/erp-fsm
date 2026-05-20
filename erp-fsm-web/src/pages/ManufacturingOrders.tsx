import { useEffect, useState } from 'react';
import {
  listManufacturingOrders,
  updateManufacturingOrderStatus,
  consumeManufacturingOrder,
  createManufacturingOrder,
} from '../api/manufacturingOrders';
import { listCustomers } from '../api/customers';
import { listProducts } from '../api/products';
import { StatusBadge } from '../components/StatusBadge';
import type { ManufacturingOrder } from '../types/manufacturingOrder';
import type { Customer } from '../types/customer';
import type { Product } from '../types/product';

const TERMINAL = new Set(['done', 'cancelled']);

const NEXT_STATUSES: Record<string, Array<{ value: string; label: string; variant: string }>> = {
  draft: [
    { value: 'confirmed', label: 'Confirmer', variant: 'btn--secondary' },
    { value: 'cancelled', label: 'Annuler', variant: 'btn--danger' },
  ],
  confirmed: [
    { value: 'in_progress', label: 'Démarrer', variant: 'btn--secondary' },
    { value: 'cancelled', label: 'Annuler', variant: 'btn--danger' },
  ],
  in_progress: [
    { value: 'cancelled', label: 'Annuler', variant: 'btn--danger' },
  ],
};

const EMPTY_FORM = {
  reference: '',
  customer_id: '',
  product_id: '',
  quantity: '1',
  description: '',
};

export default function ManufacturingOrders() {
  const [orders, setOrders] = useState<ManufacturingOrder[]>([]);
  const [customersById, setCustomersById] = useState<Record<number, Customer>>({});
  const [productsById, setProductsById] = useState<Record<number, Product>>({});
  const [customerList, setCustomerList] = useState<Customer[]>([]);
  const [productList, setProductList] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState<number | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState(EMPTY_FORM);
  const [submitting, setSubmitting] = useState(false);

  async function load() {
    try {
      const [ordersData, customersData, productsData] = await Promise.all([
        listManufacturingOrders(),
        listCustomers(),
        listProducts(),
      ]);
      setOrders(ordersData);
      setCustomerList(customersData);
      setProductList(productsData);
      setCustomersById(Object.fromEntries(customersData.map((c) => [c.id, c])));
      setProductsById(Object.fromEntries(productsData.map((p) => [p.id, p])));
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  async function handleStatusChange(id: number, status: string) {
    setPending(id);
    try {
      await updateManufacturingOrderStatus(id, status);
      await load();
    } catch (e) {
      alert(String(e));
    } finally {
      setPending(null);
    }
  }

  async function handleConsume(id: number) {
    if (!confirm('Consommer les matières de cet ordre ?')) return;
    setPending(id);
    try {
      await consumeManufacturingOrder(id);
      await load();
    } catch (e) {
      alert(String(e));
    } finally {
      setPending(null);
    }
  }

  async function handleCreate() {
    if (!form.reference || !form.customer_id || !form.product_id || !form.quantity) {
      alert('Référence, client, produit et quantité sont obligatoires.');
      return;
    }
    setSubmitting(true);
    try {
      await createManufacturingOrder({
        reference: form.reference,
        customer_id: Number(form.customer_id),
        product_id: Number(form.product_id),
        quantity: Number(form.quantity),
        description: form.description || null,
      });
      setShowForm(false);
      setForm(EMPTY_FORM);
      await load();
    } catch (e) {
      alert(String(e));
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) return <p className="page-state">Chargement…</p>;
  if (error) return <p className="page-state page-state--error">{error}</p>;

  return (
    <div className="page">
      <div className="page-header">
        <h1>Ordres de fabrication</h1>
        <button
          className={`btn ${showForm ? 'btn--ghost' : 'btn--primary'}`}
          onClick={() => { setShowForm((v) => !v); setForm(EMPTY_FORM); }}
        >
          {showForm ? 'Annuler' : '+ Nouvel ordre'}
        </button>
      </div>

      {showForm && (
        <div className="form-card">
          <div className="form-grid">
            <div className="form-field">
              <label>Référence</label>
              <input
                className="input input--full"
                placeholder="OF-2026-001"
                value={form.reference}
                onChange={(e) => setForm((f) => ({ ...f, reference: e.target.value }))}
              />
            </div>
            <div className="form-field">
              <label>Client</label>
              <select
                className="input input--full"
                value={form.customer_id}
                onChange={(e) => setForm((f) => ({ ...f, customer_id: e.target.value }))}
              >
                <option value="">— Sélectionner —</option>
                {customerList.map((c) => (
                  <option key={c.id} value={c.id}>{c.name}</option>
                ))}
              </select>
            </div>
            <div className="form-field">
              <label>Produit</label>
              <select
                className="input input--full"
                value={form.product_id}
                onChange={(e) => setForm((f) => ({ ...f, product_id: e.target.value }))}
              >
                <option value="">— Sélectionner —</option>
                {productList.map((p) => (
                  <option key={p.id} value={p.id}>{p.name}</option>
                ))}
              </select>
            </div>
            <div className="form-field">
              <label>Quantité</label>
              <input
                className="input input--full"
                type="number"
                min="1"
                value={form.quantity}
                onChange={(e) => setForm((f) => ({ ...f, quantity: e.target.value }))}
              />
            </div>
            <div className="form-field form-field--wide">
              <label>Description</label>
              <input
                className="input input--full"
                placeholder="Optionnel"
                value={form.description}
                onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
              />
            </div>
          </div>
          <div className="form-actions">
            <button className="btn btn--primary" disabled={submitting} onClick={handleCreate}>
              Créer l'ordre
            </button>
          </div>
        </div>
      )}

      {orders.length === 0 ? (
        <p className="page-state">Aucun ordre de fabrication.</p>
      ) : (
        <table className="table">
          <thead>
            <tr>
              <th>Référence</th>
              <th>Client</th>
              <th>Produit</th>
              <th>Qté</th>
              <th>Statut</th>
              <th>Créé le</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {orders.map((order) => {
              const isDisabled = pending === order.id;
              const nextStatuses = NEXT_STATUSES[order.status] ?? [];
              const canConsume = !TERMINAL.has(order.status);
              return (
                <tr key={order.id}>
                  <td className="td--mono">{order.reference}</td>
                  <td>{customersById[order.customer_id]?.name ?? `#${order.customer_id}`}</td>
                  <td>{productsById[order.product_id]?.name ?? `#${order.product_id}`}</td>
                  <td>{order.quantity}</td>
                  <td><StatusBadge status={order.status} /></td>
                  <td>{new Date(order.created_at).toLocaleDateString('fr-CA')}</td>
                  <td className="td--actions">
                    {nextStatuses.map((s) => (
                      <button
                        key={s.value}
                        className={`btn btn--sm ${s.variant}`}
                        disabled={isDisabled}
                        onClick={() => handleStatusChange(order.id, s.value)}
                      >
                        {s.label}
                      </button>
                    ))}
                    {canConsume && (
                      <button
                        className="btn btn--sm btn--primary"
                        disabled={isDisabled}
                        onClick={() => handleConsume(order.id)}
                      >
                        Consommer
                      </button>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}
    </div>
  );
}