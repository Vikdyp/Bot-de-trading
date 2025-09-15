'use client';
import React from 'react';
import { api } from '@/lib/api';
import { PositionsTable } from '../components/PositionsTable';

export default function PositionsPage(){
  const [rows, setRows] = React.useState<any[]>([]);
  const refresh = async ()=> setRows(await api.positions());
  React.useEffect(()=>{ refresh(); const id=setInterval(refresh, 8000); return ()=>clearInterval(id); },[]);
  return (
    <div className="container">
      <div className="card"><h3>Positions</h3><div className="sub">Live/paper positions</div></div>
      <div style={{marginTop:16}}>
        <PositionsTable rows={rows} onClose={async (sym)=>{await api.paperClose(sym); await refresh();}}/>
      </div>
    </div>
  );
}
