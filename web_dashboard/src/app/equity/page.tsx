'use client';
import React from 'react';
import { LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { api } from '@/lib/api';

export default function EquityPage(){
  const [data, setData] = React.useState<{t:string; nav:number}[]>([]);
  const load = async ()=>{
    // Si tu ajoutes /equity_curve côté API, remplace par api.equity() etc.
    // En attendant: on reconstruit depuis /metrics (si equity_curve y est)
    const m = await api.metrics();
    const arr = (m?.equity_curve || []).map((d:any)=>({ t: d.t, nav: Number(d.equity) }));
    setData(arr);
  };
  React.useEffect(()=>{ load(); const id=setInterval(load, 10000); return ()=>clearInterval(id); },[]);

  return (
    <div className="container">
      <div className="card">
        <h3>Equity Curve</h3>
        <div style={{height:360}}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="t" tick={{fontSize:12}} hide/>
              <YAxis domain={['auto','auto']} tick={{fontSize:12}} />
              <Tooltip />
              <Line type="monotone" dataKey="nav" stroke="#5b9dff" dot={false}/>
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
