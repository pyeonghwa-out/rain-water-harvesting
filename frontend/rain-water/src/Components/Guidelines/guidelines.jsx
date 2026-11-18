import React from 'react'
import './guideline.css'

const Introduction = () => {
  return (
    <div>
    <div className='hello1'>
    <main className="guide-container">
      <header className="guide-header">
        <h1>Harnessing the Monsoon: A Comprehensive Guide to Rainwater Harvesting in India</h1>
        <p className="subtitle">Govt of India – A crucial solution for a sustainable water future.</p>
      </header>

      <section className="guide-section">
        <h2>Why Rainwater Harvesting is a Necessity for India</h2>
        <p>
          India's geographical and climatic diversity presents both opportunities and challenges for water management. Rainwater harvesting offers a decentralized approach to water conservation with numerous benefits:
        </p>
        <ul>
          <li><strong>Combating Water Scarcity:</strong> Provides a supplementary water source, reducing reliance on over-exploited groundwater and municipal supplies.</li>
          <li><strong>Groundwater Recharge:</strong> Helps replenish depleted aquifers by directing rainwater into recharge pits, borewells, and trenches.</li>
          <li><strong>Flood Mitigation:</strong> Collecting rooftop runoff can significantly reduce stormwater volume, mitigating urban flooding.</li>
          <li><strong>Improved Water Quality:</strong> Rainwater is naturally soft and low in minerals, making it suitable for various uses with basic filtration.</li>
          <li><strong>Reduced Soil Erosion:</strong> Techniques like contour bunding and check dams slow down surface runoff, preventing soil erosion.</li>
          <li><strong>Cost-Effective and Energy-Saving:</strong> Reduces electricity consumption from pumping groundwater and dependency on expensive water tankers.</li>
        </ul>
      </section>

      <hr />

      <section className="guide-section">
        <h2>Planning and Designing Your System</h2>
        <p>A well-designed system is crucial for effectiveness, depending on rainfall, catchment area, and intended water use.</p>

        <h3>Key Steps in Planning:</h3>
        <ol>
          <li><strong>Assess Water Requirement:</strong> Determine your daily or seasonal needs for non-potable uses.</li>
          <li><strong>Calculate Potential Harvest:</strong> Use the formula to estimate the amount of water you can collect.</li>
          <li className="formula-box">
            Harvestable Rainwater (litres) = Rainfall (mm) &times; Catchment Area (sq. m.) &times; Runoff Coefficient
          </li>
          <li><strong>Select a Suitable Technique:</strong> Choose a harvesting method based on your needs and available space.</li>
        </ol>

        <h3>Essential Components of a Rooftop System:</h3>
        <ul>
            <li><strong>Catchment Area:</strong> A clean roof made of non-toxic material.</li>
            <li><strong>Gutters and Downpipes:</strong> Channels to transport rainwater.</li>
            <li><strong>First-Flush Diverter:</strong> A device to divert the initial, contaminated rainwater.</li>
            <li><strong>Filter:</strong> A system (e.g., sand, charcoal) to remove pollutants.</li>
            <li><strong>Storage Tank:</strong> A sump or tank to store filtered water.</li>
            <li><strong>Recharge Structure (Optional):</strong> Pits or trenches for groundwater replenishment.</li>
        </ul>
      </section>

      <hr />

      <section className="guide-section">
        <h2>A Step-by-Step Guide to Installation</h2>
        <ol>
            <li><strong>Prepare the Catchment:</strong> Clean the roof thoroughly.</li>
            <li><strong>Install Gutters and Downpipes:</strong> Fix channels along the roof edges.</li>
            <li><strong>Set Up the First-Flush Diverter:</strong> Install it before the filter.</li>
            <li><strong>Construct the Filtration Unit:</strong> Build or install a pre-fabricated filter.</li>
            <li><strong>Connect to Storage or Recharge:</strong> Direct the clean water to the tank or recharge pit.</li>
            <li><strong>Ensure Proper Overflow:</strong> The storage tank must have an overflow pipe.</li>
        </ol>
      </section>

      <hr />

      <section className="guide-section">
        <h2>Maintaining Your System</h2>
        <p>Regular maintenance is essential for the longevity and efficiency of the system.</p>
        <div className="table-container">
            <table>
            <thead>
                <tr>
                <th>Frequency</th>
                <th>Maintenance Task</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                <td><strong>Before the Monsoon</strong></td>
                <td>Clean the rooftop, gutters, and downpipes. Clean or replace filter media. Inspect the storage tank for leaks.</td>
                </tr>
                <tr>
                <td><strong>During the Monsoon</strong></td>
                <td>Regularly check and clear blockages. Ensure the first-flush diverter is functioning correctly.</td>
                </tr>
                <tr>
                <td><strong>After the Monsoon</strong></td>
                <td>Clean the entire system. Drain and clean the storage tank if necessary.</td>
                </tr>
            </tbody>
            </table>
        </div>
      </section>

      <hr />

      <section className="guide-section">
        <h2>Government Support and Financial Assistance</h2>
        <p>The Government of India and various state governments actively promote rainwater harvesting through schemes and subsidies.</p>
        <ul>
            <li><strong>National Level Schemes:</strong> The Jal Shakti Abhiyan and Atal Bhujal Yojana (ATAL JAL) provide financial and technical support.</li>
            <li><strong>State-Level Subsidies:</strong> Many states offer subsidies on installation costs and rebates on property tax.</li>
            <li><strong>Mandatory Provisions:</strong> Several states have made rainwater harvesting mandatory for new buildings. Check local bye-laws for requirements.</li>
        </ul>
      </section>

      <hr />

      <footer className="guide-footer">
        <h3>A Sustainable Path Forward 🌏</h3>
        <p>Rainwater harvesting is more than just a technique; it is a commitment to a sustainable and water-secure future for India. By embracing this simple yet powerful practice, every citizen can contribute to conserving this precious natural resource.</p>
      </footer>
    </main>
    </div>
    </div>
  );
};

export default Introduction;