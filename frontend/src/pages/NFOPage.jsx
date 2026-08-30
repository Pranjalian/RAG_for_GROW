import { useState, useEffect } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../config';

export default function NFOPage() {
  const [nfos, setNfos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchNFOs = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/api/data/nfo`);
        setNfos(response.data.nfos || []);
        setError(null);
      } catch (err) {
        console.error("Error fetching NFOs:", err);
        setError("Failed to load NFO data.");
      } finally {
        setLoading(false);
      }
    };
    fetchNFOs();
  }, []);

  return (
    <div className="flex-1 p-lg overflow-y-auto pb-[120px]">
      <div className="max-w-6xl mx-auto flex flex-col gap-xl mt-8">
        <div>
          <h1 className="font-headline-lg text-headline-lg font-bold text-primary">New Fund Offers (NFOs)</h1>
          <p className="text-on-surface-variant font-title-md mt-2">Discover and invest in upcoming mutual funds</p>
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
        ) : nfos.length === 0 ? (
          <div className="text-center py-12 text-on-surface-variant">
            <span className="material-symbols-outlined text-6xl opacity-50 mb-4">inbox</span>
            <p className="text-xl">No active NFOs right now.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {nfos.map(nfo => {
              const isOpen = nfo.status && nfo.status.toLowerCase().includes('open');
              const statusClass = isOpen 
                ? 'bg-primary-container text-black' 
                : 'bg-surface-container-highest text-on-surface-variant';

              return (
                <div key={nfo.id} className={`glass-panel p-xl rounded-2xl flex flex-col gap-4 ${nfo.is_new ? 'border-l-4 border-primary' : ''}`}>
                  <div className="flex justify-between items-start">
                    <div>
                      <div className="flex items-center gap-2 mb-2">
                        <span className={`${statusClass} px-2 py-1 rounded text-xs font-bold uppercase tracking-wider inline-block`}>
                          {nfo.status || 'Upcoming'}
                        </span>
                        {nfo.is_new && (
                          <span className="bg-error text-white px-2 py-1 rounded text-xs font-bold uppercase tracking-wider inline-block">
                            NEW
                          </span>
                        )}
                      </div>
                      <h3 className="font-headline-md text-headline-md text-on-surface">{nfo.fund_name}</h3>
                      <p className="text-on-surface-variant mt-1">{nfo.amc_name}</p>
                    </div>
                    <div className="text-right">
                      {nfo.close_date ? (
                        <>
                          <p className="text-sm text-on-surface-variant">Closes</p>
                          <p className="font-title-md text-title-md text-primary">{new Date(nfo.close_date).toLocaleDateString()}</p>
                        </>
                      ) : (
                        <>
                          <p className="text-sm text-on-surface-variant">Opens</p>
                          <p className="font-title-md text-title-md text-on-surface">{nfo.open_date ? new Date(nfo.open_date).toLocaleDateString() : 'TBA'}</p>
                        </>
                      )}
                    </div>
                  </div>
                  <button className={`w-full mt-2 py-3 rounded-lg font-title-md transition-colors ${isOpen ? 'bg-primary/20 text-primary border border-primary/30 hover:bg-primary hover:text-black' : 'bg-white/5 text-on-surface border border-white/10 hover:bg-white/10'}`}>
                    {isOpen ? 'View Details' : 'Set Reminder'}
                  </button>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
