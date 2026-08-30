import { useState, useEffect } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../config';

export default function WatchlistPage() {
  const [watchlist, setWatchlist] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchWatchlist = async () => {
      try {
        const sessionId = localStorage.getItem('groww_session_id') || crypto.randomUUID();
        if (!localStorage.getItem('groww_session_id')) {
          localStorage.setItem('groww_session_id', sessionId);
        }
        
        const response = await axios.get(`${API_BASE_URL}/api/data/watchlist?session_id=${sessionId}`);
        setWatchlist(response.data.watchlist || []);
        setError(null);
      } catch (err) {
        console.error("Error fetching watchlist:", err);
        setError("Failed to load watchlist.");
      } finally {
        setLoading(false);
      }
    };

    fetchWatchlist();
  }, []);

  const handleRemove = async (id) => {
    try {
      const sessionId = localStorage.getItem('groww_session_id');
      await axios.delete(`${API_BASE_URL}/api/data/watchlist/${id}?session_id=${sessionId}`);
      setWatchlist(prev => prev.filter(item => item.id !== id));
    } catch (err) {
      console.error("Error removing item:", err);
    }
  };

  return (
    <div className="flex-1 p-lg overflow-y-auto pb-[120px]">
      <div className="max-w-4xl mx-auto flex flex-col gap-lg mt-8">
        <div className="flex justify-between items-center mb-4">
          <div>
            <h1 className="font-headline-lg text-headline-lg font-bold text-primary">Your Watchlist</h1>
            <p className="text-on-surface-variant font-title-md mt-2">Tracked funds and stocks</p>
          </div>
          <button className="bg-primary/20 text-primary border border-primary/30 px-4 py-2 rounded-lg font-title-md hover:bg-primary hover:text-black transition-colors flex items-center gap-2">
            <span className="material-symbols-outlined">add</span>
            Add Item
          </button>
        </div>

        {loading ? (
          <div className="flex justify-center py-12">
            <div className="animate-spin text-primary">
              <span className="material-symbols-outlined text-4xl">autorenew</span>
            </div>
          </div>
        ) : error ? (
          <div className="bg-error/10 text-error p-4 rounded-lg border border-error/20">
            {error}
          </div>
        ) : watchlist.length === 0 ? (
          <div className="text-center py-12 text-on-surface-variant">
            <span className="material-symbols-outlined text-6xl opacity-50 mb-4">visibility_off</span>
            <p className="text-xl">Your watchlist is empty.</p>
            <p className="mt-2 text-sm opacity-70">You can add funds by clicking the Add Item button above.</p>
          </div>
        ) : (
          <div className="flex flex-col gap-4">
            {watchlist.map(item => {
              // Extract nav or latest price if available
              let price = "N/A";
              let change = "N/A";
              let isUp = true;
              
              if (item.data) {
                 price = item.data.nav || item.data.price || "N/A";
                 // basic heuristic
                 if (item.data['1Y_Return']) change = item.data['1Y_Return'];
                 else if (item.data['3Y_Return']) change = item.data['3Y_Return'];
                 
                 isUp = !change.startsWith('-');
              }

              return (
                <div key={item.id} className="glass-panel p-md rounded-xl flex items-center justify-between hover:bg-white/5 transition-colors group">
                  <div className="flex items-center gap-4">
                    <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${isUp ? 'bg-primary-container/20 text-primary' : 'bg-error-container/20 text-error'}`}>
                      <span className="material-symbols-outlined">{isUp ? 'trending_up' : 'trending_down'}</span>
                    </div>
                    <div>
                      <h3 className="font-title-md text-title-md text-on-surface">{item.label || "Unknown Item"}</h3>
                      <p className="text-sm text-on-surface-variant capitalize">{item.item_type.replace('_', ' ')}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-6">
                    <div className="text-right">
                      <p className="font-headline-md text-headline-md text-on-surface">₹{price}</p>
                      <div className={`flex items-center gap-1 justify-end ${isUp ? 'text-primary' : 'text-error'}`}>
                        <span className="material-symbols-outlined text-sm">{isUp ? 'arrow_upward' : 'arrow_downward'}</span>
                        <span className="font-title-md text-title-md">{change}</span>
                      </div>
                    </div>
                    <button 
                      onClick={() => handleRemove(item.id)}
                      className="opacity-0 group-hover:opacity-100 text-on-surface-variant hover:text-error transition-all"
                      title="Remove from watchlist"
                    >
                      <span className="material-symbols-outlined">delete</span>
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
