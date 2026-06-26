import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Sidebar from '../components/Sidebar';
import { useTheme } from '../context/ThemeContext';

const Upload = () => {
  const { theme, toggleTheme, toggleSidebar, isSidebarOpen } = useTheme();
  const navigate = useNavigate();
  
  const [selectedFile, setSelectedFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      validateAndSetFile(file);
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      validateAndSetFile(file);
    }
  };

  const validateAndSetFile = (file) => {
    setError('');
    if (file.type !== "application/pdf" && !file.name.endsWith('.pdf')) {
      setError("Invalid file format. Only PDF statements are allowed.");
      setSelectedFile(null);
      return;
    }
    setSelectedFile(file);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedFile) {
      setError("Please select a statement PDF file to analyze.");
      return;
    }

    setLoading(true);
    setError('');

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const res = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
        headers: {
          'Accept': 'application/json'
        }
      });
      
      const data = await res.json();
      if (data.success) {
        navigate(`/dashboard/${data.file_id}`);
      } else {
        setError(data.error || 'Failed to process the bank statement. Please try again.');
      }
    } catch (err) {
      console.error("Upload error:", err);
      setError("Network error occurred during upload. Check server status.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={`dashboard-container ${isSidebarOpen ? 'sidebar-open' : ''}`}>
      {/* Menu Toggle Button */}
      {!isSidebarOpen && (
        <button className="sidebar-toggle-btn" onClick={toggleSidebar} title="Open Menu">
          <span>☰</span>
        </button>
      )}

      {/* Floating Theme Toggle Button */}
      <button className="theme-toggle-float" onClick={toggleTheme} title="Toggle Light/Dark Theme">
        <span id="theme-icon">{theme === 'light' ? '🌙' : '☀️'}</span>
      </button>

      {/* Sidebar navigation */}
      <Sidebar />

      {/* Main Content Area */}
      <main className="main-content center-content">
        <div className="upload-card glass">
          <div className="upload-header">
            <h2>Track Your Spendings</h2>
            <p className="subtitle">Upload your bank statement and get detailed analytics instantly.</p>
          </div>

          {error && (
            <div className="alert alert-error">{error}</div>
          )}

          <div className="instructions-box">
            <h3>💡 Quick Instructions</h3>
            <ul>
              <li>We currently support <strong>SBI (State Bank of India)</strong> statements.</li>
              <li>Ensure the PDF file is <strong>not</strong> password-protected.</li>
            </ul>
          </div>

          <form id="uploadForm" onSubmit={handleSubmit}>
            <div 
              className={`dropzone ${dragActive ? 'drag-active' : ''} ${selectedFile ? 'has-file' : ''}`}
              onDragEnter={handleDrag}
              onDragOver={handleDrag}
              onDragLeave={handleDrag}
              onDrop={handleDrop}
              onClick={() => document.getElementById('fileInput').click()}
            >
              <input 
                type="file" 
                id="fileInput" 
                name="file" 
                accept=".pdf" 
                onChange={handleChange}
                required
                disabled={loading}
              />
              <div className="dropzone-icon">📄</div>
              <p className="dropzone-text">
                {selectedFile ? 'Change statement file' : 'Drag and drop your PDF statement here, or click to browse'}
              </p>
              {selectedFile && (
                <p className="file-selected-name" id="selected-file-name">
                  Selected: {selectedFile.name} ({(selectedFile.size / 1024 / 1024).toFixed(2)} MB)
                </p>
              )}
            </div>
            <div className="action-row">
              <button 
                type="submit" 
                className="primary-btn" 
                disabled={loading || !selectedFile}
              >
                {loading ? 'Analyzing Statement... Please Wait ⏳' : 'Analyze Statement'}
              </button>
            </div>
          </form>
        </div>
      </main>
    </div>
  );
};

export default Upload;
