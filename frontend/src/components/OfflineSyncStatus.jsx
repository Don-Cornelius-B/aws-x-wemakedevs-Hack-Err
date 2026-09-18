import React, { useState, useEffect } from 'react';
import { Cloud, CloudOff, RefreshCw } from 'lucide-react';
import { get, set } from 'idb-keyval';

export default function OfflineSyncStatus({ language, dict }) {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [pendingCount, setPendingCount] = useState(0);

  const checkPending = async () => {
    try {
      const reports = (await get('offline-reports')) || [];
      setPendingCount(reports.length);
    } catch(e) {}
  };

  useEffect(() => {
    checkPending();
    
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);
    
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    window.addEventListener('offline-report-added', checkPending);
    
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
      window.removeEventListener('offline-report-added', checkPending);
    };
  }, []);

  const handleSync = async () => {
      if (!isOnline) return;
      try {
          const reports = (await get('offline-reports')) || [];
          if(reports.length === 0) return;
          
          await fetch('http://localhost:8000/api/sync/push', {
              method: 'POST',
              headers: {'Content-Type': 'application/json', 'Authorization': 'Bearer Citizen'},
              body: JSON.stringify(reports)
          });
          await set('offline-reports', []);
          setPendingCount(0);
      } catch (err) {
          console.error("Sync failed", err);
      }
  };

  return (
    <div className={`flex items-center gap-3 px-3 py-1.5 rounded-full text-sm font-medium ${isOnline ? 'bg-green-100 text-green-800' : 'bg-slate-100 text-slate-600'}`}>
       {isOnline ? <Cloud size={16}/> : <CloudOff size={16}/>}
       <span>{isOnline ? dict[language].sync_online : dict[language].sync_offline}</span>
       
       {pendingCount > 0 && (
          <div className="flex items-center gap-2 border-l border-current pl-3 ml-1">
             <span className="bg-red-500 text-white text-xs px-2 rounded-full">{pendingCount}</span>
             <button onClick={handleSync} disabled={!isOnline} className="flex items-center hover:opacity-75 disabled:opacity-50">
                 <RefreshCw size={14} className={isOnline ? 'animate-spin-hover' : ''}/>
             </button>
          </div>
       )}
    </div>
  );
}
