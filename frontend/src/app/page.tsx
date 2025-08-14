'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8001';

interface User {
  id: number;
  employee_id: string;
  name: string;
  email: string;
  role: string;
  department?: string;
  created_at: string;
}

interface LeaveRequest {
  id: string;
  employee_id: string;
  leave_type: 'Annual' | 'Sick' | 'Unpaid';
  start_date: string;
  end_date: string;
  reason?: string;
  status: 'PENDING' | 'APPROVED' | 'DENIED' | 'CANCELLED';
  created_at: string;
  updated_at: string;
}

interface NewLeaveRequest {
  leave_type: 'Annual' | 'Sick' | 'Unpaid';
  start_date: string;
  end_date: string;
  reason?: string;
}

interface LoginData {
  email: string;
  password: string;
}

interface RegisterData {
  name: string;
  email: string;
  password: string;
  employee_id: string;
  department?: string;
}

export default function Home() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [showLogin, setShowLogin] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [leaveRequests, setLeaveRequests] = useState<LeaveRequest[]>([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  
  const [loginData, setLoginData] = useState<LoginData>({
    email: '',
    password: ''
  });

  const [registerData, setRegisterData] = useState<RegisterData>({
    name: '',
    email: '',
    password: '',
    employee_id: '',
    department: ''
  });
  
  const [formData, setFormData] = useState<NewLeaveRequest>({
    leave_type: 'Annual',
    start_date: '',
    end_date: '',
    reason: ''
  });

  // Admin filter states
  const [filterEmployeeId, setFilterEmployeeId] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [filteredRequests, setFilteredRequests] = useState<LeaveRequest[]>([]);

  // Set up axios interceptor for authentication
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      checkAuthStatus();
    }
  }, []);

  const checkAuthStatus = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/auth/me`);
      setCurrentUser(response.data);
      setIsAuthenticated(true);
      fetchLeaveRequests();
    } catch (error) {
      localStorage.removeItem('access_token');
      delete axios.defaults.headers.common['Authorization'];
    }
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const response = await axios.post(`${API_BASE_URL}/api/auth/login`, loginData);
      const { access_token } = response.data;
      
      localStorage.setItem('access_token', access_token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      await checkAuthStatus();
      setMessage('Login successful!');
      
      // Reset form
      setLoginData({ email: '', password: '' });
    } catch (error: any) {
      setMessage(error.response?.data?.detail || 'Login failed');
    }
    setLoading(false);
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      await axios.post(`${API_BASE_URL}/api/auth/register`, registerData);
      setMessage('Registration successful! Please login.');
      setShowLogin(true);
      
      // Reset form
      setRegisterData({
        name: '',
        email: '',
        password: '',
        employee_id: '',
        department: ''
      });
    } catch (error: any) {
      setMessage(error.response?.data?.detail || 'Registration failed');
    }
    setLoading(false);
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    delete axios.defaults.headers.common['Authorization'];
    setIsAuthenticated(false);
    setCurrentUser(null);
    setLeaveRequests([]);
    setMessage('Logged out successfully');
  };

  // Fetch leave requests
  const fetchLeaveRequests = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/leave-requests`);
      setLeaveRequests(response.data);
      applyFilters(response.data);
    } catch (error) {
      console.error('Error fetching leave requests:', error);
    }
  };

  // Apply filters for admin dashboard
  const applyFilters = (requests: LeaveRequest[]) => {
    let filtered = [...requests];

    // Filter by employee ID if provided
    if (filterEmployeeId.trim()) {
      filtered = filtered.filter(request => 
        request.employee_id.toLowerCase().includes(filterEmployeeId.toLowerCase())
      );
    }

    // Filter by status if provided
    if (filterStatus) {
      filtered = filtered.filter(request => request.status === filterStatus);
    }

    setFilteredRequests(filtered);
  };

  // Update filters when filter values change
  useEffect(() => {
    applyFilters(leaveRequests);
  }, [filterEmployeeId, filterStatus, leaveRequests]);

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      await axios.post(`${API_BASE_URL}/api/leave-requests`, formData);
      setMessage('Leave request created successfully!');
      setShowForm(false);
      setFormData({
        leave_type: 'Annual',
        start_date: '',
        end_date: '',
        reason: ''
      });
      fetchLeaveRequests();
    } catch (error: any) {
      setMessage(error.response?.data?.detail || 'Error creating leave request');
    }
    setLoading(false);
  };

  // Cancel a leave request
  const cancelRequest = async (id: string) => {
    try {
      await axios.patch(`${API_BASE_URL}/api/leave-requests/${id}/cancel`);
      setMessage('Leave request cancelled successfully!');
      fetchLeaveRequests();
    } catch (error: any) {
      setMessage(error.response?.data?.detail || 'Error cancelling leave request');
    }
  };

  // Admin approve/deny
  const handleDecision = async (id: string, decision: 'APPROVE' | 'DENY') => {
    try {
      await axios.patch(`${API_BASE_URL}/api/leave-requests/${id}/decision`, {
        decision
      });
      setMessage(`Leave request ${decision.toLowerCase()}d successfully!`);
      fetchLeaveRequests();
    } catch (error: any) {
      setMessage(error.response?.data?.detail || 'Error processing decision');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'PENDING': return 'text-yellow-600 bg-yellow-100';
      case 'APPROVED': return 'text-green-600 bg-green-100';
      case 'DENIED': return 'text-red-600 bg-red-100';
      case 'CANCELLED': return 'text-gray-600 bg-gray-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  // Show login/register form if not authenticated
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-md w-full space-y-8">
          <div>
            <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
              {showLogin ? 'Sign in to your account' : 'Create your account'}
            </h2>
          </div>
          
          {message && (
            <div className={`p-4 rounded-md ${
              message.includes('Error') || message.includes('failed') 
                ? 'bg-red-100 text-red-700' 
                : 'bg-green-100 text-green-700'
            }`}>
              {message}
              <button 
                onClick={() => setMessage('')}
                className="ml-2 text-sm underline"
              >
                Dismiss
              </button>
            </div>
          )}

          {showLogin ? (
            <form className="mt-8 space-y-6" onSubmit={handleLogin}>
              <div>
                <label className="block text-sm font-medium text-gray-700">Email</label>
                <input
                  type="email"
                  value={loginData.email}
                  onChange={(e) => setLoginData({...loginData, email: e.target.value})}
                  required
                  className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter your email"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Password</label>
                <input
                  type="password"
                  value={loginData.password}
                  onChange={(e) => setLoginData({...loginData, password: e.target.value})}
                  required
                  className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter your password"
                />
              </div>
              <button
                type="submit"
                disabled={loading}
                className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
              >
                {loading ? 'Signing in...' : 'Sign in'}
              </button>
              <div className="text-center">
                <button
                  type="button"
                  onClick={() => setShowLogin(false)}
                  className="text-blue-600 hover:text-blue-500"
                >
                  Don't have an account? Sign up
                </button>
              </div>
              
              <div className="mt-4 p-4 bg-blue-50 rounded-md">
                <p className="text-sm text-blue-700 font-medium">Demo Accounts:</p>
                <p className="text-xs text-blue-600">Employee: john.doe@revna.com / password123</p>
                <p className="text-xs text-blue-600">Admin: admin@revna.com / admin123</p>
              </div>
            </form>
          ) : (
            <form className="mt-8 space-y-6" onSubmit={handleRegister}>
              <div>
                <label className="block text-sm font-medium text-gray-700">Full Name</label>
                <input
                  type="text"
                  value={registerData.name}
                  onChange={(e) => setRegisterData({...registerData, name: e.target.value})}
                  required
                  className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Email</label>
                <input
                  type="email"
                  value={registerData.email}
                  onChange={(e) => setRegisterData({...registerData, email: e.target.value})}
                  required
                  className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Password</label>
                <input
                  type="password"
                  value={registerData.password}
                  onChange={(e) => setRegisterData({...registerData, password: e.target.value})}
                  required
                  className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Employee ID</label>
                <input
                  type="text"
                  value={registerData.employee_id}
                  onChange={(e) => setRegisterData({...registerData, employee_id: e.target.value})}
                  required
                  className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., EMP123"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Department (Optional)</label>
                <input
                  type="text"
                  value={registerData.department}
                  onChange={(e) => setRegisterData({...registerData, department: e.target.value})}
                  className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., Engineering"
                />
              </div>
              <button
                type="submit"
                disabled={loading}
                className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
              >
                {loading ? 'Creating account...' : 'Create account'}
              </button>
              <div className="text-center">
                <button
                  type="button"
                  onClick={() => setShowLogin(true)}
                  className="text-blue-600 hover:text-blue-500"
                >
                  Already have an account? Sign in
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    );
  }

  // Main application for authenticated users
  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4">
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="flex justify-between items-center mb-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Leave Request System</h1>
              <p className="text-gray-600">Welcome, {currentUser?.name} ({currentUser?.role})</p>
              {currentUser?.role === 'ADMIN' && (
                <p className="text-sm text-blue-600 mt-1">
                  Admin Dashboard - View and manage all employee leave requests
                </p>
              )}
            </div>
            <div className="flex gap-4">
              {currentUser?.role !== 'ADMIN' && (
                <button
                  onClick={() => setShowForm(!showForm)}
                  className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
                >
                  {showForm ? 'Cancel' : 'New Leave Request'}
                </button>
              )}
              <button
                onClick={handleLogout}
                className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 transition-colors"
              >
                Logout
              </button>
            </div>
          </div>

          {message && (
            <div className={`p-4 rounded-md mb-4 ${
              message.includes('Error') 
                ? 'bg-red-100 text-red-700' 
                : 'bg-green-100 text-green-700'
            }`}>
              {message}
              <button 
                onClick={() => setMessage('')}
                className="ml-2 text-sm underline"
              >
                Dismiss
              </button>
            </div>
          )}

          {showForm && currentUser?.role !== 'ADMIN' && (
            <form onSubmit={handleSubmit} className="bg-gray-50 p-6 rounded-lg mb-6">
              <h2 className="text-xl font-semibold mb-4">Create Leave Request</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Leave Type
                  </label>
                  <select
                    value={formData.leave_type}
                    onChange={(e) => setFormData({...formData, leave_type: e.target.value as any})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="Annual">Annual</option>
                    <option value="Sick">Sick</option>
                    <option value="Unpaid">Unpaid</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Start Date
                  </label>
                  <input
                    type="date"
                    value={formData.start_date}
                    onChange={(e) => setFormData({...formData, start_date: e.target.value})}
                    min={new Date().toISOString().split('T')[0]}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    End Date
                  </label>
                  <input
                    type="date"
                    value={formData.end_date}
                    onChange={(e) => setFormData({...formData, end_date: e.target.value})}
                    min={formData.start_date || new Date().toISOString().split('T')[0]}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>
              </div>
              
              <div className="mt-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Reason (Optional)
                </label>
                <textarea
                  value={formData.reason}
                  onChange={(e) => setFormData({...formData, reason: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  rows={3}
                  placeholder="Enter reason for leave..."
                />
              </div>
              
              <button
                type="submit"
                disabled={loading}
                className="mt-4 bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50"
              >
                {loading ? 'Creating...' : 'Create Leave Request'}
              </button>
            </form>
          )}

          <div>
            <h2 className="text-xl font-semibold mb-4">
              {currentUser?.role === 'ADMIN' ? 'All Leave Requests' : 'My Leave Requests'}
            </h2>
            
            {/* Admin filters */}
            {currentUser?.role === 'ADMIN' && (
              <div className="bg-gray-50 p-4 rounded-lg mb-6">
                <h3 className="text-lg font-medium mb-3">Filters</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Employee ID
                    </label>
                    <input
                      type="text"
                      value={filterEmployeeId}
                      onChange={(e) => setFilterEmployeeId(e.target.value)}
                      placeholder="Search by employee ID..."
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Status
                    </label>
                    <select
                      value={filterStatus}
                      onChange={(e) => setFilterStatus(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">All Statuses</option>
                      <option value="PENDING">Pending</option>
                      <option value="APPROVED">Approved</option>
                      <option value="DENIED">Denied</option>
                      <option value="CANCELLED">Cancelled</option>
                    </select>
                  </div>
                  
                  <div className="flex items-end">
                    <button
                      onClick={() => {
                        setFilterEmployeeId('');
                        setFilterStatus('');
                      }}
                      className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors"
                    >
                      Clear Filters
                    </button>
                  </div>
                </div>
                
                <div className="mt-3 text-sm text-gray-600">
                  Showing {filteredRequests.length} of {leaveRequests.length} requests
                </div>
              </div>
            )}
            
            {(currentUser?.role === 'ADMIN' ? filteredRequests : leaveRequests).length === 0 ? (
              <p className="text-gray-500 text-center py-8">
                {currentUser?.role === 'ADMIN' && (filterEmployeeId || filterStatus) 
                  ? 'No requests match the current filters' 
                  : 'No leave requests found'
                }
              </p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full table-auto">
                  <thead>
                    <tr className="bg-gray-100">
                      <th className="px-4 py-2 text-left">Employee ID</th>
                      <th className="px-4 py-2 text-left">Type</th>
                      <th className="px-4 py-2 text-left">Start Date</th>
                      <th className="px-4 py-2 text-left">End Date</th>
                      <th className="px-4 py-2 text-left">Reason</th>
                      <th className="px-4 py-2 text-left">Status</th>
                      <th className="px-4 py-2 text-left">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(currentUser?.role === 'ADMIN' ? filteredRequests : leaveRequests).map((request) => (
                      <tr key={request.id} className="border-t">
                        <td className="px-4 py-2">{request.employee_id}</td>
                        <td className="px-4 py-2">{request.leave_type}</td>
                        <td className="px-4 py-2">{request.start_date}</td>
                        <td className="px-4 py-2">{request.end_date}</td>
                        <td className="px-4 py-2">{request.reason || '-'}</td>
                        <td className="px-4 py-2">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(request.status)}`}>
                            {request.status}
                          </span>
                        </td>
                        <td className="px-4 py-2">
                          <div className="flex gap-2">
                            {request.status === 'PENDING' && 
                             request.employee_id === currentUser?.employee_id && (
                              <button
                                onClick={() => cancelRequest(request.id)}
                                className="bg-red-600 text-white px-3 py-1 rounded text-xs hover:bg-red-700"
                              >
                                Cancel
                              </button>
                            )}
                            {request.status === 'PENDING' && currentUser?.role === 'ADMIN' && (
                              <>
                                <button
                                  onClick={() => handleDecision(request.id, 'APPROVE')}
                                  className="bg-green-600 text-white px-3 py-1 rounded text-xs hover:bg-green-700"
                                >
                                  Approve
                                </button>
                                <button
                                  onClick={() => handleDecision(request.id, 'DENY')}
                                  className="bg-red-600 text-white px-3 py-1 rounded text-xs hover:bg-red-700"
                                >
                                  Deny
                                </button>
                              </>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
