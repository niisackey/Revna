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
  employee_id: string;
  leave_type: 'Annual' | 'Sick' | 'Unpaid';
  start_date: string;
  end_date: string;
  reason?: string;
}

export default function Home() {
  const [leaveRequests, setLeaveRequests] = useState<LeaveRequest[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  
  const [formData, setFormData] = useState<NewLeaveRequest>({
    employee_id: 'EMP001',
    leave_type: 'Annual',
    start_date: '',
    end_date: '',
    reason: ''
  });

  // Fetch all users
  const fetchUsers = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/users`);
      setUsers(response.data);
      // Set default user
      if (response.data.length > 0) {
        setCurrentUser(response.data[0]);
        setFormData(prev => ({ ...prev, employee_id: response.data[0].employee_id }));
      }
    } catch (error) {
      console.error('Error fetching users:', error);
    }
  };

  // Fetch all leave requests
  const fetchLeaveRequests = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/leave-requests`);
      setLeaveRequests(response.data);
    } catch (error) {
      console.error('Error fetching leave requests:', error);
      setMessage('Error fetching leave requests');
    }
  };

  useEffect(() => {
    fetchUsers();
    fetchLeaveRequests();
  }, []);

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      await axios.post(`${API_BASE_URL}/api/leave-requests`, formData);
      setMessage('Leave request created successfully!');
      setShowForm(false);
      setFormData({
        employee_id: 'EMP001',
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

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4">
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="flex justify-between items-center mb-6">
            <h1 className="text-3xl font-bold text-gray-900">Leave Request System</h1>
            <div className="flex gap-4">
              <div className="flex items-center gap-2">
                <label className="text-sm font-medium">Current User:</label>
                <select
                  value={currentUser?.employee_id || ''}
                  onChange={(e) => {
                    const user = users.find(u => u.employee_id === e.target.value);
                    setCurrentUser(user || null);
                    setFormData(prev => ({ ...prev, employee_id: e.target.value }));
                  }}
                  className="px-3 py-1 border border-gray-300 rounded-md text-sm"
                >
                  {users.map(user => (
                    <option key={user.employee_id} value={user.employee_id}>
                      {user.name} ({user.role})
                    </option>
                  ))}
                </select>
              </div>
              <button
                onClick={() => setShowForm(!showForm)}
                className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
              >
                {showForm ? 'Cancel' : 'New Leave Request'}
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

          {showForm && (
            <form onSubmit={handleSubmit} className="bg-gray-50 p-6 rounded-lg mb-6">
              <h2 className="text-xl font-semibold mb-4">Create Leave Request</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Employee ID
                  </label>
                  <input
                    type="text"
                    value={formData.employee_id}
                    onChange={(e) => setFormData({...formData, employee_id: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-gray-100"
                    required
                    readOnly
                  />
                </div>
                
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
            <h2 className="text-xl font-semibold mb-4">Leave Requests</h2>
            
            {leaveRequests.length === 0 ? (
              <p className="text-gray-500 text-center py-8">No leave requests found</p>
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
                    {leaveRequests.map((request) => (
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
                            {request.status === 'PENDING' && currentUser?.role === 'EMPLOYEE' && request.employee_id === currentUser.employee_id && (
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
