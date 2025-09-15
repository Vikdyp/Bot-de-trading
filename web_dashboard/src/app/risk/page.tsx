'use client';
import React from 'react';
import { api } from '@/lib/api';

export default function RiskPage(){
  const [m, setM] = React.useState<any>(null);
  const refresh = async ()=> setM(await api.metrics());
  React.useEffect(()=>{ refresh(); const id=setInterval(refresh, 8000); return ()=>clearInterval(id); },[]);

  return (
    <div className="container">
      <div className="card"><h3>Risk</h3><div className="sub">Aperçu des métriques de risque</div></div>
      {m && (
        <div className="grid grid-3" style={{marginTop:16}}>
          <div className="card"><h3>Winrate</h3><div className="value">{((m.winrate||0)*100).toFixed(1)}%</div></div>
          <div className="card"><h3>Sharpe (approx)</h3><div className="value">{Number(m.sharpe||0).toFixed(2)}</div></div>
          <div className="card"><h3>Trades</h3><div className="value">{m.trades ?? 0}</div></div>
        </div>
      )}
    </div>
  );
}
