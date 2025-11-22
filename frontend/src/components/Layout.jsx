import { useState } from 'react';
import { NavLink, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import {
  LayoutDashboard,
  MessageSquare,
  TestTube,
  QrCode,
  LogOut,
  Menu,
  X,
  User,
} from 'lucide-react';

export default function Layout({ children }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const isFullWidthPage = location.pathname === '/conversations' || location.pathname === '/';

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navItems = [
    { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
    { to: '/conversations', icon: MessageSquare, label: 'Conversas' },
    { to: '/trials', icon: TestTube, label: 'Testes Grátis' },
    { to: '/qrcode', icon: QrCode, label: 'QR Code' },
  ];

  return (
    <div className="min-h-screen" style={{ background: 'var(--bg-surface)' }}>
      {/* Sidebar Desktop */}
      <aside className="hidden md:fixed md:inset-y-0 md:flex md:w-64 md:flex-col">
        <div className="flex flex-col flex-grow overflow-y-auto" style={{ background: 'var(--primary-900)' }}>
          {/* Logo */}
          <div className="flex items-center flex-shrink-0 px-4 py-6" style={{ background: 'var(--primary-900)', borderBottom: '1px solid rgba(255, 255, 255, 0.1)' }}>
            <h1 className="text-2xl font-bold" style={{ color: 'var(--text-inverse)' }}>SPDrop Admin</h1>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-2 py-4 space-y-1">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-all ${
                    isActive ? 'nav-item-active' : 'nav-item-inactive'
                  }`
                }
                style={({ isActive }) => ({
                  background: isActive ? 'var(--primary-800)' : 'transparent',
                  color: isActive ? 'var(--text-inverse)' : 'var(--gray-400)',
                  borderLeft: isActive ? '4px solid var(--accent-500)' : '4px solid transparent',
                })}
              >
                <item.icon className="mr-3 h-5 w-5" />
                {item.label}
              </NavLink>
            ))}
          </nav>

          <style>{`
            .nav-item-inactive:hover {
              background: var(--primary-800) !important;
              color: var(--text-inverse) !important;
            }
          `}</style>

          {/* User Info */}
          <div className="flex-shrink-0 px-4 py-4" style={{ background: 'var(--primary-900)', borderTop: '1px solid rgba(255, 255, 255, 0.1)' }}>
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="h-10 w-10 rounded-full flex items-center justify-center" style={{ background: 'var(--accent-500)' }}>
                  <User className="h-6 w-6" style={{ color: 'var(--text-inverse)' }} />
                </div>
              </div>
              <div className="ml-3 flex-1">
                <p className="text-sm font-medium" style={{ color: 'var(--text-inverse)' }}>{user?.full_name || user?.username}</p>
                <p className="text-xs" style={{ color: 'var(--gray-400)' }}>{user?.role}</p>
              </div>
              <button
                onClick={handleLogout}
                className="ml-2 p-2 rounded-lg transition-colors user-logout-btn"
                title="Sair"
                style={{ color: 'var(--gray-400)' }}
              >
                <LogOut className="h-5 w-5" />
              </button>
            </div>
          </div>

          <style>{`
            .user-logout-btn:hover {
              background: var(--primary-800) !important;
              color: var(--text-inverse) !important;
            }
          `}</style>
        </div>
      </aside>

      {/* Mobile Sidebar */}
      {sidebarOpen && (
        <div className="fixed inset-0 z-40 md:hidden">
          <div className="fixed inset-0 bg-opacity-75" style={{ background: 'rgba(0, 0, 0, 0.5)' }} onClick={() => setSidebarOpen(false)} />
          <div className="fixed inset-y-0 left-0 flex flex-col w-64" style={{ background: 'var(--primary-900)' }}>
            {/* Logo */}
            <div className="flex items-center justify-between px-4 py-6" style={{ background: 'var(--primary-900)', borderBottom: '1px solid rgba(255, 255, 255, 0.1)' }}>
              <h1 className="text-2xl font-bold" style={{ color: 'var(--text-inverse)' }}>SPDrop Admin</h1>
              <button onClick={() => setSidebarOpen(false)} style={{ color: 'var(--text-inverse)' }}>
                <X className="h-6 w-6" />
              </button>
            </div>

            {/* Navigation */}
            <nav className="flex-1 px-2 py-4 space-y-1">
              {navItems.map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  onClick={() => setSidebarOpen(false)}
                  className={({ isActive }) =>
                    `flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-all ${
                      isActive ? 'nav-item-active' : 'nav-item-inactive'
                    }`
                  }
                  style={({ isActive }) => ({
                    background: isActive ? 'var(--primary-800)' : 'transparent',
                    color: isActive ? 'var(--text-inverse)' : 'var(--gray-400)',
                    borderLeft: isActive ? '4px solid var(--accent-500)' : '4px solid transparent',
                  })}
                >
                  <item.icon className="mr-3 h-5 w-5" />
                  {item.label}
                </NavLink>
              ))}
            </nav>

            {/* User Info */}
            <div className="px-4 py-4" style={{ background: 'var(--primary-900)', borderTop: '1px solid rgba(255, 255, 255, 0.1)' }}>
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="h-10 w-10 rounded-full flex items-center justify-center" style={{ background: 'var(--accent-500)' }}>
                    <User className="h-6 w-6" style={{ color: 'var(--text-inverse)' }} />
                  </div>
                </div>
                <div className="ml-3 flex-1">
                  <p className="text-sm font-medium" style={{ color: 'var(--text-inverse)' }}>{user?.full_name || user?.username}</p>
                  <p className="text-xs" style={{ color: 'var(--gray-400)' }}>{user?.role}</p>
                </div>
                <button
                  onClick={handleLogout}
                  className="ml-2 p-2 rounded-lg transition-colors user-logout-btn"
                  style={{ color: 'var(--gray-400)' }}
                >
                  <LogOut className="h-5 w-5" />
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="md:pl-64 flex flex-col flex-1">
        {/* Mobile Header */}
        <div className="sticky top-0 z-10 md:hidden" style={{ background: 'var(--bg-base)', boxShadow: 'var(--shadow-sm)', borderBottom: '1px solid var(--border-light)' }}>
          <div className="flex items-center justify-between px-4 py-3">
            <button
              onClick={() => setSidebarOpen(true)}
              className="mobile-menu-btn transition-colors"
              style={{ color: 'var(--text-secondary)' }}
            >
              <Menu className="h-6 w-6" />
            </button>
            <h1 className="text-xl font-bold" style={{ color: 'var(--text-primary)' }}>SPDrop Admin</h1>
            <div className="w-6" />
          </div>
          <style>{`
            .mobile-menu-btn:hover {
              color: var(--accent-500) !important;
            }
          `}</style>
        </div>

        {/* Page Content */}
        <main className="flex-1">
          <div className={isFullWidthPage ? "px-4 md:px-6" : "py-6"}>
            <div className={isFullWidthPage ? "h-full" : "max-w-7xl mx-auto px-4 sm:px-6 md:px-8"}>
              {children}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
