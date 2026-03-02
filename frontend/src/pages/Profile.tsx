import React, { useState, useEffect } from 'react';
import { userAPI } from '../api/services';
import type { UserPreferences } from '../api/services';
import { useAuth } from '../context/AuthContext';

const INDIAN_STATES = [
  'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh',
  'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand',
  'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur',
  'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Punjab',
  'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana', 'Tripura',
  'Uttar Pradesh', 'Uttarakhand', 'West Bengal',
  'Andaman and Nicobar Islands', 'Chandigarh', 'Dadra and Nagar Haveli and Daman and Diu',
  'Delhi', 'Jammu and Kashmir', 'Ladakh', 'Lakshadweep', 'Puducherry',
];

const EXAM_TYPES = ['Central', 'State', 'Banking', 'Railway', 'Defence', 'PSU'];

const POPULAR_ORGS = [
  'UPSC', 'SSC', 'IBPS', 'RBI', 'RRB', 'NTA', 'DRDO', 'ISRO',
  'BPSC', 'UPPSC', 'MPPSC', 'RPSC', 'WBPSC', 'KPSC', 'TNPSC',
  'APPSC', 'TSPSC', 'HPPSC', 'UKPSC', 'CGPSC', 'JPSC', 'GPSC', 'MPSC',
  'SBI', 'NABARD', 'LIC', 'EPFO', 'FCI', 'SAIL', 'ONGC', 'NTPC', 'AAI',
];

