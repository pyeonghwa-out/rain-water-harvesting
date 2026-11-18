import React, { useState } from "react";
import "./Hero2.css";
import dropImage from "../../assets/rain.png"; // import from assets
// 🔑 Import necessary Clerk components
import { useUser, SignIn, SignUp } from '@clerk/clerk-react'; 

// --- 1. MODAL COMPONENT ---
// This is required to show the form as a pop-up overlay.
const Modal = ({ isOpen, onClose, children }) => {
  if (!isOpen) return null;

  return (
    <div 
      style={{
        position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.6)', 
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        zIndex: 1000 
      }}
      onClick={onClose} 
    >
      <div 
        onClick={e => e.stopPropagation()} 
        style={{ 
          backgroundColor: 'white', 
          padding: '20px', 
          borderRadius: '8px', 
          minWidth: '350px', 
          minHeight: '400px', 
          maxWidth: '90%', 
          maxHeight: '90%', 
          overflowY: 'auto',
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
        }}
      >
        {children}
      </div>
    </div>
  );
};

// --- 2. HERO2 COMPONENT (Updated) ---
const Hero2 = () => {
  // 🔑 Get both isLoaded and isSignedIn state
  const { isLoaded, isSignedIn } = useUser();
  
  // State for controlling the modal visibility and content
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [modalContent, setModalContent] = useState('login'); 
  
  const openModal = (content) => {
    setModalContent(content);
    setIsModalOpen(true);
  };
  
  const closeModal = () => {
    setIsModalOpen(false);
  };

  // If Clerk is not yet loaded, return null or a simple spinner to prevent flickering
  if (!isLoaded) return null;

  return (
    <section className="account">
      <div className="account-container">
        {/* Left Side - Image */}
        <div className="account-image">
          <img src={dropImage} alt="Earth in water drop" />
        </div>

        {/* Right Side - Content */}
        <div className="account-content">
          <p className="subtitle">READY TO BEGIN?</p>
          <h1>CREATE YOUR ACCOUNT</h1>
          <p className="description">
            Join our community and take the first step towards sustainable water
            management. With your account, you’ll be able to:
          </p>
          <ul>
            <li>Estimate your rainwater harvesting potential</li>
            <li>Save your predictions and reports</li>
            <li>Earn badges & certificates</li>
            <li>Compete on the leaderboard</li>
          </ul>
          
          {/* 🔑 FIX: Add buttons only if the user is NOT signed in */}
          {!isSignedIn && (
            <div className="buttons">
              <button 
                className="btn login" 
                onClick={() => openModal('login')} // 🔑 Open login modal
              >
                Login
              </button>
              <button 
                className="btn signup" 
                onClick={() => openModal('signup')} // 🔑 Open signup modal
              >
                Signup
              </button>
            </div>
          )}
        </div>
      </div>
      
      {/* 🔑 Render the Modal outside of the main section content */}
      <Modal isOpen={isModalOpen} onClose={closeModal}>
        {modalContent === 'login' ? (
          <SignIn afterSignInUrl="/" /> 
        ) : (
          <SignUp afterSignUpUrl="/" />
        )}
      </Modal>
    </section>
  );
};

export default Hero2;
