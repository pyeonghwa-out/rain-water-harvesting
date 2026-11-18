import React from "react";
import "./RainwaterPredictor.css";
import RainwaterPredictor from "./Predictor";

const RainwaterPredictor01 = () => {
  return (
    <div className="background">
    <div className="rainwater-container">
      <div className="overlay">
        <h1 className="title">RAINWATER HARVESTING</h1>
        <h1 className="title">PREDICTOR</h1>
        <p className="subtitle">
          ENTER YOUR DETAILS AND TAKE A STEP TOWARDS PRESERVING EVERY DROP.
        </p>
      </div>
    </div>
    <RainwaterPredictor/>
    </div>
  );
};

export default RainwaterPredictor01;
