import React from 'react';
import { AlertTriangle, Users, Clock } from 'lucide-react';

export default function TriageDashboard({ triageData, language, dict }) {
  if (!triageData || triageData.length === 0) {
      return (
         <div className="bg-white p-4 rounded shadow h-full">
            <h3 className="text-lg font-bold mb-4">{dict[language].triage_dashboard}</h3>
            <p className="text-slate-500 text-sm">No isolated settlements detected.</p>
         </div>
      );
  }

  return (
    <div className="bg-white rounded shadow h-full flex flex-col">
      <div className="p-4 border-b border-slate-100 bg-red-50 rounded-t">
         <h3 className="text-lg font-bold text-red-800 flex items-center gap-2">
           <AlertTriangle size={20}/>
           {dict[language].isolated_settlements}
         </h3>
      </div>
      
      <div className="flex-1 overflow-auto p-4 flex flex-col gap-3">
         {triageData.map((item, idx) => (
             <div key={idx} className="border border-red-200 rounded p-3 bg-white shadow-sm flex flex-col gap-2">
                <div className="flex justify-between items-center">
                   <span className="font-bold text-slate-800 text-lg">{item.settlement}</span>
                   <span className="bg-red-100 text-red-800 text-xs font-bold px-2 py-1 rounded uppercase">
                      {dict[language].priority} {idx + 1} (IVI: {item.ivi_score})
                   </span>
                </div>
                
                <div className="flex gap-4 text-sm text-slate-600">
                   <div className="flex items-center gap-1">
                      <Users size={14}/> {item.population.toLocaleString()} {dict[language].pop_affected}
                   </div>
                   <div className="flex items-center gap-1">
                      <Clock size={14}/> {item.days_isolated} {dict[language].days_isolated}
                   </div>
                </div>
             </div>
         ))}
      </div>
    </div>
  );
}
