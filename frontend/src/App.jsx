import React, { useEffect, useState } from 'react';
import UploadOrders from './components/UploadOrders';
import OrdersList from './components/OrdersList';
import OrderStats from './components/OrderStats';
import { getHealth } from './services/api';
import './index.css';

export default function App() {
  const [apiStatus, setApiStatus] = useState('checking');

  useEffect(() => {
    checkApiStatus();
    const interval = setInterval(checkApiStatus, 30000); // Check every 30s
    return () => clearInterval(interval);
  }, []);

  const checkApiStatus = async () => {
    try {
      await getHealth();
      setApiStatus('connected');
    } catch (err) {
      setApiStatus('disconnected');
      console.error('API not available:', err);
    }
  };

  return (
    <div className="container">
      <header className="header">
        <div>
          <h1>🛒 RetailCRM Orders Management</h1>
          <p style={{ margin: '8px 0 0 0', fontSize: '14px', opacity: 0.9 }}>
            Monitor, sync, and manage your orders across all channels
          </p>
        </div>
        <div className="status">
          API Status: <span className={`badge ${apiStatus}`}>
            {apiStatus === 'connected' ? '✅ Connected' : 
             apiStatus === 'checking' ? '⏳ Checking...' : 
             '❌ Disconnected'}
          </span>
        </div>
      </header>

      <main className="main">
        <section className="section">
          <UploadOrders />
        </section>

        <section className="section">
          <OrderStats />
        </section>

        <section className="section">
          <OrdersList />
        </section>
      </main>

      <footer className="footer">
        <p>© 2024 RetailCRM Orders System</p>
      </footer>
    </div>
  );
}
