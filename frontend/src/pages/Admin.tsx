import React, { useState, useEffect } from 'react';
import { adminAPI } from '../api/services';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

interface Channel {
  id: number;
  channel_username: string;
  channel_name: string;
  is_active: boolean;
  last_scraped_id: number;
}

interface Stats {
  total_users: number;
  premium_users: number;
  total_notifications: number;
  total_deliveries: number;
  active_channels: number;
}

const Admin: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [channels, setChannels] = useState<Channel[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [newChannel, setNewChannel] = useState({ username: '', name: '' });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user?.role !== 'admin') {
      navigate('/notifications');
      return;
    }
    fetchData();
  }, [user]);

  const fetchData = async () => {
    try {
      const [channelsRes, statsRes] = await Promise.all([
        adminAPI.listChannels(),
        adminAPI.getStats(),
      ]);
      setChannels(channelsRes.data);
      setStats(statsRes.data);
    } catch (err) {
      console.error('Failed to fetch admin data', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddChannel = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await adminAPI.addChannel({
        channel_username: newChannel.username,
        channel_name: newChannel.name,
      });
      setNewChannel({ username: '', name: '' });
      fetchData();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to add channel');
    }
  };

  const handleToggle = async (id: number) => {
    try {
      await adminAPI.toggleChannel(id);
      fetchData();
    } catch (err) {
      alert('Failed to toggle channel');
    }
  };

  const handleRemove = async (id: number) => {
    if (!confirm('Remove this channel?')) return;
    try {
      await adminAPI.removeChannel(id);
      fetchData();
    } catch (err) {
      alert('Failed to remove channel');
    }
  };

  if (loading) return <div className="p-8">Loading...</div>;

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Admin Dashboard</h1>

        {/* Stats */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-8">
            <div className="bg-white p-6 rounded-lg shadow">
              <div className="text-3xl font-bold text-blue-600">{stats.total_users}</div>
              <div className="text-sm text-gray-600 mt-1">Total Users</div>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <div className="text-3xl font-bold text-yellow-600">{stats.premium_users}</div>
              <div className="text-sm text-gray-600 mt-1">Premium Users</div>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <div className="text-3xl font-bold text-green-600">{stats.total_notifications}</div>
              <div className="text-sm text-gray-600 mt-1">Notifications</div>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <div className="text-3xl font-bold text-purple-600">{stats.total_deliveries}</div>
              <div className="text-sm text-gray-600 mt-1">Deliveries</div>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <div className="text-3xl font-bold text-indigo-600">{stats.active_channels}</div>
              <div className="text-sm text-gray-600 mt-1">Active Channels</div>
            </div>
          </div>
        )}

        {/* Add Channel */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Add Telegram Channel</h2>
          <form onSubmit={handleAddChannel} className="flex gap-4">
            <input
              type="text"
              placeholder="Channel Username (e.g., @examnotifications)"
              value={newChannel.username}
              onChange={(e) => setNewChannel({ ...newChannel, username: e.target.value })}
              required
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
            <input
              type="text"
              placeholder="Display Name (optional)"
              value={newChannel.name}
              onChange={(e) => setNewChannel({ ...newChannel, name: e.target.value })}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
            <button
              type="submit"
              className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
            >
              Add
            </button>
          </form>
        </div>

        {/* Channels List */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <h2 className="text-xl font-bold text-gray-900 p-6 border-b">Monitored Channels</h2>
          <div className="divide-y">
            {channels.map((channel) => (
              <div key={channel.id} className="p-6 flex justify-between items-center">
                <div>
                  <div className="font-medium text-gray-900">@{channel.channel_username}</div>
                  <div className="text-sm text-gray-500">{channel.channel_name}</div>
                  <div className="text-xs text-gray-400 mt-1">
                    Last scraped ID: {channel.last_scraped_id}
                  </div>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleToggle(channel.id)}
                    className={`px-4 py-2 rounded-lg ${
                      channel.is_active
                        ? 'bg-green-100 text-green-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    {channel.is_active ? 'Active' : 'Inactive'}
                  </button>
                  <button
                    onClick={() => handleRemove(channel.id)}
                    className="px-4 py-2 bg-red-100 text-red-800 rounded-lg hover:bg-red-200"
                  >
                    Remove
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Admin;
