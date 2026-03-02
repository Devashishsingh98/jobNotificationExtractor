import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Navbar: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (!user) return null;

  const isActive = (path: string) => location.pathname === path;

  const linkClass = (path: string) =>
    `font-medium transition ${
      isActive(path)
        ? 'text-blue-600 border-b-2 border-blue-600 pb-1'
        : 'text-gray-700 hover:text-blue-600'
    }`;

  const mobileLinkClass = (path: string) =>
    `block px-3 py-2 rounded-lg font-medium transition ${
      isActive(path)
        ? 'bg-blue-50 text-blue-600'
        : 'text-gray-700 hover:bg-gray-50'
    }`;

  return (
    <nav className="bg-white shadow-md relative z-50">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          {/* Logo + Desktop Nav */}
          <div className="flex items-center space-x-8">
            <Link to="/notifications" className="text-xl font-bold text-blue-600">
              Job Notifications
            </Link>
            <div className="hidden md:flex items-center space-x-6">
              <Link to="/notifications" className={linkClass('/notifications')}>
                Notifications
              </Link>
              <Link to="/profile" className={linkClass('/profile')}>
                Profile
              </Link>
              {user.role === 'admin' && (
                <Link to="/admin" className={linkClass('/admin')}>
                  Admin
                </Link>
              )}
            </div>
          </div>

          {/* Desktop Right */}
          <div className="hidden md:flex items-center space-x-4">
            <span className="text-sm text-gray-600">{user.email}</span>
            {user.is_premium && (
              <span className="bg-yellow-100 text-yellow-800 text-xs px-2 py-1 rounded-full">
                Premium
              </span>
            )}
            <button
              onClick={handleLogout}
              className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 text-sm font-medium"
            >
              Logout
            </button>
          </div>

          {/* Mobile Hamburger */}
          <button
            type="button"
            onClick={() => setMobileOpen(!mobileOpen)}
            className="md:hidden p-2 rounded-lg hover:bg-gray-100"
            aria-label="Toggle menu"
          >
            <svg className="w-6 h-6 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              {mobileOpen ? (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              ) : (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              )}
            </svg>
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      {mobileOpen && (
        <div className="md:hidden border-t bg-white px-4 py-3 space-y-1">
          <Link
            to="/notifications"
            className={mobileLinkClass('/notifications')}
            onClick={() => setMobileOpen(false)}
          >
            Notifications
          </Link>
          <Link
            to="/profile"
            className={mobileLinkClass('/profile')}
            onClick={() => setMobileOpen(false)}
          >
            Profile
          </Link>
          {user.role === 'admin' && (
            <Link
              to="/admin"
              className={mobileLinkClass('/admin')}
              onClick={() => setMobileOpen(false)}
            >
              Admin
            </Link>
          )}
          <div className="border-t pt-3 mt-3">
            <div className="flex items-center justify-between px-3">
              <div>
                <div className="text-sm text-gray-600">{user.email}</div>
                {user.is_premium && (
                  <span className="bg-yellow-100 text-yellow-800 text-xs px-2 py-1 rounded-full">
                    Premium
                  </span>
                )}
              </div>
              <button
                type="button"
                onClick={handleLogout}
                className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 text-sm font-medium"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
