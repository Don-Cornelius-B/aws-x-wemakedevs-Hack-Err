import React, { useState, useEffect } from 'react';
import { dict } from './locales/i18n';
import OfflineSyncStatus from './components/OfflineSyncStatus';
import RoleSwitcher from './components/RoleSwitcher';
import HazardReportForm from './components/HazardReportForm';
import GISRiskMap from './components/GISRiskMap';
import TriageDashboard from './components/TriageDashboard';

function App() {
  const [language, setLanguage] = useState('en');
  const [role, setRole] = useState('Citizen');
  const [corridors, setCorridors] = useState([
     { corridor_id: 'NH-29-NAGALAND', status: 'OPEN' },
     { corridor_id: 'NH-10-SIKKIM', status: 'OPEN' }
  ]);
  const [triageData, setTriageData] = useState([]);

  const fetchData = async () => {
     try {
        const res = await fetch('http://localhost:8000/api/risk/corridors');
        if(res.ok) {
           const data = await res.json();
           setCorridors(data);
        }
     } catch(e) {
        console.warn("Backend unreachable, using mock data");
     }
  };

  useEffect(() => {
     fetchData();
     
     const handleRefresh = (e) => {
        // Mock update triage based on blocked roads if we want to simulate frontend side
        // In real app, we fetch from API. We will simulate fetching here.
        fetchData();
        // Just mocking the effect of blocking for the demo
        setTriageData([
            { settlement: "Zubza", population: 5000, days_isolated: 1, ivi_score: 75.0 },
            { settlement: "Medziphema", population: 10000, days_isolated: 1, ivi_score: 55.0 }
        ]);
     };
     
     window.addEventListener('refresh-data', handleRefresh);
     return () => window.removeEventListener('refresh-data', handleRefresh);
  }, []);

  return (
    <div className="min-h-screen bg-slate-100 flex flex-col font-sans">
      <header className="bg-slate-900 text-white p-4 flex flex-col sm:flex-row gap-4 justify-between items-center shadow-lg z-20 relative">
         <div className="flex items-center gap-3">
             <div className="bg-blue-600 p-2 rounded-lg">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m8 3 4 8 5-5 5 15H2L8 3z"/></svg>
             </div>
             <h1 className="text-xl font-bold tracking-tight">{dict[language].app_title}</h1>
         </div>
         
         <div className="flex items-center gap-4">
            <OfflineSyncStatus language={language} dict={dict} />
            <select 
               value={language} 
               onChange={e => setLanguage(e.target.value)}
               className="bg-slate-800 border-none outline-none text-sm px-2 py-1 rounded text-slate-300"
            >
               <option value="en">English</option>
               <option value="as">অসমীয়া</option>
               <option value="bn">বাংলা</option>
            </select>
            <RoleSwitcher role={role} setRole={setRole} language={language} dict={dict} />
         </div>
      </header>

      <main className="flex-1 p-4 flex flex-col lg:flex-row gap-4 overflow-hidden">
         {/* Left Column - Map and Report */}
         <div className="w-full lg:w-2/3 flex flex-col gap-4">
            <div className="bg-white p-4 rounded shadow flex-1 min-h-[400px]">
               <h2 className="text-lg font-bold mb-3">{dict[language].map_view}</h2>
               <GISRiskMap corridors={corridors} language={language} role={role} />
            </div>
         </div>
         
         {/* Right Column - Forms and Dashboard */}
         <div className="w-full lg:w-1/3 flex flex-col gap-4">
            <HazardReportForm language={language} dict={dict} />
            <div className="flex-1 min-h-[300px]">
               <TriageDashboard triageData={triageData} language={language} dict={dict} />
            </div>
         </div>
      </main>
    </div>
  );
}

export default App;
