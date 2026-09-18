import React, { useState, useRef } from 'react';
import { Camera, Upload, MapPin } from 'lucide-react';
import { set, get } from 'idb-keyval';

export default function HazardReportForm({ language, dict }) {
  const [status, setStatus] = useState('');
  const [file, setFile] = useState(null);
  const fileInputRef = useRef(null);

  const handleCapture = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;

    setStatus('Obtaining location...');
    
    // Get Geolocation
    const position = await new Promise((resolve, reject) => {
        if(!navigator.geolocation) return resolve({coords: {latitude: 26.0, longitude: 92.0}});
        navigator.geolocation.getCurrentPosition(resolve, () => resolve({coords: {latitude: 26.0, longitude: 92.0}}));
    });

    const report = {
      id: Date.now().toString(),
      lat: position.coords.latitude,
      lon: position.coords.longitude,
      timestamp: new Date().toISOString(),
      fileName: file.name
    };

    if (navigator.onLine) {
        setStatus('Uploading...');
        try {
            // Mock form data upload
            const formData = new FormData();
            formData.append('file', file);
            await fetch('http://localhost:8000/api/hazards/upload', {
                method: 'POST',
                headers: { 'Authorization': 'Bearer Citizen' },
                body: formData
            });
            setStatus('Report submitted successfully!');
            setFile(null);
        } catch(err) {
            await saveOffline(report);
        }
    } else {
        await saveOffline(report);
    }
  };

  const saveOffline = async (report) => {
      setStatus('Offline mode: Saving locally...');
      try {
          const existing = (await get('offline-reports')) || [];
          existing.push(report);
          await set('offline-reports', existing);
          setStatus('Saved to offline queue.');
          window.dispatchEvent(new Event('offline-report-added'));
          setFile(null);
      } catch (e) {
          setStatus('Failed to save offline.');
      }
  };

  return (
    <div className="bg-white p-4 rounded shadow">
      <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
        <MapPin className="text-red-500" size={20}/>
        {dict[language].report_hazard}
      </h3>
      
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <div 
           className="border-2 border-dashed border-slate-300 p-8 rounded-lg flex flex-col items-center justify-center cursor-pointer hover:bg-slate-50 transition"
           onClick={() => fileInputRef.current?.click()}
        >
            <Camera size={48} className="text-slate-400 mb-2"/>
            <span className="text-sm font-medium text-slate-600">
                {file ? file.name : dict[language].capture_photo}
            </span>
            <input 
                type="file" 
                accept="image/*" 
                capture="environment" 
                ref={fileInputRef} 
                className="hidden" 
                onChange={handleCapture}
            />
        </div>
        
        <button 
           type="submit" 
           disabled={!file}
           className="bg-blue-600 disabled:bg-slate-300 text-white font-bold py-2 rounded flex items-center justify-center gap-2"
        >
           <Upload size={18}/>
           {dict[language].submit}
        </button>
        
        {status && <p className="text-sm text-center text-slate-600 font-medium">{status}</p>}
      </form>
    </div>
  );
}
