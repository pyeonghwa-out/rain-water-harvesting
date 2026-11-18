import React, { useState, useEffect } from "react";
import "./Hero1.css";
import img1 from "../../assets/rain1.png"
import img2 from "../../assets/rain2.png"
import img3 from "../../assets/rain3.png"
import img4 from "../../assets/rain4.png"



const images = [
  img1,
  img2,
  img3,
  img4
];

const Hero1 = () => {
  const [currentIndex, setCurrentIndex] = useState(0);

  // Auto-rotate every 3 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      nextSlide();
    }, 3000);
    return () => clearInterval(interval);
  }, [currentIndex]);

  const nextSlide = () => {
    setCurrentIndex((prev) => (prev + 1) % images.length);
  };

  const prevSlide = () => {
    setCurrentIndex((prev) => (prev - 1 + images.length) % images.length);
  };

  return (
    <div className="predictor-container">
      {/* LEFT SIDE: Image Slider */}
      <div className="slider-container">
        <button className="slider-btn left" onClick={prevSlide}>
          ❮
        </button>

        <div className="slider-image">
          <img src={images[currentIndex]} alt="Rainwater" />
        </div>

        <button className="slider-btn right" onClick={nextSlide}>
          ❯
        </button>

       

        {/* Dots indicator */}
        <div className="slider-dots">
          {images.map((_, idx) => (
            <span
              key={idx}
              className={`dot ${idx === currentIndex ? "active" : ""}`}
              onClick={() => setCurrentIndex(idx)}
            ></span>
          ))}
        </div>
      </div>

      {/* RIGHT SIDE: Text Content */}
      <div className="predictor-text">
        <h4 className="predictor-subtitle">WHAT IS THIS PREDICTOR?</h4>
        <h2 className="predictor-title">RAINWATER HARVESTING PREDICTOR</h2>
        <p className="predictor-description">
          Welcome to the Rainwater Harvesting Predictor Platform, your gateway
          tool that offers the flexibility to quickly visualize rainwater
          harvesting for your location.
          <br />
          <br />
          This platform encompasses:
        </p>
        <ul className="predictor-list">
          <li>Real-time rainwater prediction</li>
          <li>Personalized rainwater harvesting suggestions</li>
          <li>Enhanced AI-integrated predictions</li>
          <li>Integration of topography & housing</li>
        </ul>
        <p className="predictor-footer">
          Start now to simulate accurate RAINING with your home.
        </p>
      </div>
      
    </div>
  );
};

export default Hero1;
