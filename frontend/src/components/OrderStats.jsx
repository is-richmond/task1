import React, { useState, useEffect } from 'react';
import { getOrdersDirectly } from '../services/supabaseClient';

export default function OrderStats() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);

  useEffect(() => {
    loadStats();
    const interval = setInterval(loadStats, 10000); // Auto-refresh every 10s
    return () => clearInterval(interval);
  }, []);

  const loadStats = async () => {
    try {
      setLoading(true);
      const response = await getOrdersDirectly();
      setStats(response);
      setLastUpdate(new Date().toLocaleTimeString('ru-RU'));
      setError(null);
    } catch (err) {
      setError('Failed to load orders from Supabase');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getTotalSum = () => {
    if (!stats?.orders) return 0;
    return stats.orders.reduce((sum, order) => sum + (order.total || 0), 0);
  };

  const getOrdersByStatus = () => {
    if (!stats?.orders) return {};
    const byStatus = {};
    stats.orders.forEach(order => {
      const status = order.status || 'unknown';
      byStatus[status] = (byStatus[status] || 0) + 1;
    });
    return byStatus;
  };

  const getAverageOrderValue = () => {
    if (!stats?.orders || stats.orders.length === 0) return 0;
    return Math.round(getTotalSum() / stats.orders.length);
  };

  const statusCounts = getOrdersByStatus();

  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2 style={{ marginBottom: '0' }}>📊 Orders Statistics</h2>
        {lastUpdate && (
          <span style={{ fontSize: '12px', color: '#6b7280' }}>
            Last updated: {lastUpdate}
          </span>
        )}
      </div>
      
      {loading && <p style={{ textAlign: 'center', color: '#6b7280' }}>⏳ Loading...</p>}
      
      {error && <div className="error">{error}</div>}
      
      {stats && (
        <div className="stats">
          <div className="stat-item">
            <h3>📦 Total Orders</h3>
            <p className="stat-value">{stats.count}</p>
            <span style={{ fontSize: '12px', color: '#6b7280' }}>orders in Supabase</span>
          </div>
          
          <div className="stat-item">
            <h3>💰 Total Revenue</h3>
            <p className="stat-value">{getTotalSum().toLocaleString()}</p>
            <span style={{ fontSize: '12px', color: '#6b7280' }}>₸</span>
          </div>

          <div className="stat-item">
            <h3>📈 Avg Order Value</h3>
            <p className="stat-value">{getAverageOrderValue().toLocaleString()}</p>
            <span style={{ fontSize: '12px', color: '#6b7280' }}>₸</span>
          </div>

          {Object.keys(statusCounts).length > 0 && (
            <div className="stat-item">
              <h3>📋 Orders by Status</h3>
              <div style={{ fontSize: '13px', lineHeight: '2.2' }}>
                {Object.entries(statusCounts)
                  .sort((a, b) => b[1] - a[1])
                  .map(([status, count]) => (
                    <div key={status} style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ textTransform: 'capitalize', fontWeight: '500' }}>
                        {status === 'completed' ? '✅' : 
                         status === 'new' ? '🆕' : 
                         status === 'processing' ? '⚙️' : 
                         status === 'ready' ? '✓' : 
                         status === 'shipped' ? '📦' : 
                         '❌'} {status}
                      </span>
                      <strong style={{ color: 'var(--primary)' }}>{count}</strong>
                    </div>
                  ))}
              </div>
            </div>
          )}
          
          {stats.orders && stats.orders.length > 0 && (
            <div style={{ gridColumn: '1 / -1' }}>
              <h3 style={{ marginBottom: '15px', marginTop: '25px', fontSize: '16px', fontWeight: '700' }}>
                🆕 Recently Synced Orders
              </h3>
              <div className="orders-list">
                {stats.orders.slice(0, 5).map((order) => (
                  <div key={order.id} className="order-item">
                    <span className="order-num">#{order.number}</span>
                    <span className="order-customer">
                      {order.first_name} {order.last_name}
                    </span>
                    <span className="order-sum">{order.total?.toLocaleString()} ₸</span>
                  </div>
                ))}
              </div>
            </div>
          )}
          
          <div style={{ gridColumn: '1 / -1', marginTop: '25px' }}>
            <button onClick={loadStats} className="btn btn-primary">
              🔄 Refresh Data
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
