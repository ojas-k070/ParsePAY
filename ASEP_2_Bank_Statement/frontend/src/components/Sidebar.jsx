import React, { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate, useParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import SupportPopup from './SupportPopup';

const Sidebar = () => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const { fileId } = useParams();
  const { isSidebarOpen, closeSidebar } = useTheme();
  
  const [statements, setStatements] = useState([]);
  const [isSupportOpen, setIsSupportOpen] = useState(false);
  const [loading, setLoading] = useState(false);

  const fetchStatements = async () => {
    try {
      const res = await fetch('/api/statements');
      const data = await res.json();
      if (data.success) {
        setStatements(data.statements || []);
      }
    } catch (err) {
      console.error('Error fetching statements:', err);
    }
  };

  useEffect(() => {
    if (user) {
      fetchStatements();
    }
  }, [user, fileId]); // Refresh list when active file changes or user changes
  
  useEffect(() => {
    closeSidebar();
  }, [location.pathname]);

  const handleDelete = async (id, e) => {
    e.preventDefault();
    e.stopPropagation();
    if (!window.confirm('Are you sure you want to delete this statement?')) {
      return;
    }
    try {
      setLoading(true);
      const res = await fetch(`/api/delete-statement/${id}`, {
        method: 'POST', // Backend handles both POST and DELETE
      });
      const data = await res.json();
      if (data.success) {
        // If we deleted the active statement, redirect to home
        if (fileId && parseInt(fileId) === id) {
          navigate('/');
        } else {
          fetchStatements();
        }
      } else {
        alert('Failed to delete statement: ' + (data.error || 'Unknown error'));
      }
    } catch (err) {
      console.error('Error deleting statement:', err);
      alert('Network error while deleting statement.');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async (e) => {
    e.preventDefault();
    await logout();
    navigate('/login');
  };

  const isUploadActive = location.pathname === '/' || location.pathname === '/upload';
  const isDashboardActive = location.pathname.startsWith('/dashboard');

  return (
    <>
      {/* Sidebar Overlay backdrop */}
      <div className={`sidebar-overlay ${isSidebarOpen ? 'active' : ''}`} onClick={closeSidebar}></div>

      <aside className={`sidebar glass ${isSidebarOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <div className="rupee-icon">₹</div>
          <h3>ParsePAY</h3>
          <button className="sidebar-close-btn" onClick={closeSidebar} title="Close Menu">✕</button>
        </div>

        {user && (
          <div className="user-profile-badge">
            <div className="user-avatar">👤</div>
            <div className="user-info">
              <span className="profile-name">{user.username}</span>
              <span className="profile-id">{user.unique_id}</span>
            </div>
          </div>
        )}

        <nav className="sidebar-nav">
          <Link to="/" className={`nav-item ${isUploadActive ? 'active' : ''}`}>
            <span className="nav-icon">📤</span>
            Upload Statement
          </Link>
          
          {fileId && (
            <Link to={`/dashboard/${fileId}`} className={`nav-item ${isDashboardActive ? 'active' : ''}`}>
              <span className="nav-icon">📊</span>
              Dashboard
            </Link>
          )}

          <a href="#logout" onClick={handleLogout} className="nav-item logout-item">
            <span className="nav-icon">🔓</span>
            Logout Profile
          </a>
        </nav>

        <div className="recent-uploads-section">
          <h4>Recent Statements</h4>
          <div className="recent-list">
            {statements.length > 0 ? (
              statements.map((st) => {
                const isActive = fileId && parseInt(fileId) === st.id;
                return (
                  <div key={st.id} className={`recent-file-item ${isActive ? 'active-file' : ''}`}>
                    <Link to={`/dashboard/${st.id}`} className="file-link">
                      <span className="file-icon">📄</span>
                      <span className="file-name" title={st.filename}>{st.filename}</span>
                    </Link>
                    <button
                      onClick={(e) => handleDelete(st.id, e)}
                      className="delete-btn-icon"
                      title="Delete Statement"
                      disabled={loading}
                    >
                      🗑️
                    </button>
                  </div>
                );
              })
            ) : (
              <p className="no-uploads">No statements uploaded yet.</p>
            )}
          </div>
        </div>

        <div className="sidebar-footer">
          <button className="support-btn" onClick={() => setIsSupportOpen(true)}>
            Support / Contact
          </button>
        </div>
      </aside>

      <SupportPopup isOpen={isSupportOpen} onClose={() => setIsSupportOpen(false)} />
    </>
  );
};

export default Sidebar;
