import React, { useState } from "react";
import "./main1.css";
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';

// 🔑 Import Clerk components
import { SignIn, SignUp } from '@clerk/clerk-react';

// --- MODAL COMPONENT ---
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

function RainwaterPredictor() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [modalContent] = useState('login');

  const [formData, setFormData] = useState({
    latitude: "",
    longitude: "",
    rooftopArea: "",
    openGroundArea: "",
    roofType: "Concrete",
    household: "",
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [isDownloading, setIsDownloading] = useState(false);

  const closeModal = () => {
    setIsModalOpen(false);
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const runPrediction = async () => {
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const requestBody = {
        lat: parseFloat(formData.latitude),
        lon: parseFloat(formData.longitude),
        rooftop_area_m2: formData.rooftopArea ? parseFloat(formData.rooftopArea) : null,
        open_area_m2: parseFloat(formData.openGroundArea),
        roof_type: formData.roofType,
        num_persons: parseInt(formData.household),
      };

      const response = await fetch("http://127.0.0.1:8000/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        throw new Error("Failed to fetch prediction. Please check inputs.");
      }

      const data = await response.json();

      console.log("Raw API Response Data:", data);

      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    // if (!isSignedIn) {
    //   openModal('login');
    //   return;
    // }

    runPrediction();
  };

  const handleDownloadPdf = () => {
    const input = document.getElementById('result-panel-to-download');
    if (!input) {
      console.error("Error: Could not find element with id 'result-panel-to-download'");
      setError("Could not generate PDF: Target element not found.");
      return;
    }
    console.log("Starting PDF generation for element:", input);
    setIsDownloading(true);

    html2canvas(input, { scale: 2, useCORS: true, allowTaint: true })
      .then((canvas) => {
        const imgData = canvas.toDataURL('image/png');
        const pdf = new jsPDF('p', 'mm', 'a4');
        const pdfWidth = pdf.internal.pageSize.getWidth();
        const canvasAspectRatio = canvas.width / canvas.height;
        const imgHeightInPdf = pdfWidth / canvasAspectRatio;

        pdf.addImage(imgData, 'PNG', 0, 0, pdfWidth, imgHeightInPdf);
        pdf.save("rainwater-harvesting-prediction.pdf");
      })
      .catch((err) => {
        console.error("Error generating PDF canvas:", err);
        setError("An error occurred while generating the PDF. Please check the console.");
      })
      .finally(() => {
        setIsDownloading(false);
      });
  };

  const formatInr = (num) => {
    if (num === null || num === undefined || isNaN(Number(num))) return String(num);
    try {
      return new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(Number(num));
    } catch {
      return `₹${Number(num).toLocaleString("en-IN")}`;
    }
  };

  const formatKey = (key) => {
    return key
      .replace(/_/g, ' ')
      .replace(/\b\w/g, l => l.toUpperCase())
      .replace(/\b(Mbgl|Lps|L)\b/g, match => match.toUpperCase())
      .replace(/\b(Lat|Lon|Long)\b/g, match => match === 'Long' ? 'Longitude' : match === 'Lat' ? 'Latitude' : match);
  };

  const formatStructureName = (structure) => {
    if (!structure) return structure;
    return structure
      .replace(/_/g, ' ')
      .replace(/\b\w/g, l => l.toUpperCase())
      .replace(/\bOn\b/g, 'on')
      .replace(/\bOr\b/g, 'or');
  };

  const formatExplanation = (explanation) => {
    if (!explanation) return explanation;
    return explanation
      .replace(/L\b/g, ' liters')
      .replace(/>=/g, '≥')
      .replace(/annual harvest/g, 'Annual harvest')
      .replace(/demand/g, 'demand');
  };

  const renderKeyValueGrid = (obj) => {
    if (!obj) return null;
    return (
      <div className="kv-grid">
        {Object.entries(obj).map(([k, v]) => (
          <div className="kv-item" key={k}>
            <div className="kv-key">{formatKey(k)}</div>
            <div className="kv-val">{typeof v === "number" ? v : String(v)}</div>
          </div>
        ))}
      </div>
    );
  };

  // 🔑 FINAL FIX: Filter function for Nearest Well Record using combined Python/DB keys
  const filterWellRecord = (record) => {
    if (!record) return null;

    const filteredRecord = {};

    // 1. Latitude and Longitude (Keys are Capitalized/No Space)
    const latValue = record.Latitude || record.coordinates?.lat || record.latitude;
    const lonValue = record.Longitude || record.coordinates?.lon || record.longitude;

    if (latValue !== undefined && latValue !== null) {
        filteredRecord['Latitude'] = latValue;
    }
    if (lonValue !== undefined && lonValue !== null) {
        filteredRecord['Longitude'] = lonValue;
    }

    // 2. Distance Km (KEY: _distance_km or Distance Km)
    const distanceValue = record._distance_km || record['Distance Km'] || record.Distance_Km || record.distance_km;
    if (distanceValue !== undefined && distanceValue !== null) {
        // FIX: Ensure Number conversion for rounding
        filteredRecord['Distance Km'] = Number(distanceValue).toFixed(2);
    }

    // 3. Source (KEY: Source)
    const sourceValue = record.Source || record.source;
    if (sourceValue !== undefined && sourceValue !== null) {
        filteredRecord['Source'] = sourceValue;
    }

    // 4. Mean Annual Rainfall (KEY: mean_annual_rainfall)
    const rainfallValue = record.mean_annual_rainfall || record['Mean Annual Rainfall'];
    if (rainfallValue !== undefined && rainfallValue !== null) {
        // FIX: Ensure Number conversion for rounding
        filteredRecord['Mean Annual Rainfall'] = Number(rainfallValue).toFixed(2);
    }

    // 5. Soil Type (KEY: soil_type)
    const soilTypeValue = record.soil_type || record['Soil Type'];
    if (soilTypeValue !== undefined && soilTypeValue !== null) {
        filteredRecord['Soil Type'] = soilTypeValue;
    }

    // This ensures only the 6 defined fields are returned.
    return filteredRecord;
  };


  return (
    <div style={{minHeight: '100vh', display: 'flex', flexDirection: 'column'}}>
      {/* 🔑 Content Wrapper Div for padding */}
      <div className="main-content-wrapper" style={{flexGrow: 1, paddingBottom: '3rem'}}>
        <div className="landing">
          <div className="overlay">
            <h1 className="title">RAINWATER HARVESTING PREDICTOR</h1>
            <p className="subtitle">
              Enter your location and basic details to get water harvesting prediction
            </p>

            <form className="form-box" onSubmit={handleSubmit}>
              <h2>Enter Your Details</h2>
              <div className="input-grid">
                <input
                  type="text"
                  name="latitude"
                  placeholder="Enter Location Latitude"
                  value={formData.latitude}
                  onChange={handleChange}
                  required
                />
                <input
                  type="text"
                  name="longitude"
                  placeholder="Enter Location Longitude"
                  value={formData.longitude}
                  onChange={handleChange}
                  required
                />
                <input
                  type="number"
                  name="rooftopArea"
                  placeholder="Enter Rooftop Area (sq.m) - Optional (auto-detected if empty)"
                  value={formData.rooftopArea}
                  onChange={handleChange}
                />
                <input
                  type="number"
                  name="openGroundArea"
                  placeholder="Enter Open Ground Area (sq.m)"
                  value={formData.openGroundArea}
                  onChange={handleChange}
                  required
                />
                <select
                  name="roofType"
                  value={formData.roofType}
                  onChange={handleChange}
                >
                  <option value="Concrete">Concrete (Default)</option>
                  <option value="Tin">Tin</option>
                  <option value="Thatch">Thatch</option>
                </select>
                <input
                  type="number"
                  name="household"
                  placeholder="Enter No. of People in Household"
                  value={formData.household}
                  onChange={handleChange}
                  required
                />
              </div>
              <button type="submit" className="btn" disabled={loading}>
                {loading ? "Predicting..." : "Predict Now"}
              </button>
            </form>

            {error && <p className="error">{error}</p>}

            {/* --- Prediction Results Section --- */}
            {result && (
              <div id="result-panel-to-download" className="result-panel">
                <div className="result-header">
                  <div className="pill">
                    {formatStructureName(result.predicted_structure) || "Structure"}
                  </div>
                  {result.explanation && (
                    <div className="badge">{formatExplanation(result.explanation)}</div>
                  )}
                </div>

                {/* 1. Recommended Dimensions (Keep as is) */}
                {result.predicted_dimensions && (
                  <div className="section">
                    <h3 className="section-title">Recommended Dimensions</h3>
                    <div className="cards-grid">
                      {Object.entries(result.predicted_dimensions).map(([k, v]) => (
                        <div className="card" key={k}>
                          <div className="card-key">{formatKey(k)}</div>
                          <div className="card-val">
                            {typeof v === "number" ? v.toFixed(2) : String(v)}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* 2. Cost Estimate (Filtered) */}
                {result.cost_estimate && (
                  <div className="section">
                    <h3 className="section-title">Cost Estimate</h3>
                    <div className="cards-grid">
                      {/* Only display Total Cost Card */}
                      <div className="card highlight">
                        <div className="card-key">Total Cost</div>
                        <div className="card-val">{formatInr(result.cost_estimate.total_cost_inr)}</div>
                      </div>
                    </div>


                    {Array.isArray(result.cost_estimate.breakdown) && result.cost_estimate.breakdown.length > 0 && (
                      <div className="subsection">
                        <h4 className="subsection-title">Breakdown of Cost</h4>
                        <div className="table">
                          <div className="table-row table-header">
                            <div>Item</div>
                            <div>Qty</div>
                            <div>Rate</div>
                            <div>Cost</div>
                          </div>
                          {result.cost_estimate.breakdown.map((row, idx) => (
                            <div className="table-row" key={idx}>
                              <div>{formatKey(row.item)}</div>
                              <div>{row.qty}</div>
                              <div>{row.rate}</div>
                              <div>{formatInr(row.cost_inr)}</div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}


                    {Array.isArray(result.cost_estimate.assumptions) && result.cost_estimate.assumptions.length > 0 && (
                      <div className="subsection">
                        <h4 className="subsection-title">Assumptions</h4>
                        <ul className="assumptions">
                          {result.cost_estimate.assumptions.map((a, i) => (
                            <li key={i}>{a}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}

                {result.rooftop_detection && (
                  <div className="section">
                    <h3 className="section-title">Rooftop Detection</h3>
                    <div className="rooftop-detection">
                      <div className="detection-info">
                        <div className="info-item">
                          <span className="info-label">Detected Area:</span>
                          <span className="info-value">{(result.rooftop_detection.detected_area_m2).toFixed(2)} m²</span>
                        </div>
                        <div className="info-item">
                          <span className="info-label">Coordinates:</span>
                          <span className="info-value">
                            {result.rooftop_detection.coordinates?.lat}, {result.rooftop_detection.coordinates?.lon}
                          </span>
                        </div>
                      </div>
                      {result.rooftop_detection.detection_image && (
                        <div className="detection-image-container">
                          <h4 className="subsection-title">Detected Rooftop Area</h4>
                          <img
                            src={result.rooftop_detection.detection_image}
                            alt="Detected rooftop area"
                            className="detection-image"
                          />
                          <p className="image-caption">
                            Blue highlighted area shows the detected rooftop for rainwater harvesting
                          </p>
                        </div>
                      )}
                    </div>
                  </div>
                )}


                {result.nearest_well_record && (
                  <div className="section">
                    <h3 className="section-title">Nearest Well Record Used</h3>
                    {/* Render the filtered data */}
                    {renderKeyValueGrid(filterWellRecord(result.nearest_well_record))}
                  </div>
                )}
              </div>
            )}
            {/* --- END Prediction Results Section --- */}

            {result && (
              <div className="download-button-container">
                <button
                  onClick={handleDownloadPdf}
                  className="btn download-btn"
                  disabled={isDownloading}
                >
                  {isDownloading ? "Downloading..." : "Download Results as PDF"}
                </button>
              </div>
            )}

          </div>
        </div>
      </div>

      <Modal isOpen={isModalOpen} onClose={closeModal}>
        {modalContent === 'login' ? (
          <SignIn afterSignInUrl={window.location.pathname} />
        ) : (
          <SignUp afterSignUpUrl={window.location.pathname} />
        )}
      </Modal>
    </div>
  );
}

export default RainwaterPredictor;
