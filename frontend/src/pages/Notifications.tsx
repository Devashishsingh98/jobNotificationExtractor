import React, { useState, useEffect } from 'react';
import { notificationAPI } from '../api/services';
import type { Notification } from '../api/services';
import { useAuth } from '../context/AuthContext';

const Notifications: React.FC = () => {
  const { user } = useAuth();
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [examType, setExamType] = useState('');
  const [search, setSearch] = useState('');
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchNotifications();
  }, [page, examType]);

  const fetchNotifications = async () => {
    setLoading(true);
    try {
      const response = await notificationAPI.list({
        page,
        per_page: 20,
        exam_type: examType || undefined,
        search: search || undefined,
      });
      setNotifications(response.data.notifications);
      setTotal(response.data.total);
    } catch (err) {
      console.error('Failed to fetch notifications', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchNotifications();
  };

  const toggleSelection = (id: number) => {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((i) => i !== id) : [...prev, id]
    );
  };

  const handleSubmitSelections = async () => {
    if (selectedIds.length === 0) return;
    setSubmitting(true);
    try {
      await notificationAPI.select(selectedIds);
      alert(`${selectedIds.length} notifications will be sent to your Telegram`);
      setSelectedIds([]);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to submit selections');
    } finally {
      setSubmitting(false);
    }
  };

  const getEligibilityBadge = (status?: string) => {
    if (!status) return null;
    const colors = {
      eligible: 'bg-green-100 text-green-800',
      partial: 'bg-yellow-100 text-yellow-800',
      not_eligible: 'bg-red-100 text-red-800',
    };
    return (
      <span className={`text-xs px-2 py-1 rounded-full ${colors[status as keyof typeof colors]}`}>
        {status.replace('_', ' ')}
      </span>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Job Notifications</h1>
          <p className="text-gray-600 mt-2">Browse and select notifications</p>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow p-4 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <form onSubmit={handleSearch} className="md:col-span-2">
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search notifications..."
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </form>

            <select
              value={examType}
              onChange={(e) => {
                setExamType(e.target.value);
                setPage(1);
              }}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Exam Types</option>
              <option value="Central">Central</option>
              <option value="State">State</option>
              <option value="Banking">Banking</option>
              <option value="Railway">Railway</option>
              <option value="Defence">Defence</option>
              <option value="PSU">PSU</option>
              <option value="Other">Other</option>
            </select>
          </div>
        </div>

        {/* Selection Actions (Free Users) */}
        {user && !user.is_premium && selectedIds.length > 0 && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <div className="flex justify-between items-center">
              <span className="text-blue-800 font-medium">
                {selectedIds.length} notification(s) selected
              </span>
              <button
                onClick={handleSubmitSelections}
                disabled={submitting}
                className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                {submitting ? 'Submitting...' : 'Send to Telegram'}
              </button>
            </div>
          </div>
        )}

        {/* Notifications List */}
        {loading ? (
          <div className="text-center py-12">Loading notifications...</div>
        ) : notifications.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-12 text-center text-gray-500">
            No notifications found
          </div>
        ) : (
          <div className="space-y-4">
            {notifications.map((notif) => (
              <div key={notif.id} className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-start gap-3">
                      {user && !user.is_premium && (
                        <input
                          type="checkbox"
                          checked={selectedIds.includes(notif.id)}
                          onChange={() => toggleSelection(notif.id)}
                          className="mt-1 w-4 h-4 text-blue-600"
                        />
                      )}
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold text-gray-900">{notif.title}</h3>

                        <div className="flex flex-wrap gap-2 mt-2">
                          {notif.organization && (
                            <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">
                              {notif.organization}
                            </span>
                          )}
                          {notif.exam_type && (
                            <span className="bg-purple-100 text-purple-800 text-xs px-2 py-1 rounded-full">
                              {notif.exam_type}
                            </span>
                          )}
                          {getEligibilityBadge(notif.eligibility_status)}
                        </div>

                        <div className="mt-3 text-sm text-gray-600 space-y-1">
                          {notif.last_date && (
                            <div>
                              <strong>Last Date:</strong> {new Date(notif.last_date).toLocaleDateString()}
                            </div>
                          )}
                          {notif.min_age && notif.max_age && (
                            <div>
                              <strong>Age:</strong> {notif.min_age} - {notif.max_age} years
                            </div>
                          )}
                          {notif.education_required && (
                            <div>
                              <strong>Education:</strong> {notif.education_required}
                            </div>
                          )}
                          {notif.total_vacancies && (
                            <div>
                              <strong>Vacancies:</strong> {notif.total_vacancies}
                            </div>
                          )}
                        </div>

                        {notif.eligibility_reasons && notif.eligibility_reasons.length > 0 && (
                          <div className="mt-3 text-sm">
                            <strong className="text-gray-700">Eligibility Details:</strong>
                            <ul className="list-disc list-inside text-gray-600 mt-1">
                              {notif.eligibility_reasons.map((reason, idx) => (
                                <li key={idx}>{reason}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Pagination */}
        {total > 20 && (
          <div className="flex justify-center gap-2 mt-6">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
              className="px-4 py-2 bg-white border rounded-lg disabled:opacity-50"
            >
              Previous
            </button>
            <span className="px-4 py-2">
              Page {page} of {Math.ceil(total / 20)}
            </span>
            <button
              onClick={() => setPage((p) => p + 1)}
              disabled={page >= Math.ceil(total / 20)}
              className="px-4 py-2 bg-white border rounded-lg disabled:opacity-50"
            >
              Next
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default Notifications;
