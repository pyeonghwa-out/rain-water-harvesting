import React from "react";
import "./about.css";

const AboutUs = () => {
  return (  <div>

    
   <div className="about-us-container">
      <header className="about-header">
        <h1>About Our Mission</h1>
        <h2 className="hindi-title">जल शक्ति आपके हाथों में: Your Personal Rainwater Harvesting Guide</h2>
      </header>

      <section className="intro-section">
        <div className="intro-text">
            <p>
                In regions like Delhi, and across India , water is a precious, often unpredictable resource. We face the dual challenges of intense seasonal monsoons and rapidly depleting groundwater levels. Many of us want to conserve water, but the crucial questions often stop us: <em>Is it possible at my home? What kind of system do I need? How much will it cost? Will it even make a difference?</em>
            </p>
            <p className="mission-statement">
                This platform was born to answer exactly these questions. We are a team of hydrologists, data scientists, and environmental advocates dedicated to bridging the gap between the desire to conserve water and the knowledge to do so effectively.
            </p>
            <p className="empower-statement">
                Our mission is to empower every individual, farmer, and community with clear, data-driven insights to make informed decisions about rainwater harvesting and groundwater recharge.
            </p>
        </div>
        <div className="intro-image-container">
            
            <img src="https://infinitylearn.com/surge/wp-content/uploads/2024/01/average-annual-rainfall-of-india.jpeg" alt="Data visualization of water levels" />
        </div>
      </section>

      <section className="how-it-works-section">
        <h3>How Our Tool Empowers You</h3>
        <p className="section-subtitle">
            This isn't just a website; it's a powerful decision-making tool that puts complex hydrological data at your fingertips, presented in a simple and actionable format. Here’s what our platform does for you:
        </p>
        <ul className="features-list">
          <li><strong>💧 Instantly Checks Feasibility:</strong> Enter your location, and we'll instantly analyze if your rooftop is suitable for rainwater harvesting.</li>
          <li><strong>⚙️ Provides Tailored Recommendations:</strong> We don't give generic advice. Based on your specific location and needs, the tool suggests the most effective type of structure, whether it's a recharge pit, trench, or shaft.</li>
          <li><strong>📊 Offers Hyperlocal Data:</strong> Access critical information for your area, including the principal aquifer, groundwater depth, and local rainfall data.</li>
          <li><strong>📐 Delivers Precise Planning & Costing:</strong> Get recommended dimensions for your recharge structure and a clear, transparent cost-benefit analysis.</li>
        </ul>
      </section>
      
      <section className="vision-section">
        <h3>Our Vision: A Water-Secure Future</h3>
        <p className="section-subtitle">
            We believe that sustainable water management starts from the ground up—literally. By providing accessible, reliable, and localized information, we aim to spark a grassroots movement of water conservation. Our vision is a future where:
        </p>
        <ul className="vision-list">
            <li>Informed citizens are the primary drivers of groundwater conservation.</li>
            <li>Communities thrive with a secure and sustainable water source.</li>
            <li>Rainwater is seen not as a problem, but as the most valuable resource it is.</li>
        </ul>
      </section>
      
      <section className="language-section">
        <h3>Accessible to All (भाषा सबके लिए)</h3>
        <p>
            Knowledge should have no language barrier. We are committed to inclusivity, which is why our tool is available in regional languages, ensuring everyone can participate in securing our shared water future.
        </p>
      </section>

      <section className="cta-section">
        <h4>Ready to make an impact?</h4>
        <p>Let's start by understanding the potential right under your roof.</p>
        <button className="cta-button">
          Analyze Your Property's Potential
        </button>
      </section>

    </div>
     </div>
  );
};

export default AboutUs;
