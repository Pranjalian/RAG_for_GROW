import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { API_BASE_URL } from '../../config';

export default function AdminDashboard() {
  const [urls, setUrls] = useState([]);
  const [newUrl, setNewUrl] = useState('');
  const [sourceType, setSourceType] = useState('mutual_fund');
  const [label, setLabel] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [syncStatus, setSyncStatus] = useState('');
  
  const navigate = useNavigate();

  const getHeaders = () => {
    const token = localStorage.getItem('admin_token');
    return { Authorization: `Bearer ${token}` };
  };

  const fetchUrls = async () => {
    try {
      const res = await axios.get(`${API_BASE_URL}/api/admin/status`, { headers: getHeaders() });
      setUrls(res.data.per_source || []);
      setIsLoading(false);
    } catch (err) {
      if (err.response?.status === 401) {
        navigate('/admin/login');
      } else {
        setError('Failed to load sources.');
        setIsLoading(false);
      }
    }
  };

  useEffect(() => {
    fetchUrls();
  }, []);

  const handleAddUrl = async (e) => {
    e.preventDefault();
    setError('');
    
    try {
      await axios.post(`${API_BASE_URL}/api/admin/urls`, {
        url: newUrl,
        source_type: sourceType,
        label: label || 'Custom Source'
      }, { headers: getHeaders() });
      
      setNewUrl('');
      setLabel('');
      fetchUrls(); // Refresh list
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to add URL.');
    }
  };

  const handleDeleteUrl = async (id) => {
    if (!confirm('Are you sure you want to remove this source?')) return;
    
    try {
      await axios.delete(`${API_BASE_URL}/api/admin/urls/${id}`, { headers: getHeaders() });
      fetchUrls();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to delete URL.');
    }
  };

  const handleSync = async () => {
    setSyncStatus('Syncing...');
    try {
      const res = await axios.post(`${API_BASE_URL}/api/admin/sync`, {}, { headers: getHeaders() });
      setSyncStatus(`Sync Complete: ${res.data.success} successful, ${res.data.failed} failed.`);
      fetchUrls(); // Refresh statuses
      setTimeout(() => setSyncStatus(''), 5000);
    } catch (err) {
      setSyncStatus('Sync failed.');
      setTimeout(() => setSyncStatus(''), 5000);
    }
  };

  if (isLoading) {
    return <div className="p-xl text-center text-on-surface">Loading Dashboard...</div>;
  }

  return (
    <div className="flex-1 p-lg overflow-y-auto pb-[120px]">
      <div className="max-w-6xl mx-auto flex flex-col gap-xl mt-8">
        
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="font-headline-lg text-headline-lg font-bold text-primary">Admin Control Panel</h1>
            <p className="text-on-surface-variant font-title-md mt-2">Manage Knowledge Sources & Sync Operations</p>
          </div>
          <button 
            onClick={handleSync}
            className="bg-primary-container text-black px-4 py-2 rounded-lg font-title-md font-bold hover:bg-primary transition-colors flex items-center gap-2"
          >
            <span className="material-symbols-outlined">sync</span>
            Force Sync Now
          </button>
        </div>

        {error && (
          <div className="bg-error-container text-on-error-container p-4 rounded-lg font-title-md border border-error/20">
            {error}
          </div>
        )}
        
        {syncStatus && (
          <div className="bg-tertiary-container/20 text-tertiary p-4 rounded-lg font-title-md border border-tertiary/20">
            {syncStatus}
          </div>
        )}

        {/* Add Source Card */}
        <div className="glass-panel p-xl rounded-2xl flex flex-col gap-md">
          <h2 className="font-headline-md text-headline-md text-on-surface">Add New Source</h2>
          <form onSubmit={handleAddUrl} className="flex gap-4 items-end flex-wrap">
            <div className="flex-1 min-w-[200px] flex flex-col gap-1">
              <label className="text-sm text-on-surface-variant">Groww.in URL</label>
              <input 
                type="url" 
                value={newUrl}
                onChange={e => setNewUrl(e.target.value)}
                placeholder="https://groww.in/mutual-funds/..."
                className="bg-surface-container-highest border border-white/10 rounded-lg p-3 text-on-surface focus:border-primary focus:outline-none"
                required
              />
            </div>
            <div className="w-[200px] flex flex-col gap-1">
              <label className="text-sm text-on-surface-variant">Type</label>
              <select 
                value={sourceType}
                onChange={e => setSourceType(e.target.value)}
                className="bg-surface-container-highest border border-white/10 rounded-lg p-3 text-on-surface focus:border-primary focus:outline-none"
              >
                <option value="mutual_fund">Mutual Fund</option>
                <option value="nfo">NFO</option>
                <option value="market_news">Market News</option>
                <option value="help_article">Help Article</option>
              </select>
            </div>
            <div className="flex-1 min-w-[150px] flex flex-col gap-1">
              <label className="text-sm text-on-surface-variant">Label (Optional)</label>
              <input 
                type="text" 
                value={label}
                onChange={e => setLabel(e.target.value)}
                placeholder="e.g. Parag Parikh Flexi"
                className="bg-surface-container-highest border border-white/10 rounded-lg p-3 text-on-surface focus:border-primary focus:outline-none"
              />
            </div>
            <button 
              type="submit"
              className="bg-primary/20 text-primary border border-primary/30 px-6 py-3 rounded-lg font-title-md hover:bg-primary hover:text-black transition-colors"
            >
              Add Source
            </button>
          </form>
        </div>

        {/* Source List Table */}
        <div className="glass-panel rounded-2xl overflow-hidden flex flex-col">
          <div className="p-lg border-b border-white/10 bg-surface-container-highest/50">
            <h2 className="font-headline-md text-headline-md text-on-surface">Active Sources ({urls.length})</h2>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/10 text-on-surface-variant text-sm font-label-mono bg-surface-container-high">
                  <th className="p-4 font-normal">URL</th>
                  <th className="p-4 font-normal">Label</th>
                  <th className="p-4 font-normal">Type</th>
                  <th className="p-4 font-normal">Status</th>
                  <th className="p-4 font-normal text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                {urls.length === 0 ? (
                  <tr>
                    <td colSpan="5" className="p-8 text-center text-on-surface-variant">
                      No active sources found. Add one above.
                    </td>
                  </tr>
                ) : (
                  urls.map(url => (
                    <tr key={url.id} className="border-b border-white/5 hover:bg-white/5 transition-colors group">
                      <td className="p-4">
                        <div className="truncate max-w-[300px] text-on-surface font-title-md" title={url.url}>
                          {url.url.replace('https://groww.in', '')}
                        </div>
                      </td>
                      <td className="p-4 text-on-surface-variant">{url.label}</td>
                      <td className="p-4">
                        <span className="bg-white/5 px-2 py-1 rounded text-xs text-on-surface-variant border border-white/10">
                          {url.source_type}
                        </span>
                      </td>
                      <td className="p-4">
                        <div className="flex items-center gap-2">
                          <span className={`w-2 h-2 rounded-full ${url.status === 'success' ? 'bg-primary' : url.status === 'failed' ? 'bg-error' : 'bg-tertiary animate-pulse'}`}></span>
                          <span className="text-sm capitalize text-on-surface-variant">{url.status}</span>
                        </div>
                      </td>
                      <td className="p-4 text-right">
                        <button 
                          onClick={() => handleDeleteUrl(url.id)}
                          className="p-2 text-on-surface-variant hover:text-error hover:bg-error/10 rounded transition-colors opacity-0 group-hover:opacity-100"
                          title="Delete Source"
                        >
                          <span className="material-symbols-outlined text-sm">delete</span>
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
