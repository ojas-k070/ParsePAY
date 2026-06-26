import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';

const Login = () => {
  const { user, login, register, error } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();

  const [activeTab, setActiveTab] = useState('login'); // 'login' or 'register'
  const [userIdInput, setUserIdInput] = useState('');
  const [usernameInput, setUsernameInput] = useState('');
  const [localError, setLocalError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [submitting, setSubmitting] = useState(false);

  // If already logged in, redirect to upload home page
  useEffect(() => {
    if (user) {
      navigate('/');
    }
  }, [user, navigate]);

  const handleLoginSubmit = async (e) => {
    e.preventDefault();
    if (!userIdInput.trim()) return;
    
    setSubmitting(true);
    setLocalError('');
    setSuccessMessage('');
    
    const res = await login(userIdInput);
    setSubmitting(false);
    
    if (res.success) {
      navigate('/');
    } else {
      setLocalError(res.error || 'Failed to login');
    }
  };

  const handleRegisterSubmit = async (e) => {
    e.preventDefault();
    if (!usernameInput.trim()) return;
    
    setSubmitting(true);
    setLocalError('');
    setSuccessMessage('');
    
    const res = await register(usernameInput);
    setSubmitting(false);
    
    if (res.success) {
      setSuccessMessage(`Profile created successfully! Your unique User ID is: ${res.user.unique_id}. Save this to login from other devices.`);
      // Clear input
      setUsernameInput('');
      // Delay navigation slightly so they can read the User ID
      setTimeout(() => {
        navigate('/');
      }, 7000);
    } else {
      setLocalError(res.error || 'Failed to create profile');
    }
  };

  return (
    <div className="dashboard-body login-body">
      {/* Floating Theme Toggle Button */}
      <button className="theme-toggle-float" onClick={toggleTheme} title="Toggle Light/Dark Theme">
        <span id="theme-icon">{theme === 'light' ? '🌙' : '☀️'}</span>
      </button>

      <div className="login-wrapper">
        {/* Logo and App Name */}
        <div className="login-logo-container">
          <div className="rupee-icon">₹</div>
          <h1>ParsePAY</h1>
          <p className="tagline">Personalized Bank Statement Analytics</p>
        </div>

        {/* Glassmorphic Form Container */}
        <div className="login-card glass">
          
          {/* Tabs to toggle between Login & Register */}
          <div className="login-tabs">
            <button 
              className={`tab-btn ${activeTab === 'login' ? 'active' : ''}`}
              onClick={() => { setActiveTab('login'); setLocalError(''); setSuccessMessage(''); }}
            >
              Access Profile
            </button>
            <button 
              className={`tab-btn ${activeTab === 'register' ? 'active' : ''}`}
              onClick={() => { setActiveTab('register'); setLocalError(''); setSuccessMessage(''); }}
            >
              New Profile
            </button>
          </div>

          {/* Display Messages */}
          {localError && (
            <div className="alert alert-error">{localError}</div>
          )}
          {error && !localError && (
            <div className="alert alert-error">{error}</div>
          )}
          {successMessage && (
            <div className="alert alert-success" style={{ whiteSpace: 'pre-wrap' }}>{successMessage}</div>
          )}

          {/* Tab 1: Access Profile */}
          {activeTab === 'login' && (
            <div className="tab-content active">
              <form onSubmit={handleLoginSubmit}>
                <div className="form-group">
                  <label htmlFor="user_id">Enter Your Profile User ID</label>
                  <input 
                    type="text" 
                    id="user_id" 
                    name="user_id" 
                    placeholder="e.g. RS-1234" 
                    value={userIdInput}
                    onChange={(e) => setUserIdInput(e.target.value)}
                    autoComplete="off" 
                    required 
                    disabled={submitting}
                  />
                  <span className="help-text">Your generated ID is required to reload your statement history.</span>
                </div>
                <button type="submit" className="primary-btn" disabled={submitting}>
                  {submitting ? 'Opening...' : 'Open Dashboard'}
                </button>
              </form>
            </div>
          )}

          {/* Tab 2: Create New Profile */}
          {activeTab === 'register' && (
            <div className="tab-content active">
              <form onSubmit={handleRegisterSubmit}>
                <div className="form-group">
                  <label htmlFor="username">Your Name / Profile Name</label>
                  <input 
                    type="text" 
                    id="username" 
                    name="username" 
                    placeholder="e.g. Ojas Kulkarni" 
                    value={usernameInput}
                    onChange={(e) => setUsernameInput(e.target.value)}
                    autoComplete="off" 
                    required 
                    disabled={submitting}
                  />
                  <span className="help-text">Creating a profile generates a unique ID. Write it down to access your data later!</span>
                </div>
                <button type="submit" className="primary-btn" disabled={submitting}>
                  {submitting ? 'Creating...' : 'Create Profile'}
                </button>
              </form>
            </div>
          )}

        </div>

        {/* Extra details/security note */}
        <div className="privacy-note">
          <p>🔒 <strong>Privacy Assurance</strong>: Your transaction details are stored locally on your unique profile database and are never shared or made visible to other visitors.</p>
        </div>

      </div>
    </div>
  );
};

export default Login;
