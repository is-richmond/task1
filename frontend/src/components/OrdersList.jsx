import React, { useState, useEffect } from 'react';
import { getOrdersDirectly } from '../services/supabaseClient';

export default function OrdersList() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [sortBy, setSortBy] = useState('date');
  const [filterStatus, setFilterStatus] = useState('all');
  const [lastUpdate, setLastUpdate] = useState(null);

  useEffect(() => {
    loadOrders();
    const interval = setInterval(loadOrders, 10000); // Auto-refresh every 10s
    return () => clearInterval(interval);
  }, []);

  const loadOrders = async () => {
    try {
      setLoading(true);
      const response = await getOrdersDirectly();
      setOrders(response.orders || []);
      setLastUpdate(new Date().toLocaleTimeString('ru-RU'));
      setError(null);
    } catch (err) {
      setError('Failed to load orders from Supabase');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      'new': 'status-new',
      'processing': 'status-processing',
      'ready': 'status-ready',
      'shipped': 'status-shipped',
      'completed': 'status-completed',
      'canceled': 'status-canceled'
    };
    return colors[status] || 'status-default';
  };

  const getStatusIcon = (status) => {
    const icons = {
      'new': '🆕',
      'processing': '⚙️',
      'ready': '✓',
      'shipped': '📦',
      'completed': '✅',
      'canceled': '❌'
    };
    return icons[status] || '•';
  };

  const sortOrders = (ordersToSort) => {
    const sorted = [...ordersToSort];
    if (sortBy === 'date') {
      sorted.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
    } else if (sortBy === 'amount') {
      sorted.sort((a, b) => (b.total || 0) - (a.total || 0));
    } else if (sortBy === 'name') {
      sorted.sort((a, b) => `${a.first_name} ${a.last_name}`.localeCompare(`${b.first_name} ${b.last_name}`));
    }
    return sorted;
  };

  const filterOrders = (ordersToFilter) => {
    if (filterStatus === 'all') return ordersToFilter;
    return ordersToFilter.filter(order => order.status === filterStatus);
  };

  const displayedOrders = sortOrders(filterOrders(orders));

  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '25px' }}>
        <h2 style={{ marginBottom: '0' }}>📋 All Orders</h2>
        {lastUpdate && (
          <span style={{ fontSize: '12px', color: '#6b7280' }}>
            Updated: {lastUpdate}
          </span>
        )}
      </div>

      {error && <div className="error">{error}</div>}
      
      {loading && <p style={{ textAlign: 'center', color: '#6b7280' }}>⏳ Loading orders...</p>}
      
      {!loading && orders.length === 0 && (
        <div style={{
          textAlign: 'center',
          padding: '40px 20px',
          background: 'rgba(99, 102, 241, 0.05)',
          borderRadius: '12px',
          border: '1px dashed var(--border)'
        }}>
          <p style={{ fontSize: '16px', color: '#6b7280', marginBottom: '10px' }}>
            📭 No orders synced to Supabase yet
          </p>
          <p style={{ fontSize: '13px', color: '#9ca3af' }}>
            Upload orders and wait for synchronization
          </p>
        </div>
      )}
      
      {orders.length > 0 && (
        <>
          <div style={{
            display: 'flex',
            gap: '15px',
            marginBottom: '20px',
            flexWrap: 'wrap',
            padding: '15px',
            background: 'var(--light)',
            borderRadius: '10px',
            alignItems: 'center'
          }}>
            <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
              <label style={{ fontSize: '13px', fontWeight: '600', color: '#6b7280' }}>
                Sort by:
              </label>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                style={{
                  padding: '8px 12px',
                  borderRadius: '8px',
                  border: '1px solid var(--border)',
                  background: 'white',
                  cursor: 'pointer',
                  fontSize: '13px'
                }}
              >
                <option value="date">📅 Date (newest)</option>
                <option value="amount">💰 Amount (highest)</option>
                <option value="name">👤 Name (A-Z)</option>
              </select>
            </div>

            <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
              <label style={{ fontSize: '13px', fontWeight: '600', color: '#6b7280' }}>
                Filter:
              </label>
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                style={{
                  padding: '8px 12px',
                  borderRadius: '8px',
                  border: '1px solid var(--border)',
                  background: 'white',
                  cursor: 'pointer',
                  fontSize: '13px'
                }}
              >
                <option value="all">All statuses</option>
                {Array.from(new Set(orders.map(o => o.status))).map(status => (
                  <option key={status} value={status}>
                    {getStatusIcon(status)} {status}
                  </option>
                ))}
              </select>
            </div>

            <span style={{ marginLeft: 'auto', fontSize: '13px', color: '#6b7280', fontWeight: '600' }}>
              Showing {displayedOrders.length} of {orders.length}
            </span>
          </div>

          <div className="orders-table">
            <table>
              <thead>
                <tr>
                  <th>Order #</th>
                  <th>Customer</th>
                  <th>Phone</th>
                  <th>Total Sum</th>
                  <th>Status</th>
                  <th>Date</th>
                </tr>
              </thead>
              <tbody>
                {displayedOrders.map((order) => (
                  <tr key={order.id}>
                    <td><strong style={{ color: 'var(--primary)' }}>#{order.number}</strong></td>
                    <td>
                      <div style={{ fontSize: '14px', fontWeight: '500' }}>
                        {order.first_name} {order.last_name}
                      </div>
                      {order.email && (
                        <div style={{ fontSize: '12px', color: '#6b7280' }}>
                          {order.email}
                        </div>
                      )}
                    </td>
                    <td style={{ fontSize: '13px', color: '#6b7280' }}>
                      {order.phone ? (
                        <a href={`tel:${order.phone}`} style={{ color: 'var(--primary)', textDecoration: 'none' }}>
                          {order.phone}
                        </a>
                      ) : '—'}
                    </td>
                    <td className="text-right">
                      <strong style={{ fontSize: '15px', color: 'var(--success)' }}>
                        {order.total?.toLocaleString()} ₸
                      </strong>
                    </td>
                    <td>
                      <span className={`status ${getStatusColor(order.status)}`}>
                        {getStatusIcon(order.status)} {order.status || '—'}
                      </span>
                    </td>
                    <td style={{ fontSize: '13px', color: '#6b7280' }}>
                      {order.created_at ? new Date(order.created_at).toLocaleDateString('ru-RU', {
                        year: 'numeric',
                        month: '2-digit',
                        day: '2-digit'
                      }) : '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}

      {orders.length > 0 && (
        <button onClick={loadOrders} className="btn btn-primary" style={{ marginTop: '20px' }}>
          🔄 Refresh Orders
        </button>
      )}
    </div>
  );
}
