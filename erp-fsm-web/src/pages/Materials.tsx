import { Fragment, useEffect, useState } from 'react';
import { listMaterials, receiveMaterialStock, listStockMovements, createMaterial } from '../api/materials';
import type { Material } from '../types/material';
import type { StockMovement } from '../types/stockMovement';

const UNITS = ['unit', 'inch', 'foot', 'square_foot', 'cubic_foot'];

const UNIT_LABELS: Record<string, string> = {
  unit: 'Unité',
  inch: 'Pouce',
  foot: 'Pied',
  square_foot: 'Pied²',
  cubic_foot: 'Pied³',
};

const MOVEMENT_LABELS: Record<string, string> = {
  consumption: 'Consommation',
  receipt: 'Réception',
  adjustment: 'Ajustement',
};

const EMPTY_FORM = { sku: '', name: '', unit: 'unit', unit_cost: '', quantity_on_hand: '0' };

export default function Materials() {
  const [materials, setMaterials] = useState<Material[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [receiving, setReceiving] = useState<number | null>(null);
  const [receiveQty, setReceiveQty] = useState('');
  const [receiveRef, setReceiveRef] = useState('');
  const [movements, setMovements] = useState<{ id: number; data: StockMovement[] } | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState(EMPTY_FORM);
  const [submitting, setSubmitting] = useState(false);

  async function load() {
    try {
      setMaterials(await listMaterials());
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  async function handleCreate() {
    if (!form.sku || !form.name || !form.unit_cost) {
      alert('SKU, nom et coût unitaire sont obligatoires.');
      return;
    }
    setSubmitting(true);
    try {
      await createMaterial({
        sku: form.sku,
        name: form.name,
        unit: form.unit,
        unit_cost: Number(form.unit_cost),
        quantity_on_hand: Number(form.quantity_on_hand) || 0,
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

  async function handleReceive(id: number) {
    const qty = parseFloat(receiveQty);
    if (!qty || qty <= 0) { alert('Quantité invalide'); return; }
    try {
      await receiveMaterialStock(id, qty, receiveRef || null);
      setReceiving(null);
      setReceiveQty('');
      setReceiveRef('');
      await load();
    } catch (e) {
      alert(String(e));
    }
  }

  async function handleToggleMovements(id: number) {
    if (movements?.id === id) { setMovements(null); return; }
    const data = await listStockMovements(id);
    setMovements({ id, data });
  }

  if (loading) return <p className="page-state">Chargement…</p>;
  if (error) return <p className="page-state page-state--error">{error}</p>;

  return (
    <div className="page">
      <div className="page-header">
        <h1>Matières</h1>
        <button
          className={`btn ${showForm ? 'btn--ghost' : 'btn--primary'}`}
          onClick={() => { setShowForm((v) => !v); setForm(EMPTY_FORM); }}
        >
          {showForm ? 'Annuler' : '+ Nouvelle matière'}
        </button>
      </div>

      {showForm && (
        <div className="form-card">
          <div className="form-grid">
            <div className="form-field">
              <label>SKU</label>
              <input
                className="input input--full"
                placeholder="MAT-001"
                value={form.sku}
                onChange={(e) => setForm((f) => ({ ...f, sku: e.target.value }))}
              />
            </div>
            <div className="form-field form-field--wide">
              <label>Nom</label>
              <input
                className="input input--full"
                placeholder="Nom de la matière"
                value={form.name}
                onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
              />
            </div>
            <div className="form-field">
              <label>Unité</label>
              <select
                className="input input--full"
                value={form.unit}
                onChange={(e) => setForm((f) => ({ ...f, unit: e.target.value }))}
              >
                {UNITS.map((u) => (
                  <option key={u} value={u}>{UNIT_LABELS[u]}</option>
                ))}
              </select>
            </div>
            <div className="form-field">
              <label>Coût unitaire ($)</label>
              <input
                className="input input--full"
                type="number"
                min="0"
                step="0.01"
                placeholder="0.00"
                value={form.unit_cost}
                onChange={(e) => setForm((f) => ({ ...f, unit_cost: e.target.value }))}
              />
            </div>
            <div className="form-field">
              <label>Stock initial</label>
              <input
                className="input input--full"
                type="number"
                min="0"
                step="any"
                placeholder="0"
                value={form.quantity_on_hand}
                onChange={(e) => setForm((f) => ({ ...f, quantity_on_hand: e.target.value }))}
              />
            </div>
          </div>
          <div className="form-actions">
            <button className="btn btn--primary" disabled={submitting} onClick={handleCreate}>
              Créer la matière
            </button>
          </div>
        </div>
      )}

      {materials.length === 0 ? (
        <p className="page-state">Aucune matière.</p>
      ) : (
        <table className="table">
          <thead>
            <tr>
              <th>SKU</th>
              <th>Nom</th>
              <th>Unité</th>
              <th>Coût unitaire</th>
              <th>Stock</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {materials.map((mat) => (
              <Fragment key={mat.id}>
                <tr>
                  <td className="td--mono">{mat.sku}</td>
                  <td>{mat.name}</td>
                  <td>{UNIT_LABELS[mat.unit] ?? mat.unit}</td>
                  <td>{mat.unit_cost.toFixed(2)} $</td>
                  <td className={mat.quantity_on_hand === 0 ? 'td--zero' : ''}>
                    {mat.quantity_on_hand}
                  </td>
                  <td className="td--actions">
                    <button
                      className="btn btn--sm btn--secondary"
                      onClick={() => {
                        setReceiving(receiving === mat.id ? null : mat.id);
                        setReceiveQty('');
                        setReceiveRef('');
                      }}
                    >
                      Recevoir
                    </button>
                    <button
                      className={`btn btn--sm btn--ghost ${movements?.id === mat.id ? 'btn--ghost-active' : ''}`}
                      onClick={() => handleToggleMovements(mat.id)}
                    >
                      Mouvements
                    </button>
                  </td>
                </tr>

                {receiving === mat.id && (
                  <tr className="tr--sub">
                    <td colSpan={6}>
                      <div className="inline-form">
                        <input
                          type="number"
                          min="0.01"
                          step="any"
                          placeholder="Quantité"
                          value={receiveQty}
                          onChange={(e) => setReceiveQty(e.target.value)}
                          className="input"
                          autoFocus
                        />
                        <input
                          type="text"
                          placeholder="Référence (optionnel)"
                          value={receiveRef}
                          onChange={(e) => setReceiveRef(e.target.value)}
                          className="input input--wide"
                        />
                        <button className="btn btn--sm btn--primary" onClick={() => handleReceive(mat.id)}>
                          Confirmer
                        </button>
                        <button className="btn btn--sm btn--ghost" onClick={() => setReceiving(null)}>
                          Annuler
                        </button>
                      </div>
                    </td>
                  </tr>
                )}

                {movements?.id === mat.id && (
                  <tr className="tr--sub">
                    <td colSpan={6}>
                      <p className="sub-title">Historique des mouvements</p>
                      {movements.data.length === 0 ? (
                        <p className="sub-empty">Aucun mouvement enregistré.</p>
                      ) : (
                        <table className="table table--compact">
                          <thead>
                            <tr>
                              <th>Type</th>
                              <th>Quantité</th>
                              <th>Référence</th>
                              <th>Date</th>
                            </tr>
                          </thead>
                          <tbody>
                            {movements.data.map((m) => (
                              <tr key={m.id}>
                                <td>{MOVEMENT_LABELS[m.movement_type] ?? m.movement_type}</td>
                                <td className={m.quantity < 0 ? 'td--negative' : 'td--positive'}>
                                  {m.quantity > 0 ? '+' : ''}{m.quantity}
                                </td>
                                <td>{m.reference ?? '—'}</td>
                                <td>{new Date(m.created_at).toLocaleString('fr-CA')}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      )}
                    </td>
                  </tr>
                )}
              </Fragment>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}