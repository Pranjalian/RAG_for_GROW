import { useState } from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import { useNotifications } from '../../hooks/useNotifications';

export default function AppLayout() {
  const { notifications, unreadCount, markAllRead } = useNotifications();
  const [showNotifications, setShowNotifications] = useState(false);
  return (
    <div className="bg-surface text-on-surface min-h-screen flex flex-col font-body-md text-body-md overflow-hidden">
      {/* Source-Only Banner */}
      <div className="fixed top-0 w-full z-[60] flex items-center justify-center h-8 bg-secondary-container dark:bg-secondary-container text-on-secondary-container dark:text-on-secondary-container font-label-mono text-label-mono uppercase tracking-widest cursor-default">
        🔒 Groww Source-Only Mode
      </div>

      {/* Main Header */}
      <header className="fixed top-8 w-full z-50 flex items-center justify-between px-lg h-16 border-b border-white/5 bg-surface/80 backdrop-blur-md">
        <div className="flex items-center gap-md">
          <h1 className="font-headline-md text-headline-md font-bold text-primary dark:text-primary">
            Groww Market Intelligence
          </h1>
          <div className="hidden md:flex items-center gap-2 px-3 py-1 rounded-full bg-primary-container/10 border border-primary-container/20">
            <span className="w-1.5 h-1.5 rounded-full bg-primary-container animate-pulse"></span>
            <span className="font-label-mono text-label-mono text-primary-container">All sources healthy</span>
          </div>
        </div>

        {/* Web Nav Cluster */}
        <nav className="hidden md:flex items-center gap-lg">
          <NavLink
            to="/"
            className={({ isActive }) =>
              `font-medium font-title-md text-title-md transition-all ${
                isActive
                  ? 'text-primary font-bold border-b-2 border-primary pb-1 opacity-80 scale-95'
                  : 'text-on-surface-variant hover:text-primary duration-200'
              }`
            }
          >
            Chat
          </NavLink>
          <NavLink
            to="/compare"
            className={({ isActive }) =>
              `font-medium font-title-md text-title-md transition-all ${
                isActive
                  ? 'text-primary font-bold border-b-2 border-primary pb-1 opacity-80 scale-95'
                  : 'text-on-surface-variant hover:text-primary duration-200'
              }`
            }
          >
            Compare
          </NavLink>
          <NavLink
            to="/nfo"
            className={({ isActive }) =>
              `font-medium font-title-md text-title-md transition-all ${
                isActive
                  ? 'text-primary font-bold border-b-2 border-primary pb-1 opacity-80 scale-95'
                  : 'text-on-surface-variant hover:text-primary duration-200'
              }`
            }
          >
            NFO
          </NavLink>
          <NavLink
            to="/news"
            className={({ isActive }) =>
              `font-medium font-title-md text-title-md transition-all ${
                isActive
                  ? 'text-primary font-bold border-b-2 border-primary pb-1 opacity-80 scale-95'
                  : 'text-on-surface-variant hover:text-primary duration-200'
              }`
            }
          >
            News
          </NavLink>
          <NavLink
            to="/watchlist"
            className={({ isActive }) =>
              `font-medium font-title-md text-title-md transition-all ${
                isActive
                  ? 'text-primary font-bold border-b-2 border-primary pb-1 opacity-80 scale-95'
                  : 'text-on-surface-variant hover:text-primary duration-200'
              }`
            }
          >
            Watchlist
          </NavLink>
        </nav>

        <div className="flex items-center gap-md relative">
          <button 
            className="p-2 text-on-surface-variant hover:text-primary transition-colors rounded-full hover:bg-white/5 relative"
            onClick={() => {
              setShowNotifications(!showNotifications);
              if (!showNotifications && unreadCount > 0) markAllRead();
            }}
          >
            <span className="material-symbols-outlined" style={{ fontVariationSettings: "'FILL' 1" }}>
              notifications
            </span>
            {unreadCount > 0 && (
              <span className="absolute top-1 right-1 w-2.5 h-2.5 bg-error rounded-full animate-pulse"></span>
            )}
          </button>
          
          {showNotifications && (
            <div className="absolute top-12 right-0 w-80 bg-surface-container border border-white/10 rounded-xl shadow-2xl p-4 z-50">
              <h3 className="font-headline-sm font-bold text-primary mb-3">Notifications</h3>
              {notifications.length === 0 ? (
                <p className="text-sm text-on-surface-variant text-center py-4">No notifications</p>
              ) : (
                <div className="flex flex-col gap-3 max-h-64 overflow-y-auto pr-1">
                  {notifications.map(notif => (
                    <div key={notif.id} className="p-3 bg-surface-container-highest rounded-lg">
                      <p className="font-title-sm text-on-surface">{notif.title}</p>
                      <p className="text-xs text-on-surface-variant mt-1 line-clamp-2">{notif.summary}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
          <img
            alt="User Profile"
            className="w-8 h-8 rounded-full border border-white/10 object-cover"
            src="https://lh3.googleusercontent.com/aida-public/AB6AXuCxapk40DR_N6C8d38fX032G_NAPMYI2940u2TLrz6Qw9uKNOveTcr57j6OdEqzDWr40QzpQyA6uVQhlFJxb1Mk2CEj8vFz_-3clNsES8PjylzE8-rkIUOuar6hYlvVvJnlUTxA4tAj20wyuOVbnWMrLhaFv36KxtUbiO1f-ux6t4Q9kaSQaOWoRfnePxtxiOusnohl2EyFmEk3nejg44IaEaDxrMCIAlvlQouiMs_ks6is_m7x2pa7gA"
          />
        </div>
      </header>

      <div className="flex flex-1 pt-24 h-screen">
        {/* SideNav */}
        <aside className="hidden lg:flex flex-col fixed left-0 top-24 h-[calc(100vh-96px)] w-[240px] py-md border-r border-white/5 bg-surface-container-low dark:bg-surface-container-low z-40">
          <div className="px-md mb-xl flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-surface-container-highest flex items-center justify-center border border-white/5">
              <span className="material-symbols-outlined text-primary">monitor_heart</span>
            </div>
            <div>
              <h2 className="font-title-md text-title-md text-on-surface">System Status</h2>
              <p className="font-caption text-caption text-primary">All Systems Live</p>
            </div>
          </div>

          <nav className="flex-1 flex flex-col gap-1">
            <NavLink
              to="/admin/dashboard"
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2 mx-2 rounded-lg transition-colors ${
                  isActive ? 'bg-white/10 text-primary' : 'text-on-surface-variant hover:bg-white/5'
                }`
              }
            >
              <span className="material-symbols-outlined">dashboard</span>
              <span>Admin Panel</span>
            </NavLink>
            <a className="flex items-center gap-3 px-3 py-2 text-on-surface-variant hover:bg-white/5 mx-2 rounded-lg transition-colors" href="#">
              <span className="material-symbols-outlined">show_chart</span>
              <span>Markets</span>
            </a>
            <a className="flex items-center gap-3 px-3 py-2 text-on-surface-variant hover:bg-white/5 mx-2 rounded-lg transition-colors" href="#">
              <span className="material-symbols-outlined">account_balance_wallet</span>
              <span>Portfolio</span>
            </a>
          </nav>

          <div className="mt-auto flex flex-col gap-1">
            <button className="mx-2 mb-4 bg-primary-container text-black font-title-md text-title-md py-2 rounded-lg hover:opacity-90 transition-opacity">
              Premium Insights
            </button>
            <a className="flex items-center gap-3 px-3 py-2 text-on-surface-variant hover:bg-white/5 mx-2 rounded-lg transition-colors" href="#">
              <span className="material-symbols-outlined">help</span>
              <span>Help</span>
            </a>
            <a className="flex items-center gap-3 px-3 py-2 text-on-surface-variant hover:bg-white/5 mx-2 rounded-lg transition-colors" href="#">
              <span className="material-symbols-outlined">logout</span>
              <span>Sign Out</span>
            </a>
          </div>
        </aside>

        {/* Main Content Area */}
        <main className="flex-1 flex flex-col lg:ml-[240px] relative h-full">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