const Profile: React.FC = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [savingPrefs, setSavingPrefs] = useState(false);
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');
  const [telegramUsername, setTelegramUsername] = useState('');
  const [activeTab, setActiveTab] = useState<'profile' | 'preferences'>('profile');

  const [profile, setProfile] = useState({
    dob: '',
    gender: '',
    education_level: '',
    education_stream: '',
    category: '',
    state: '',
    exam_interests: [] as string[],
  });

  const [preferences, setPreferences] = useState<UserPreferences>({
    preferred_exam_types: [],
    preferred_states: [],
    preferred_orgs: [],
    min_education: undefined,
    notify_via: ['website'],
    max_notifications_per_day: 10,
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [profileRes, meRes, prefsRes] = await Promise.all([
        userAPI.getProfile(),
        userAPI.getMe(),
        userAPI.getPreferences(),
      ]);
      const data = profileRes.data;
      setProfile({
        dob: data.dob || '',
        gender: data.gender || '',
        education_level: data.education_level || '',
        education_stream: data.education_stream || '',
        category: data.category || '',
        state: data.state || '',
        exam_interests: data.exam_interests || [],
      });
      setTelegramUsername(meRes.data.telegram_username || '');
      if (prefsRes.data) {
        setPreferences({
          preferred_exam_types: prefsRes.data.preferred_exam_types || [],
          preferred_states: prefsRes.data.preferred_states || [],
          preferred_orgs: prefsRes.data.preferred_orgs || [],
          min_education: prefsRes.data.min_education || undefined,
          notify_via: prefsRes.data.notify_via || ['website'],
          max_notifications_per_day: prefsRes.data.max_notifications_per_day || 10,
        });
      }
    } catch (err) {
      setError('Failed to load profile. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setSaving(true);
    try {
      await userAPI.updateProfile(profile);
      setSuccess('Profile updated successfully!');
      setTimeout(() => setSuccess(''), 3000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update profile');
    } finally {
      setSaving(false);
    }
  };

  const handleSubmitPreferences = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setSavingPrefs(true);
    try {
      await userAPI.updatePreferences(preferences);
      setSuccess('Preferences saved! Your "For You" feed will update.');
      setTimeout(() => setSuccess(''), 3000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update preferences');
    } finally {
      setSavingPrefs(false);
    }
  };

  const toggleExamInterest = (interest: string) => {
    setProfile((prev) => ({
      ...prev,
      exam_interests: prev.exam_interests.includes(interest)
        ? prev.exam_interests.filter((i) => i !== interest)
        : [...prev.exam_interests, interest],
    }));
  };

  const toggleChip = (
    list: string[],
    item: string,
    setter: (fn: (prev: UserPreferences) => UserPreferences) => void,
    field: keyof UserPreferences
  ) => {
    setter((prev) => ({
      ...prev,
      [field]: (prev[field] as string[]).includes(item)
        ? (prev[field] as string[]).filter((i: string) => i !== item)
        : [...(prev[field] as string[]), item],
    }));
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-3xl mx-auto px-4">
          <div className="bg-white rounded-lg shadow-lg p-8 animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-1/3 mb-4"></div>
            <div className="h-4 bg-gray-200 rounded w-2/3 mb-8"></div>
            <div className="grid grid-cols-2 gap-6">
              {[...Array(6)].map((_, i) => (
                <div key={i}>
                  <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
                  <div className="h-10 bg-gray-200 rounded"></div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-3xl mx-auto px-4">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <div className="mb-6">
            <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
            <p className="text-gray-600 mt-2">
              Manage your profile and notification preferences
            </p>
            {user && (
              <div className="mt-2 flex items-center gap-2">
                <span className="text-sm text-gray-600">{user.email}</span>
                {user.is_premium && (
                  <span className="bg-yellow-100 text-yellow-800 text-xs px-2 py-1 rounded-full">
                    Premium
                  </span>
                )}
              </div>
            )}
          </div>

          {/* Tab Switcher */}
          <div className="flex border-b border-gray-200 mb-6">
            <button
              onClick={() => setActiveTab('profile')}
              className={`px-6 py-3 text-sm font-medium border-b-2 transition ${activeTab === 'profile'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
            >
              👤 Profile
            </button>
            <button
              onClick={() => setActiveTab('preferences')}
              className={`px-6 py-3 text-sm font-medium border-b-2 transition ${activeTab === 'preferences'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
            >
              🔔 Notification Preferences
            </button>
          </div>

          {error && (
            <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
              {error}
            </div>
          )}

          {success && (
            <div className="mb-4 p-3 bg-green-100 border border-green-400 text-green-700 rounded">
              {success}
            </div>
          )}

          {/* Profile Tab */}
          {activeTab === 'profile' && (
            <form onSubmit={handleSubmitProfile} className="space-y-6">
              {/* Telegram Username (read-only info) */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <label className="block text-sm font-medium text-blue-800 mb-1">
                  Telegram Username
                </label>
                <div className="text-sm text-blue-700">
                  {telegramUsername ? (
                    <span>@{telegramUsername.replace('@', '')}</span>
                  ) : (
                    <span className="text-blue-500 italic">
                      Not set. Set during registration to receive notifications via Telegram.
                    </span>
                  )}
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Date of Birth
                  </label>
                  <input
                    type="date"
                    value={profile.dob}
                    onChange={(e) => setProfile({ ...profile, dob: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Gender</label>
                  <select
                    value={profile.gender}
                    onChange={(e) => setProfile({ ...profile, gender: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Select Gender</option>
                    <option value="M">Male</option>
                    <option value="F">Female</option>
                    <option value="Other">Other</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Education Level</label>
                  <select
                    value={profile.education_level}
                    onChange={(e) => setProfile({ ...profile, education_level: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Select Education</option>
                    <option value="10th">10th</option>
                    <option value="12th">12th</option>
                    <option value="Diploma">Diploma</option>
                    <option value="Graduation">Graduation</option>
                    <option value="Post Graduation">Post Graduation</option>
                    <option value="PhD">PhD</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Education Stream</label>
                  <input
                    type="text"
                    value={profile.education_stream}
                    onChange={(e) => setProfile({ ...profile, education_stream: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder="e.g., Science, Commerce, Arts"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Category</label>
                  <select
                    value={profile.category}
                    onChange={(e) => setProfile({ ...profile, category: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Select Category</option>
                    <option value="General">General</option>
                    <option value="OBC">OBC</option>
                    <option value="SC">SC</option>
                    <option value="ST">ST</option>
                    <option value="EWS">EWS</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">State</label>
                  <select
                    value={profile.state}
                    onChange={(e) => setProfile({ ...profile, state: e.target.value })}
                    aria-label="State"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Select State</option>
                    {INDIAN_STATES.map((state) => (
                      <option key={state} value={state}>{state}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">Exam Interests</label>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                  {EXAM_TYPES.map((interest) => (
                    <label key={interest} className="flex items-center space-x-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={profile.exam_interests.includes(interest)}
                        onChange={() => toggleExamInterest(interest)}
                        className="w-4 h-4 text-blue-600 focus:ring-blue-500"
                      />
                      <span className="text-sm text-gray-700">{interest}</span>
                    </label>
                  ))}
                </div>
              </div>

              <button
                type="submit"
                disabled={saving}
                className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 disabled:opacity-50 font-medium transition"
              >
                {saving ? 'Saving...' : 'Save Profile'}
              </button>
            </form>
          )}

          {/* Preferences Tab */}
          {activeTab === 'preferences' && (
            <form onSubmit={handleSubmitPreferences} className="space-y-6">
              {/* Exam Types */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  🎯 Preferred Exam Types
                </label>
                <p className="text-xs text-gray-500 mb-2">Select the types of exams you're interested in</p>
                <div className="flex flex-wrap gap-2">
                  {EXAM_TYPES.map((type) => (
                    <button
                      key={type}
                      type="button"
                      onClick={() => toggleChip(preferences.preferred_exam_types, type, setPreferences, 'preferred_exam_types')}
                      className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${preferences.preferred_exam_types.includes(type)
                          ? 'bg-blue-600 text-white shadow-md'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                        }`}
                    >
                      {preferences.preferred_exam_types.includes(type) ? '✓ ' : ''}{type}
                    </button>
                  ))}
                </div>
              </div>

              {/* Preferred States */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  📍 Preferred States
                </label>
                <p className="text-xs text-gray-500 mb-2">Get notified about state-level exams in these states</p>
                <div className="flex flex-wrap gap-2 max-h-48 overflow-y-auto p-2 border border-gray-200 rounded-lg">
                  {INDIAN_STATES.slice(0, 28).map((state) => (
                    <button
                      key={state}
                      type="button"
                      onClick={() => toggleChip(preferences.preferred_states, state, setPreferences, 'preferred_states')}
                      className={`px-3 py-1.5 rounded-full text-xs font-medium transition-all ${preferences.preferred_states.includes(state)
                          ? 'bg-green-600 text-white shadow-md'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                        }`}
                    >
                      {preferences.preferred_states.includes(state) ? '✓ ' : ''}{state}
                    </button>
                  ))}
                </div>
              </div>

              {/* Preferred Organizations */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  🏛 Preferred Organizations
                </label>
                <p className="text-xs text-gray-500 mb-2">Follow specific organizations</p>
                <div className="flex flex-wrap gap-2 max-h-48 overflow-y-auto p-2 border border-gray-200 rounded-lg">
                  {POPULAR_ORGS.map((org) => (
                    <button
                      key={org}
                      type="button"
                      onClick={() => toggleChip(preferences.preferred_orgs, org, setPreferences, 'preferred_orgs')}
                      className={`px-3 py-1.5 rounded-full text-xs font-medium transition-all ${preferences.preferred_orgs.includes(org)
                          ? 'bg-purple-600 text-white shadow-md'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                        }`}
                    >
                      {preferences.preferred_orgs.includes(org) ? '✓ ' : ''}{org}
                    </button>
                  ))}
                </div>
              </div>

              {/* Min Education */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  🎓 Minimum Education Level
                </label>
                <p className="text-xs text-gray-500 mb-2">Only show jobs requiring at least this level</p>
                <select
                  value={preferences.min_education || ''}
                  onChange={(e) => setPreferences({ ...preferences, min_education: e.target.value || undefined })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Any Education</option>
                  <option value="10th">10th</option>
                  <option value="12th">12th</option>
                  <option value="Diploma">Diploma</option>
                  <option value="Graduation">Graduation</option>
                  <option value="Post Graduation">Post Graduation</option>
                  <option value="PhD">PhD</option>
                </select>
              </div>

              {/* Notification Channels */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  📬 Notification Channels
                </label>
                <div className="space-y-3">
                  <label className="flex items-center space-x-3 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={preferences.notify_via.includes('website')}
                      onChange={() => toggleChip(preferences.notify_via, 'website', setPreferences, 'notify_via')}
                      className="w-5 h-5 text-blue-600 focus:ring-blue-500 rounded"
                    />
                    <span className="text-sm text-gray-700">🌐 Website (For You feed)</span>
                  </label>
                  <label className="flex items-center space-x-3 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={preferences.notify_via.includes('telegram')}
                      onChange={() => toggleChip(preferences.notify_via, 'telegram', setPreferences, 'notify_via')}
                      className="w-5 h-5 text-blue-600 focus:ring-blue-500 rounded"
                    />
                    <span className="text-sm text-gray-700">📱 Telegram Bot</span>
                    {!user?.is_premium && (
                      <span className="text-xs text-yellow-600 bg-yellow-50 px-2 py-0.5 rounded">
                        Premium only
                      </span>
                    )}
                  </label>
                </div>
              </div>

              <button
                type="submit"
                disabled={savingPrefs}
                className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 disabled:opacity-50 font-medium transition"
              >
                {savingPrefs ? 'Saving...' : 'Save Preferences'}
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};

export default Profile;
