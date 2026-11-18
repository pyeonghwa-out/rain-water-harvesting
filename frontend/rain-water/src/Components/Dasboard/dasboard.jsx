import React from 'react';
import './dashboard.css';
// FaUserCircle is no longer needed, so it's removed from this import
import { FaArrowRight } from 'react-icons/fa'; 
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  LineChart, Line
} from 'recharts';

// Data for charts remains the same
const dataWaterStorage = [
  { name: 'Jan', 'Water Stored': 80 },
  { name: 'Feb', 'Water Stored': 90 },
  { name: 'Mar', 'Water Stored': 120 },
  { name: 'Apr', 'Water Stored': 150 },
  { name: 'May', 'Water Stored': 180 },
  { name: 'Jun', 'Water Stored': 130 },
  { name: 'Jul', 'Water Stored': 100 },
  { name: 'Aug', 'Water Stored': 70 },
];

const dataCostBenefits = [
  { name: 'Jan', 'Cost Benefits': 1000 },
  { name: 'Feb', 'Cost Benefits': 1200 },
  { name: 'Mar', 'Cost Benefits': 1500 },
  { name: 'Apr', 'Cost Benefits': 1300 },
  { name: 'May', 'Cost Benefits': 1800 },
  { name: 'Jun', 'Cost Benefits': 2000 },
  { name: 'Jul', 'Cost Benefits': 2500 },
  { name: 'Aug', 'Cost Benefits': 3000 },
];

const Leaderboard = () => (
  <div className="leaderboard">
    <h3> MONTHLY LEADERBOARD</h3>
    <ul>
      <li>1 Vishalbharti434 <span>100L saved</span></li>
      <li>2 Harshit454  <span>90L saved</span></li>
      <li>3 Manish087  3 <span>80L saved</span></li>
      <li>...</li>
      <li className="you-rank">97 YOU <span>65L saved</span></li>
    </ul>
  </div>
);

const TheTop3 = () => (
  <div className="the-top-3">
    <h3>THE TOP 3</h3>
    <div className="podium">
      <div className="podium-item rank-2">#2<br/>vishal</div>
      <div className="podium-item rank-1">#1<br/>Harshit</div>
      <div className="podium-item rank-3">#3<br/>Manish</div>
    </div>
  </div>
);

const MostRecentProjects = () => (
  <div className="most-recent-projects">
    <h3>MOST RECENT USER'S PROJECTS</h3>
    <ul>
      <li> Bhaskarkr432 <span>3days ago</span></li>
      <li>Rahulgupta54 <span>10 days ago</span></li>
      <li>Bhargavsing54 <span>13 days ago</span></li>
    </ul>
  </div>
);

