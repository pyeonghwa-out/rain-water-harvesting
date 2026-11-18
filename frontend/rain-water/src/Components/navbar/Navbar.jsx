// components/Navbar.jsx

import React, { useEffect, useState } from 'react';
import './Navbar.css';
import logo from "../../assets/navbar.png";
import menu_icon from "../../assets/menu.png";
import { Link } from 'react-router-dom';
import { useUser, UserButton, SignIn, SignUp } from '@clerk/clerk-react'; 

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
          // Container styling is correct to ensure visibility and size
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

const Navbar = () => {
  const [sticky, setSticky] = useState(false);
  const [mobileMenu, setMobileMenu] = useState(false);
  
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [modalContent, setModalContent] = useState('login'); 

  const { user } = useUser();

  useEffect(() => {
    const handleScroll = () => {
        setSticky(window.scrollY > 50);
    };
    window.addEventListener('scroll', handleScroll);

    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const toggleMenu = () => setMobileMenu(!mobileMenu);
  
  const openModal = (content) => {
    setModalContent(content);
    setIsModalOpen(true);
  };
  
  const closeModal = () => {
    setIsModalOpen(false);
  };

  return (
    <nav className={sticky ? 'dark-nav' : ''}>
      <div className="nav-logo">
        <Link to="/">
          <img src={logo} alt="logo" className="logo" />
        </Link>
      </div>

      <ul className={mobileMenu ? '' : 'hide-mobile-menu'}>
        <div>
          <Link to="/"><li>HOME</li></Link>
          <Link to="/guide"><li>GUIDELINES</li></Link>
          <Link to="/about"><li>ABOUT</li></Link>
          <Link to="/predictor"><li>PREDICTOR</li></Link>
          <Link to="/dashboard"><li>DASHBOARD</li></Link>
          <Link to="/contact"><li>CONTACT US</li></Link>
        </div>
      </ul>

      <div className="nav-auth">
        {!user ? (
          <>
            <button className='nav-link-button' onClick={() => openModal('login')}>LOGIN</button> 
            <button className='nav-link-button' onClick={() => openModal('signup')}>SIGNUP</button>
          </>
        ) : (
          <UserButton />
        )}
      </div>

      <img src={menu_icon} alt="" className="menu-icon" onClick={toggleMenu} />
      
      <Modal isOpen={isModalOpen} onClose={closeModal}>
        {modalContent === 'login' ? (
          // 🔑 FIX APPLIED: Removed routing="path" and path="/login"
          <SignIn afterSignInUrl="/" /> 
        ) : (
          // 🔑 FIX APPLIED: Removed routing="path" and path="/signup"
          <SignUp afterSignUpUrl="/" />
        )}
      </Modal>
    </nav>
  );
};

export default Navbar;