'use client';
import React from 'react';
import { api } from '@/lib/api';

export default function StatusBar(){
  const [status, setStatus] = React.useState<string>('...');
  const [version, setVersion] = React.useState<string>('');

  const refresh = async ()=>{
    try{
      const h = await api.health();
      setStatus(h.status); setVersion(h.version);
    }catch(e){ setStatus('down'); }
  };
  React.useEffect(()=>{ refresh(); const id=setInterval(refresh,8000); return ()=>clearInterval(id); },[]);
  const ok = status==='ok';
  return (
    <div className="card" style={{display:'flex',justifyContent:'space-between',alignItems:'center'}}>
      <div><b>Status API:</b> <span className={ok?'kpi-up':'kpi-down'}>{status}</span> <span className="sub">v{version}</span></div>
      <button className="btn" onClick={refresh}>Refresh</button>
    </div>
  );
}
