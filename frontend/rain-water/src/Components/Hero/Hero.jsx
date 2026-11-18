import React from "react";
import "./Hero.css";
import Predictor from "./Hero1";
import Hero1 from "./Hero1";
import Hero2 from "./Hero2";
import { Link } from "react-router-dom";


const Hero = () => {
  return (
    <div className="backgrounda">
    <div className="background">
    <section className="hero">
      <div className="raindrops">
        {Array.from({ length: 80 }).map((_, i) => (
          <span key={i} style={{ '--i': i }} />
        ))}
      </div>
      <div className="hero-content">
        <h1  >REIMAGINE RAINWATER</h1>
        <p>
          EVERY DROP COUNTS, ASSESS YOUR ROOFTOP RAINWATER HARVESTING POTENTIAL
          TODAY.
        </p>
        
        <Link to="/predictor"><button className="btn">Predict Now</button></Link>
      </div>
    </section>
    <Hero1/>
    <Hero2/>
    </div>
    </div>
    
  );
};

export default Hero;