const Dashboard = () => {

  // --- CHANGE: Added a user data object ---
  // In a real app, this would come from state management or an API call.
  const userData = {
    name: 'Deep raj Gupta',
    rank: 97,
    profileImageUrl: 'https://tse3.mm.bing.net/th/id/OIP.ml-V4ZujR8jjesv-uMtY0AHaHa?pid=Api&P=0&h=180' // Placeholder image URL
  };
  // --- END CHANGE ---

  return ( 
    <div>
       <div className='dashboard01'>
    <div className="dashboard-container">
      {/* Top Section */}
      <div className="header-grid">
        <div className="user-profile panel">
          {/* --- CHANGE: Replaced icon with an <img> tag for the profile photo --- */}
          <img 
            src={userData.profileImageUrl} 
            alt={`Profile of ${userData.name}`} 
            className="profile-picture" 
          />
          {/* --- END CHANGE --- */}

          <div className="user-info">
            {/* --- CHANGE: Used dynamic data for username and rank --- */}
            <h2>{userData.name}</h2>
            <span>Rank: {userData.rank}</span>
            {/* --- END CHANGE --- */}
          </div>
        </div>

        <div className="yearly-water-storage panel">
          <h3>YEARLY WATER STORAGE</h3>
          <p>Water Stored (in L)</p>
          <ResponsiveContainer width="100%" height={150}>
            <BarChart data={dataWaterStorage} margin={{ top: 10, right: 10, left: -25, bottom: 0 }}>
              <XAxis dataKey="name" axisLine={false} tickLine={false} />
              <YAxis axisLine={false} tickLine={false} />
              <Tooltip cursor={{ fill: 'rgba(255,255,255,0.1)' }} />
              <Bar dataKey="Water Stored" fill="#4CAF50" radius={[5, 5, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
          <p className="month-label">Month</p>
        </div>

        <div className="yearly-cost-benefits panel">
          <h3>YEARLY COST BENEFITS</h3>
          <p>Cost Benefits (in Rs )</p>
          <ResponsiveContainer width="100%" height={150}>
            <LineChart data={dataCostBenefits} margin={{ top: 10, right: 10, left: -25, bottom: 0 }}>
              <XAxis dataKey="name" axisLine={false} tickLine={false} />
              <YAxis axisLine={false} tickLine={false} />
              <Tooltip cursor={{ fill: 'rgba(255,255,255,0.1)' }} />
              <Line type="monotone" dataKey="Cost Benefits" stroke="#2196F3" strokeWidth={3} dot={false} />
            </LineChart>
          </ResponsiveContainer>
          <p className="month-label">Month</p>
        </div>
      </div>

      {/* Middle and Bottom sections remain the same... */}
      <div className="middle-grid">
        <div className="projects panel">
          <h3>PROJECTS</h3>
          <div className="project-item">
            <h4>Project A</h4>
            <p> Dimensions of rooftop: 20 meters x 15 meters</p>
            <p> Total Rooftop Area: 300 square meters</p>
            <p> Total Yearly Potential: 280,500 Liters</p>
            <p> Tank Size :-300 m² × 0.1 m (100 mm) × 0.85 = 25.5 m³ </p>
            <p> Volume in Liters: 25.5 m³ × 1000 = 25,500 Liters</p>
            <p> total cost of making:- $200</p>
            <p> Location:- 11sansad Marg, New Delhi 110 001 </p>

          </div>
          <div className="project-item">
            <h4>Project B</h4>
           <p>Dimensions of rooftop: 18 meters × 12 meters</p>
            <p>Total Rooftop Area: 216 square meters</p> 
           <p>Total Yearly Potential: 203,040 Liters</p> 
           <p>Tank Size :- 216 m² × 0.1 m (100 mm) × 0.85 = 18.36 m³</p>
            <p>Volume in Liters: 18.36 m³ × 1000 = 18,360 Liters</p>
             <p>Total cost of making: $240</p>
              <p>Location: 22 Connaught Place, New Delhi 110 001</p>
          </div>
         
        </div>

        <div className="stats panel">
          <h3>STATS</h3>
          <div className="stats-grid">
            <div className="stat-item">
              <h4>Total Water Saved</h4>
              <p>200+<span>million L</span></p>
            </div>
            <div className="stat-item">
              <h4>Total Cost Saved</h4>
              <p>200k+<span>dollars</span></p>
            </div>
            <div className="stat-item">
              <h4>Referrals Earned</h4>
              <p>20+<span>persons</span></p>
            </div>
          </div>
        </div>

        <div className="badges-certificates panel">
          <h3>BADGES & CERTIFICATES <FaArrowRight className="arrow-icon" /></h3>
          <p className="count">4</p>
          <div className="badges-display">
            <img src="https://www.alamy.com/aggregator-api/download?url=https://c8.alamy.com/comp/W7TMFN/save-the-earth-badge-environmental-conservation-concept-vector-illustration-W7TMFN.jpg" alt="Badge 1" />
            <img src="https://tse1.mm.bing.net/th/id/OIP.YnD2DobPFlqOAVy3fiAl_gHaG7?pid=Api&P=0&h=180" alt="Badge 2" />
            <img src="https://tse4.mm.bing.net/th/id/OIP.omeBHj3zThkH8R_nK_v60QHaHa?pid=Api&P=0&h=180" alt="Badge 3" />
            <div className="main-badge">
              <img src="https://www.girlguiding-anglia.org.uk/app/uploads/2023/05/8206.jpg" alt="Water Rakshak Badge" />
            </div>
          </div>
          <p className="recent-badge">Most Recent Badge<br/><span>Water Rakshak</span></p>
        </div>
      </div>

      <div className="bottom-grid">
        <Leaderboard />
        <TheTop3 />
        <MostRecentProjects />
      </div>
      </div>
      </div>

    </div>
  );
};

export default Dashboard;