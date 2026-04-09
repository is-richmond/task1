import React, { useState, useEffect } from 'react';
import { uploadOrders } from '../services/api';
import { getHealth } from '../services/api';

export default function UploadOrders() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [backendStatus, setBackendStatus] = useState('checking');

  useEffect(() => {
    checkBackendStatus();
    const interval = setInterval(checkBackendStatus, 10000); // Check every 10s
    return () => clearInterval(interval);
  }, []);

  const checkBackendStatus = async () => {
    try {
      await getHealth();
      setBackendStatus('connected');
    } catch (err) {
      setBackendStatus('disconnected');
    }
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      processFile(file);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    const file = e.dataTransfer.files[0];
    if (file) {
      processFile(file);
    }
  };

  const processFile = (file) => {
    const reader = new FileReader();
    reader.onload = (event) => {
      try {
        const data = JSON.parse(event.target.result);
        setOrders(Array.isArray(data) ? data : []);
        setError(null);
      } catch (err) {
        setError('❌ Invalid JSON file');
      }
    };
    reader.readAsText(file);
  };

  const handleUpload = async () => {
    if (backendStatus !== 'connected') {
      setError('❌ Backend is not running. Please start the backend server first.');
      return;
    }

    if (orders.length === 0) {
      setError('❌ No orders to upload');
      return;
    }

    setLoading(true);
    setError(null);
    
    try {
      const response = await uploadOrders(orders);
      setResult(response.data);
      setOrders([]);
    } catch (err) {
      setError(err.response?.data?.error || '❌ Upload failed');
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setOrders([]);
    setResult(null);
    setError(null);
  };

  return (
    <div className="card">
      <h2>📦 Upload Orders</h2>
      
      {backendStatus !== 'connected' && (
        <div className="warning">
          <strong>⚠️ Backend Not Connected</strong>
          <p style={{ marginTop: '8px', marginBottom: '0', fontSize: '14px' }}>
            To upload orders, you need to start the backend server. Run:
          </p>
          <code style={{
            display: 'block',
            marginTop: '10px',
            padding: '10px',
            background: 'rgba(0,0,0,0.05)',
            borderRadius: '6px',
            fontFamily: 'monospace',
            fontSize: '12px',
            overflow: 'auto'
          }}>
            cd backend && python3 app.py
          </code>
        </div>
      )}
      
      <div
        className={`form-group ${dragActive ? 'drag-active' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        style={{
          padding: '30px',
          border: `2px dashed ${dragActive ? '#6366f1' : '#e5e7eb'}`,
          borderRadius: '12px',
          textAlign: 'center',
          backgroundColor: dragActive ? 'rgba(99, 102, 241, 0.05)' : 'transparent',
          cursor: backendStatus === 'connected' ? 'pointer' : 'not-allowed',
          transition: 'all 0.3s ease',
          opacity: backendStatus === 'connected' ? 1 : 0.6
        }}
      >
        <label style={{ cursor: backendStatus === 'connected' ? 'pointer' : 'not-allowed', marginBottom: '0' }}>
          <div style={{ fontSize: '32px', marginBottom: '10px' }}>📁</div>
          <strong style={{ fontSize: '16px', display: 'block', marginBottom: '8px' }}>
            {dragActive ? 'Drop file here' : 'Drag JSON file here'}
          </strong>
          <span style={{ color: '#6b7280', fontSize: '14px', display: 'block' }}>
            or click to select
          </span>
          <input 
            type="file" 
            accept=".json"
            onChange={handleFileUpload}
            disabled={loading || backendStatus !== 'connected'}
            style={{ display: 'none' }}
          />
        </label>
      </div>

      {orders.length > 0 && (
        <p className="info">
          ✅ Loaded <strong>{orders.length} orders</strong> ready to upload
        </p>
      )}

      <div style={{ display: 'flex', gap: '12px', marginTop: '20px' }}>
        <button 
          onClick={handleUpload} 
          disabled={loading || orders.length === 0 || backendStatus !== 'connected'}
          className="btn btn-primary"
        >
          {loading ? '⏳ Uploading...' : backendStatus !== 'connected' ? '🔌 Backend Required' : '🚀 Upload to RetailCRM'}
        </button>
        {orders.length > 0 && (
          <button 
            onClick={resetForm}
            className="btn btn-secondary"
            style={{ background: '#9ca3af', backgroundImage: 'none' }}
          >
            ↺ Clear
          </button>
        )}
      </div>

      {error && <div className="error">{error}</div>}

      {result && (
        <div className="success">
          <h3>✅ Upload Complete!</h3>
          <p style={{ marginBottom: '15px', fontSize: '16px' }}>
            Successfully uploaded <strong>{result.uploaded}/{result.total}</strong> orders
          </p>
          {result.results && (
            <div style={{ marginTop: '15px' }}>
              <div style={{ fontSize: '12px', color: '#047857', marginBottom: '10px' }}>
                Upload Details:
              </div>
              <ul style={{ columns: 2, columnGap: '20px' }}>
                {result.results.map((r, i) => (
                  <li key={i} style={{ marginBottom: '6px', fontSize: '13px' }}>
                    {r.success ? '✓' : '✗'} Order {i + 1}
                  </li>
                ))}
              </ul>
            </div>
          )}
          <button
            onClick={resetForm}
            className="btn btn-primary"
            style={{ marginTop: '15px' }}
          >
            📁 Upload More Orders
          </button>
        </div>
      )}
    </div>
  );
}
