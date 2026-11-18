import React from "react";
import "./Footer.css";

const Footer = () => {
  return (
    <footer className="footer">
      <div className="footer-left">
        <p>© 2025 Zenkai. All rights reserved.</p>
      </div>
      <div className="footer-right">
        <ul>
          <li><a href="#">Privacy Policy</a></li>
          <li><a href="#">Terms of Services</a></li>
          <li><a href="#">Code of Conduct</a></li>
        </ul>
      </div>
    </footer>
  );
};

export default Footer;
