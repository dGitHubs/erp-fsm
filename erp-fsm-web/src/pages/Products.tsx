import { Fragment, useEffect, useState } from 'react';
import { listProducts, createProduct } from '../api/products';
import { listMaterials } from '../api/materials';
import { listProductMaterials, createProductMaterial } from '../api/productMaterials';
import type { Product } from '../types/product';
import type { Material } from '../types/material';
import type { ProductMaterial } from '../types/productMaterial';

const PRODUCT_UNITS = ['unit', 'inch', 'foot', 'square_foot'];
const UNIT_LABELS: Record<string, string> = {
  unit: 'Unité',
  inch: 'Pouce',
  foot: 'Pied',
  square_foot: 'Pied²',
  cubic_foot: 'Pied³',
};

const EMPTY_FORM = { sku: '', name: '', unit: 'unit', width: '', height: '', depth: '' };

export default function Products() {
  const [products, setProducts] = useState<Product[]>([]);
  const [materials, setMaterials] = useState<Material[]>([]);
  const [bomLines, setBomLines] = useState<ProductMaterial[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expanded, setExpanded] = useState<number | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState(EMPTY_FORM);
  const [submitting, setSubmitting] = useState(false);
  const [addingBom, setAddingBom] = useState<number | null>(null);
  const [bomMaterialId, setBomMaterialId] = useState('');
  const [bomQuantity, setBomQuantity] = useState('');

  const materialsById = Object.fromEntries(materials.map((m) => [m.id, m]));

  async function load() {
    try {
      const [p, m, bom] = await Promise.all([
        listProducts(),
        listMaterials(),
        listProductMaterials(),
      ]);
      setProducts(p);
      setMaterials(m);
      setBomLines(bom);
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  async function handleCreateProduct() {
    if (!form.sku || !form.name) {
      alert('SKU et nom sont obligatoires.');
      return;
    }
    setSubmitting(true);
    try {
      await createProduct({
        sku: form.sku,
        name: form.name,
        unit: form.unit,
        width: form.width ? Number(form.width) : null,
        height: form.height ? Number(form.height) : null,
        depth: form.depth ? Number(form.depth) : null,
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

  async function handleAddBomLine(productId: number) {
    if (!bomMaterialId || !bomQuantity || Number(bomQuantity) <= 0) {
      alert('Matière et quantité sont obligatoires.');
      return;
    }
    try {
      await createProductMaterial({
        product_id: productId,
        material_id: Number(bomMaterialId),
        quantity: Number(bomQuantity),
      });
      setBomMaterialId('');
      setBomQuantity('');
      setAddingBom(null);
      await load();
    } catch (e) {
      alert(String(e));
    }
  }

  if (loading) return <p className="page-state">Chargement…</p>;
  if (error) return <p className="page-state page-state--error">{error}</p>;

  return (
    <div className="page">
      <div className="page-header">
        <h1>Produits</h1>
        <button
          className={`btn ${showForm ? 'btn--ghost' : 'btn--primary'}`}
          onClick={() => { setShowForm((v) => !v); setForm(EMPTY_FORM); }}
        >
          {showForm ? 'Annuler' : '+ Nouveau produit'}
        </button>
      </div>

      {showForm && (
        <div className="form-card">
          <div className="form-grid">
            <div className="form-field">
              <label>SKU</label>
              <input className="input input--full" placeholder="TABLE-001" value={form.sku}
                onChange={(e) => setForm((f) => ({ ...f, sku: e.target.value }))} />
            </div>
            <div className="form-field form-field--wide">
              <label>Nom</label>
              <input className="input input--full" placeholder="Nom du produit" value={form.name}
                onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))} />
            </div>
            <div className="form-field">
              <label>Unité</label>
              <select className="input input--full" value={form.unit}
                onChange={(e) => setForm((f) => ({ ...f, unit: e.target.value }))}>
                {PRODUCT_UNITS.map((u) => (
                  <option key={u} value={u}>{UNIT_LABELS[u]}</option>
                ))}
              </select>
            </div>
            <div className="form-field">
              <label>Largeur (mm)</label>
              <input className="input input--full" type="number" min="0" placeholder="Optionnel"
                value={form.width} onChange={(e) => setForm((f) => ({ ...f, width: e.target.value }))} />
            </div>
            <div className="form-field">
              <label>Hauteur (mm)</label>
              <input className="input input--full" type="number" min="0" placeholder="Optionnel"
                value={form.height} onChange={(e) => setForm((f) => ({ ...f, height: e.target.value }))} />
            </div>
            <div className="form-field">
              <label>Profondeur (mm)</label>
              <input className="input input--full" type="number" min="0" placeholder="Optionnel"
                value={form.depth} onChange={(e) => setForm((f) => ({ ...f, depth: e.target.value }))} />
            </div>
          </div>
          <div className="form-actions">
            <button className="btn btn--primary" disabled={submitting} onClick={handleCreateProduct}>
              Créer le produit
            </button>
          </div>
        </div>
      )}

      {products.length === 0 ? (
        <p className="page-state">Aucun produit.</p>
      ) : (
        <table className="table">
          <thead>
            <tr>
              <th>SKU</th>
              <th>Nom</th>
              <th>Unité</th>
              <th>Dimensions (l × h × p)</th>
              <th>Nomenclature</th>
            </tr>
          </thead>
          <tbody>
            {products.map((product) => {
              const lines = bomLines.filter((b) => b.product_id === product.id);
              const isExpanded = expanded === product.id;

              return (
                <Fragment key={product.id}>
                  <tr>
                    <td className="td--mono">{product.sku}</td>
                    <td>{product.name}</td>
                    <td>{UNIT_LABELS[product.unit] ?? product.unit}</td>
                    <td className="td--dims">
                      {product.width && product.height && product.depth
                        ? `${product.width} × ${product.height} × ${product.depth}`
                        : '—'}
                    </td>
                    <td>
                      <button
                        className={`btn btn--sm btn--ghost ${isExpanded ? 'btn--ghost-active' : ''}`}
                        onClick={() => setExpanded(isExpanded ? null : product.id)}
                      >
                        {lines.length} matière{lines.length !== 1 ? 's' : ''}
                      </button>
                    </td>
                  </tr>

                  {isExpanded && (
                    <tr className="tr--sub">
                      <td colSpan={5}>
                        <p className="sub-title">Nomenclature — {product.name}</p>

                        {lines.length === 0 ? (
                          <p className="sub-empty">Aucune matière liée.</p>
                        ) : (
                          <table className="table table--compact">
                            <thead>
                              <tr>
                                <th>SKU</th>
                                <th>Matière</th>
                                <th>Quantité</th>
                                <th>Unité</th>
                              </tr>
                            </thead>
                            <tbody>
                              {lines.map((line) => {
                                const mat = materialsById[line.material_id];
                                return (
                                  <tr key={line.id}>
                                    <td className="td--mono">{mat?.sku ?? `#${line.material_id}`}</td>
                                    <td>{mat?.name ?? `#${line.material_id}`}</td>
                                    <td>{line.quantity}</td>
                                    <td>{mat ? (UNIT_LABELS[mat.unit] ?? mat.unit) : '—'}</td>
                                  </tr>
                                );
                              })}
                            </tbody>
                          </table>
                        )}

                        {addingBom === product.id ? (
                          <div className="inline-form bom-form">
                            <select
                              className="input"
                              value={bomMaterialId}
                              onChange={(e) => setBomMaterialId(e.target.value)}
                              autoFocus
                            >
                              <option value="">— Choisir une matière —</option>
                              {materials
                                .filter((m) => !lines.some((l) => l.material_id === m.id))
                                .map((m) => (
                                  <option key={m.id} value={m.id}>{m.name} ({m.sku})</option>
                                ))}
                            </select>
                            <input
                              className="input"
                              type="number"
                              min="0.001"
                              step="any"
                              placeholder="Quantité"
                              value={bomQuantity}
                              onChange={(e) => setBomQuantity(e.target.value)}
                            />
                            <button className="btn btn--sm btn--primary" onClick={() => handleAddBomLine(product.id)}>
                              Ajouter
                            </button>
                            <button className="btn btn--sm btn--ghost" onClick={() => setAddingBom(null)}>
                              Annuler
                            </button>
                          </div>
                        ) : (
                          <button
                            className="btn btn--sm btn--secondary bom-add-btn"
                            onClick={() => { setAddingBom(product.id); setBomMaterialId(''); setBomQuantity(''); }}
                          >
                            + Ajouter une matière
                          </button>
                        )}
                      </td>
                    </tr>
                  )}
                </Fragment>
              );
            })}
          </tbody>
        </table>
      )}
    </div>
  );
}