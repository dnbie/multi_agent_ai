import React, { useState } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { motion } from 'framer-motion';
import {
  Bot,
  LayoutDashboard,
  Mail,
  FileText,
  Plane,
  Bus,
  Train,
  FolderOpen,
  Globe,
  Cloud,
  Newspaper,
  Bell,
  AlertTriangle,
  History,
  Settings,
  LogOut,
  Menu,
  X,
  Sparkles
} from 'lucide-react';

const NAVIGATION = [
  {
    section: 'Main',
    items: [
      { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
      { name: 'Auto Mode', path: '/agents/auto', icon: Sparkles },
    ]
  },
  {
    section: 'Agents',
    items: [
      { name: 'Email', path: '/agents/email', icon: Mail },
      { name: 'Reports', path: '/agents/report', icon: FileText },
      { name: 'Flight', path: '/agents/flight', icon: Plane },
      { name: 'Bus', path: '/agents/bus', icon: Bus },
      { name: 'Train', path: '/agents/train', icon: Train },
      { name: 'Files', path: '/agents/file_organizer', icon: FolderOpen },
      { name: 'Browser', path: '/agents/browser', icon: Globe },
      { name: 'Weather', path: '/agents/weather', icon: Cloud },
      { name: 'News', path: '/agents/news', icon: Newspaper },
      { name: 'Reminders', path: '/agents/reminder', icon: Bell },
      { name: 'Emergency', path: '/agents/emergency', icon: AlertTriangle },
    ]
  },
  {
    section: 'Account',
    items: [
      { name: 'History', path: '/history', icon: History },
      { name: 'Settings', path: '/settings', icon: Settings },
    ]
  }
];

const Layout = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const handleNavClick = (path) => {
    navigate(path);
    setSidebarOpen(false);
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const getUserInitials = () => {
    if (!user) return '?';
    if (user.full_name) {
      return user.full_name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
    }
    return user.username?.slice(0, 2).toUpperCase() || '?';
  };

  return (
    <div className="layout">
      {/* Mobile Menu Button */}
      <button
        className="mobile-menu-btn"
        onClick={() => setSidebarOpen(!sidebarOpen)}
        style={{
          position: 'fixed',
          top: '1rem',
          left: '1rem',
          zIndex: 200,
          background: 'var(--bg-secondary)',
          border: '1px solid var(--border-color)',
          borderRadius: 'var(--radius-md)',
          padding: '0.75rem',
          color: 'var(--text-primary)',
          cursor: 'pointer',
          display: 'none'
        }}
      >
        {sidebarOpen ? <X size={24} /> : <Menu size={24} />}
      </button>

      {/* Sidebar */}
      <motion.aside 
        className={`sidebar ${sidebarOpen ? 'open' : ''}`}
        initial={{ x: -280 }}
        animate={{ x: 0 }}
        transition={{ duration: 0.3 }}
      >
        {/* Logo */}
        <div className="sidebar-header">
          <div className="sidebar-logo">
            <div className="sidebar-logo-icon">
              <Bot size={20} />
            </div>
            <span>Agent X</span>
          </div>
        </div>

        {/* Navigation */}
        <nav className="sidebar-nav">
          {NAVIGATION.map((section) => (
            <div key={section.section} className="nav-section">
              <div className="nav-section-title">{section.section}</div>
              {section.items.map((item) => {
                const Icon = item.icon;
                const isActive = location.pathname === item.path;
                
                return (
                  <motion.div
                    key={item.path}
                    className={`nav-item ${isActive ? 'active' : ''}`}
                    onClick={() => handleNavClick(item.path)}
                    whileHover={{ x: 4 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <span className="nav-item-icon">
                      <Icon size={18} />
                    </span>
                    <span>{item.name}</span>
                  </motion.div>
                );
              })}
            </div>
          ))}
        </nav>

        {/* User Profile */}
        <div className="sidebar-footer">
          <div className="user-card">
            <div className="user-avatar">
              {user?.picture ? (
                <img 
                  src={user.picture} 
                  alt={user.username}
                  style={{ width: '100%', height: '100%', borderRadius: '50%', objectFit: 'cover' }}
                />
              ) : (
                getUserInitials()
              )}
            </div>
            <div className="user-info">
              <div className="user-name">{user?.full_name || user?.username}</div>
              <div className="user-email">{user?.email || 'No email'}</div>
            </div>
            <button 
              className="logout-btn" 
              onClick={handleLogout}
              title="Logout"
            >
              <LogOut size={18} />
            </button>
          </div>
        </div>
      </motion.aside>

      {/* Overlay for mobile */}
      {sidebarOpen && (
        <div 
          className="sidebar-overlay"
          onClick={() => setSidebarOpen(false)}
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(0,0,0,0.5)',
            zIndex: 99,
            display: 'none'
          }}
        />
      )}

      {/* Main Content */}
      <main className="main-content">
        <div className="content-wrapper">
          <Outlet />
        </div>
      </main>

      <style>{`
        @media (max-width: 1024px) {
          .mobile-menu-btn {
            display: block !important;
          }
          .sidebar-overlay {
            display: block !important;
          }
          .sidebar {
            transform: translateX(-100%);
          }
          .sidebar.open {
            transform: translateX(0);
          }
          .main-content {
            margin-left: 0 !important;
          }
        }
      `}</style>
    </div>
  );
};

export default Layout;
