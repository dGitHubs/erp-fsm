import { useState } from 'react';
import ManufacturingOrders from './pages/ManufacturingOrders';
import Materials from './pages/Materials';
import './App.css';

type Page = 'orders' | 'materials';

export default function App() {
  const [page, setPage] = useState<Page>('orders');

  return (
    <div className="app">
      <nav className="nav">
        <span className="nav-brand">ERP FSM</span>
        <div className="nav-links">
          <button
            className={`nav-link ${page === 'orders' ? 'active' : ''}`}
            onClick={() => setPage('orders')}
          >
            Ordres de fabrication
          </button>
          <button
            className={`nav-link ${page === 'materials' ? 'active' : ''}`}
            onClick={() => setPage('materials')}
          >
            Matières
          </button>
        </div>
      </nav>
      <main className="main">
        {page === 'orders' && <ManufacturingOrders />}
        {page === 'materials' && <Materials />}
      </main>
    </div>
  );
}