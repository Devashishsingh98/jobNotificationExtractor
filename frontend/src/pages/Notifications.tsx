import React, { useState, useEffect, useCallback, useRef } from 'react';
import { notificationAPI } from '../api/services';
import type { Notification } from '../api/services';
import { useAuth } from '../context/AuthContext';

const Notifications: React.FC = () => {
  const { user } = useAuth();
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [examType, setExamType] = useState('');
  const [search, setSearch] = useState('');
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [submitting, setSubmitting] = useState(false);
  const [selectedNotif, setSelectedNotif] = useState<Notification | null>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout>>();

  useEffect(() => {
    fetchNotifications();
  }, [page, examType]);

  // Debounced search
  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      setPage(1);
      fetchNotifications();
    }, 400);
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, [search]);

  const fetchNotifications = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await notificationAPI.list({
        page,
        per_page: 20,
        exam_type: examType || undefined,
        search: search || undefined,
      });
      setNotifications(response.data.notifications);
      setTotal(response.data.total);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load notifications. Please try again.');
      setNotifications([]);
    } finally {
      setLoading(false);
    }
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
    const config: Record<string, { bg: string; label: string }> = {
      eligible: { bg: 'bg-green-100 text-green-800', label: 'Eligible' },
      partial: { bg: 'bg-yellow-100 text-yellow-800', label: 'Partially Eligible' },
      not_eligible: { bg: 'bg-red-100 text-red-800', label: 'Not Eligible' },
    };
    const c = config[status];
    if (!c) return null;
    return <span className={`text-xs px-2 py-1 rounded-full ${c.bg}`}>{c.label}</span>;
  };

  const openDetail = useCallback(async (notif: Notification) => {
    try {
      const response = await notificationAPI.getById(notif.id);
      setSelectedNotif(response.data);
    } catch {
      setSelectedNotif(notif);
    }
  }, []);

  // Loading skeleton
  const LoadingSkeleton = () => (
    <div className="space-y-4">
      {[...Array(5)].map((_, i) => (
        <div key={i} className="bg-white rounded-lg shadow p-6 animate-pulse">
          <div className="h-5 bg-gray-200 rounded w-3/4 mb-3"></div>
          <div className="flex gap-2 mb-3">
            <div className="h-5 bg-gray-200 rounded-full w-16"></div>
            <div className="h-5 bg-gray-200 rounded-full w-20"></div>
          </div>
          <div className="space-y-2">
            <div className="h-4 bg-gray-200 rounded w-1/3"></div>
            <div className="h-4 bg-gray-200 rounded w-1/4"></div>
          </div>
        </div>
      ))}
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Job Notifications</h1>
          <p className="text-gray-600 mt-2">
            {total > 0 ? `${total} notification${total > 1 ? 's' : ''} found` : 'Browse and select notifications'}
          </p>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow p-4 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="md:col-span-2">
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search notifications... (auto-searches as you type)"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <select
              value={examType}
              onChange={(e) => {
                setExamType(e.target.value);
                setPage(1);
              }}
              aria-label="Filter by exam type"
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

        {/* Error Banner */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <div className="flex items-center justify-between">
              <span className="text-red-800">{error}</span>
              <button
                type="button"
                onClick={fetchNotifications}
                className="text-red-600 hover:text-red-800 font-medium text-sm"
              >
                Retry
              </button>
            </div>
          </div>
        )}

        {/* Selection Actions (Free Users) */}
        {user && !user.is_premium && selectedIds.length > 0 && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <div className="flex justify-between items-center">
              <span className="text-blue-800 font-medium">
                {selectedIds.length} notification(s) selected
              </span>
              <button
                type="button"
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
          <LoadingSkeleton />
        ) : notifications.length === 0 && !error ? (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <div className="text-gray-400 text-5xl mb-4">&#128270;</div>
            <h3 className="text-lg font-medium text-gray-700 mb-2">No notifications found</h3>
            <p className="text-gray-500">
              {search || examType
                ? 'Try adjusting your filters or search terms.'
                : 'New notifications will appear here once channels are configured.'}
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {notifications.map((notif) => (
              <div
                key={notif.id}
                className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition cursor-pointer"
                onClick={() => openDetail(notif)}
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-start gap-3">
                      {user && !user.is_premium && (
                        <input
                          type="checkbox"
                          checked={selectedIds.includes(notif.id)}
                          onChange={(e) => {
                            e.stopPropagation();
                            toggleSelection(notif.id);
                          }}
                          onClick={(e) => e.stopPropagation()}
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

                        <div className="mt-3 text-sm text-gray-600 grid grid-cols-2 md:grid-cols-4 gap-2">
                          {notif.last_date && (
                            <div>
                              <span className="font-medium">Last Date:</span>{' '}
                              {new Date(notif.last_date).toLocaleDateString('en-IN')}
                            </div>
                          )}
                          {notif.min_age && notif.max_age && (
                            <div>
                              <span className="font-medium">Age:</span> {notif.min_age}-{notif.max_age} yrs
                            </div>
                          )}
                          {notif.education_required && (
                            <div>
                              <span className="font-medium">Education:</span> {notif.education_required}
                            </div>
                          )}
                          {notif.total_vacancies && (
                            <div>
                              <span className="font-medium">Vacancies:</span> {notif.total_vacancies.toLocaleString()}
                            </div>
                          )}
                        </div>

                        {notif.eligibility_reasons && notif.eligibility_reasons.length > 0 && (
                          <div className="mt-3 text-sm">
                            <span className="font-medium text-gray-700">Eligibility:</span>
                            <ul className="list-disc list-inside text-gray-600 mt-1">
                              {notif.eligibility_reasons.slice(0, 2).map((reason, idx) => (
                                <li key={idx}>{reason}</li>
                              ))}
                              {notif.eligibility_reasons.length > 2 && (
                                <li className="text-blue-600">+{notif.eligibility_reasons.length - 2} more...</li>
                              )}
                            </ul>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                  <span className="text-gray-400 ml-2 text-sm hidden md:block">Click for details</span>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Pagination */}
        {total > 20 && (
          <div className="flex justify-center items-center gap-2 mt-6">
            <button
              type="button"
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
              className="px-4 py-2 bg-white border rounded-lg disabled:opacity-50 hover:bg-gray-50"
            >
              Previous
            </button>
            <span className="px-4 py-2 text-sm text-gray-600">
              Page {page} of {Math.ceil(total / 20)}
            </span>
            <button
              type="button"
              onClick={() => setPage((p) => p + 1)}
              disabled={page >= Math.ceil(total / 20)}
              className="px-4 py-2 bg-white border rounded-lg disabled:opacity-50 hover:bg-gray-50"
            >
              Next
            </button>
          </div>
        )}
      </div>

      {/* Detail Modal */}
      {selectedNotif && (
        <div
          className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4"
          onClick={() => setSelectedNotif(null)}
        >
          <div
            className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="p-6">
              {/* Header */}
              <div className="flex justify-between items-start mb-4">
                <h2 className="text-2xl font-bold text-gray-900 pr-4">{selectedNotif.title}</h2>
                <button
                  type="button"
                  onClick={() => setSelectedNotif(null)}
                  className="text-gray-400 hover:text-gray-600 text-2xl leading-none"
                  aria-label="Close modal"
                >
                  &times;
                </button>
              </div>

              {/* Badges */}
              <div className="flex flex-wrap gap-2 mb-6">
                {selectedNotif.organization && (
                  <span className="bg-blue-100 text-blue-800 text-sm px-3 py-1 rounded-full">
                    {selectedNotif.organization}
                  </span>
                )}
                {selectedNotif.exam_type && (
                  <span className="bg-purple-100 text-purple-800 text-sm px-3 py-1 rounded-full">
                    {selectedNotif.exam_type}
                  </span>
                )}
                {getEligibilityBadge(selectedNotif.eligibility_status)}
              </div>

              {/* Details Grid */}
              <div className="grid grid-cols-2 gap-4 mb-6">
                {selectedNotif.last_date && (
                  <div className="bg-gray-50 rounded-lg p-3">
                    <div className="text-xs text-gray-500 uppercase">Last Date</div>
                    <div className="font-semibold text-gray-900">
                      {new Date(selectedNotif.last_date).toLocaleDateString('en-IN', {
                        year: 'numeric', month: 'long', day: 'numeric',
                      })}
                    </div>
                  </div>
                )}
                {selectedNotif.total_vacancies && (
                  <div className="bg-gray-50 rounded-lg p-3">
                    <div className="text-xs text-gray-500 uppercase">Total Vacancies</div>
                    <div className="font-semibold text-gray-900">
                      {selectedNotif.total_vacancies.toLocaleString()}
                    </div>
                  </div>
                )}
                {selectedNotif.min_age && selectedNotif.max_age && (
                  <div className="bg-gray-50 rounded-lg p-3">
                    <div className="text-xs text-gray-500 uppercase">Age Limit</div>
                    <div className="font-semibold text-gray-900">
                      {selectedNotif.min_age} - {selectedNotif.max_age} years
                    </div>
                  </div>
                )}
                {selectedNotif.education_required && (
                  <div className="bg-gray-50 rounded-lg p-3">
                    <div className="text-xs text-gray-500 uppercase">Education</div>
                    <div className="font-semibold text-gray-900">{selectedNotif.education_required}</div>
                  </div>
                )}
              </div>

              {/* Category-wise Vacancies */}
              {selectedNotif.vacancy_by_category && Object.keys(selectedNotif.vacancy_by_category).length > 0 && (
                <div className="mb-6">
                  <h3 className="font-semibold text-gray-900 mb-2">Vacancy Breakdown</h3>
                  <div className="flex flex-wrap gap-2">
                    {Object.entries(selectedNotif.vacancy_by_category).map(([cat, count]) => (
                      <span key={cat} className="bg-gray-100 text-gray-800 text-sm px-3 py-1 rounded-lg">
                        {cat}: {count}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Age Relaxation */}
              {selectedNotif.age_relaxation && Object.keys(selectedNotif.age_relaxation).length > 0 && (
                <div className="mb-6">
                  <h3 className="font-semibold text-gray-900 mb-2">Age Relaxation</h3>
                  <div className="flex flex-wrap gap-2">
                    {Object.entries(selectedNotif.age_relaxation).map(([cat, years]) => (
                      <span key={cat} className="bg-orange-50 text-orange-800 text-sm px-3 py-1 rounded-lg">
                        {cat}: +{years} yrs
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Eligibility Reasons */}
              {selectedNotif.eligibility_reasons && selectedNotif.eligibility_reasons.length > 0 && (
                <div className="mb-6">
                  <h3 className="font-semibold text-gray-900 mb-2">Eligibility Details</h3>
                  <ul className="list-disc list-inside text-gray-600 space-y-1">
                    {selectedNotif.eligibility_reasons.map((reason, idx) => (
                      <li key={idx}>{reason}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex flex-col sm:flex-row gap-3 pt-4 border-t">
                {selectedNotif.original_pdf_url && (
                  <a
                    href={selectedNotif.original_pdf_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex-1 bg-red-600 text-white text-center py-3 px-4 rounded-lg hover:bg-red-700 font-medium transition"
                  >
                    Download PDF
                  </a>
                )}
                {selectedNotif.official_website_url && (
                  <a
                    href={selectedNotif.official_website_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex-1 bg-blue-600 text-white text-center py-3 px-4 rounded-lg hover:bg-blue-700 font-medium transition"
                  >
                    Official Website
                  </a>
                )}
                {!selectedNotif.original_pdf_url && !selectedNotif.official_website_url && (
                  <p className="text-sm text-gray-500 italic">No external links available for this notification.</p>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Notifications;
