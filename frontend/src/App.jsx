import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import AppLayout from './components/layout/AppLayout';
import ChatPage from './pages/ChatPage';
import ComparePage from './pages/ComparePage';
import NFOPage from './pages/NFOPage';
import NewsPage from './pages/NewsPage';
import WatchlistPage from './pages/WatchlistPage';
import AdminDashboard from './pages/admin/AdminDashboard';
import AdminLogin from './pages/admin/AdminLogin';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/admin/login" element={<AdminLogin />} />
        
        <Route path="/" element={<AppLayout />}>
          <Route index element={<ChatPage />} />
          <Route path="compare" element={<ComparePage />} />
          <Route path="nfo" element={<NFOPage />} />
          <Route path="news" element={<NewsPage />} />
          <Route path="watchlist" element={<WatchlistPage />} />
          <Route path="admin/dashboard" element={<AdminDashboard />} />
        </Route>
        
        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
