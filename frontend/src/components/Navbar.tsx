import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Navbar: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (!user) return null;

  return (
    <nav className="bg-white shadow-md">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center space-x-8">
            <Link to="/notifications" className="text-xl font-bold text-blue-600">
              Job Notifications
            </Link>
            <Link
              to="/notifications"
              className="text-gray-700 hover:text-blue-600 font-medium"
            >
              Notifications
            </Link>
            <Link to="/profile" className="text-gray-700 hover:text-blue-600 font-medium">
              Profile
            </Link>
            {user.role === 'admin' && (
              <Link to="/admin" className="text-gray-700 hover:text-blue-600 font-medium">
                Admin
              </Link>
            )}
          </div>

          <div className="flex items-center space-x-4">
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
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
