import { useState } from 'react';
import ManufacturingOrders from './pages/ManufacturingOrders';
import Materials from './pages/Materials';
import Products from './pages/Products';
import './App.css';

type Page = 'orders' | 'products' | 'materials';

const NAV: Array<{ key: Page; label: string }> = [
  { key: 'orders', label: 'Ordres de fabrication' },
  { key: 'products', label: 'Produits' },
  { key: 'materials', label: 'Matières' },
];

export default function App() {
  const [page, setPage] = useState<Page>('orders');

  return (
    <div className="app">
      <nav className="nav">
        <span className="nav-brand">ERP FSM</span>
        <div className="nav-links">
          {NAV.map((n) => (
            <button
              key={n.key}
              className={`nav-link ${page === n.key ? 'active' : ''}`}
              onClick={() => setPage(n.key)}
            >
              {n.label}
            </button>
          ))}
        </div>
      </nav>
      <main className="main">
        {page === 'orders' && <ManufacturingOrders />}
        {page === 'products' && <Products />}
        {page === 'materials' && <Materials />}
      </main>
    </div>
  );
}