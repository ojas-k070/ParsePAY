import React from 'react';

const SupportPopup = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
    <div className="popup-overlay" style={{ display: 'flex' }} onClick={onClose}>
      <div className="popup-content glass" onClick={(e) => e.stopPropagation()}>
        <button className="close-btn" onClick={onClose}>×</button>
        <h2>Support Details</h2>
        <div className="support-info">
          <p><strong>Developer:</strong> Ojas Kulkarni</p>
          <p><strong>Email:</strong> ojas.kulkarni241@vit.edu</p>
          <p><strong>Phone:</strong> 7558774626</p>
        </div>
      </div>
    </div>
  );
};

export default SupportPopup;
