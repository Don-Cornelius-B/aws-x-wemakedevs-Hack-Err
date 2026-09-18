import React from 'react';
import { Shield } from 'lucide-react';

export default function RoleSwitcher({ role, setRole, language, dict }) {
  return (
    <div className="flex items-center gap-2 bg-slate-800 rounded px-3 py-1 text-sm text-slate-200">
      <Shield size={16} className="text-blue-400" />
      <select 
         value={role} 
         onChange={(e) => setRole(e.target.value)}
         className="bg-transparent outline-none cursor-pointer"
      >
         <option value="Citizen" className="text-black">{dict[language].role_citizen}</option>
         <option value="FieldInspector" className="text-black">{dict[language].role_inspector}</option>
         <option value="DistrictOfficer" className="text-black">{dict[language].role_officer}</option>
      </select>
    </div>
  );
}
