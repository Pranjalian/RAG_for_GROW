import { useState, useEffect } from 'react';
import axios from 'axios';

export default function NewsPage() {
  const [newsList, setNewsList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchNews = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/data/news');
        setNewsList(response.data.news || []);
        setError(null);
      } catch (err) {
        console.error("Error fetching news:", err);
        setError("Failed to load news data.");
      } finally {
        setLoading(false);
      }
    };
    fetchNews();
  }, []);

  return (
    <div className="flex-1 p-lg overflow-y-auto pb-[120px]">
      <div className="max-w-4xl mx-auto flex flex-col gap-lg mt-8">
        <div>
          <h1 className="font-headline-lg text-headline-lg font-bold text-primary">Market News</h1>
          <p className="text-on-surface-variant font-title-md mt-2">Latest updates affecting your portfolio</p>
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
        ) : newsList.length === 0 ? (
          <div className="text-center py-12 text-on-surface-variant">
            <span className="material-symbols-outlined text-6xl opacity-50 mb-4">newspaper</span>
            <p className="text-xl">No news right now.</p>
          </div>
        ) : (
          <div className="flex flex-col gap-4">
            {newsList.map(news => {
              // Calculate relative time (basic)
              const timeStr = news.published_at 
                ? new Date(news.published_at).toLocaleString() 
                : 'Recently';

              return (
                <div 
                  key={news.id} 
                  className={`glass-panel p-xl rounded-2xl flex gap-6 hover:bg-white/5 transition-colors cursor-pointer ${news.is_new ? 'border-l-4 border-tertiary' : ''}`}
                  onClick={() => news.link && window.open(news.link, '_blank')}
                >
                  <div className="flex-1">
                    <div className="flex gap-2 mb-3 items-center">
                      <span className="bg-tertiary-container/20 text-tertiary px-2 py-1 rounded text-xs border border-tertiary/20 uppercase tracking-wide">
                        Market Update
                      </span>
                      {news.is_new && (
                        <span className="bg-error text-white px-2 py-1 rounded text-xs font-bold uppercase tracking-wider">
                          NEW
                        </span>
                      )}
                      <span className="text-on-surface-variant text-sm ml-auto">{timeStr}</span>
                    </div>
                    <h3 className="font-headline-md text-headline-md text-on-surface mb-2">{news.title}</h3>
                    <p className="text-on-surface-variant line-clamp-2">{news.summary}</p>
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
