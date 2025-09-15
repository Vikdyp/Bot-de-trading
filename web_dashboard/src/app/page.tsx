'use client';
import React from 'react';
import StatusBar from './components/StatusBar';
import { api } from '@/lib/api';
import { StatCard } from './components/StatCard';
import { PositionsTable, PositionRow } from './components/PositionsTable';

export default function OverviewPage(){
  const [portfolio, setPortfolio] = React.useState<any>(null);
  const [positions, setPositions] = React.useState<PositionRow[]>([]);
  const refresh = async ()=>{
    const [p, pos] = await Promise.all([api.portfolio(), api.positions()]);
    setPortfolio(p); setPositions(pos);
  };
  React.useEffect(()=>{ refresh(); const id=setInterval(refresh, 8000); return ()=>clearInterval(id); },[]);
  const closeAll = async (symbol:string)=>{ await api.paperClose(symbol); await refresh(); };

  const nav = Number(portfolio?.nav||0);
  const cash = Number(portfolio?.cash_eur||0);
  const expo = Number(portfolio?.exposure_eur ?? (nav - cash));
  const ratio = Number(portfolio?.exposure_ratio ?? (nav?expo/nav:0));
  const breakdown: Record<string, number> = portfolio?.breakdown || {};

  return (
    <div className="container">
      <StatusBar/>
      <div style={{height:12}}/>
      {!portfolio ? <div className="sub">Chargement...</div> : (
        <>
          <div className="grid grid-3">
            <StatCard title="NAV (EUR)" value={nav.toLocaleString(undefined,{maximumFractionDigits:2})}/>
            <StatCard title="Cash (EUR)" value={cash.toLocaleString(undefined,{maximumFractionDigits:2})}/>
            <StatCard title="Exposition" value={(ratio*100).toFixed(1)+' %'} hint={`${expo.toFixed(2)} €`} accent={ratio>0.5?'warn':'ok'}/>
          </div>

          <div className="card" style={{marginTop:16}}>
            <h3>Répartition</h3>
            {Object.keys(breakdown).length===0 ? <div className="sub">Aucune exposition</div> : (
              <div className="row" style={{flexWrap:'wrap'}}>
                {Object.entries(breakdown).map(([k,v])=>(
                  <div key={k} className="badge" style={{marginRight:8}}>{k}: {Number(v).toFixed(2)} €</div>
                ))}
              </div>
            )}
          </div>

          <div className="card" style={{marginTop:16}}>
            <h3>Actions rapides</h3>
            <QuickTrade onDone={refresh}/>
          </div>

          <div style={{marginTop:16}}>
            <PositionsTable rows={positions} onClose={closeAll}/>
          </div>
        </>
      )}
    </div>
  );
}

function QuickTrade({ onDone }:{ onDone: ()=>void }){
  const [symbol,setSymbol] = React.useState('BTCEUR');
  const [alloc,setAlloc] = React.useState<number>(10);
  const [qty,setQty] = React.useState<string>('');
  const buy = async ()=>{ await api.paperBuy(symbol, Number(alloc)); onDone(); };
  const sell = async ()=>{
    const pos = await api.positions();
    const row = (pos || []).find((p:any)=>p.symbol===symbol);
    const q = qty==='' ? row?.qty : Number(qty);
    if (!q || q<=0) return;
    await api.paperSell(symbol, q);
    onDone();
  };
  const closeAll = async ()=>{ await api.paperClose(symbol); onDone(); };

  return (
    <div className="row">
      <select value={symbol} onChange={e=>setSymbol((e.target as HTMLSelectElement).value)} style={{minWidth:140}}>
        {['BTCEUR','ETHEUR','BNBEUR','SOLEUR','ADAEUR','XDCEUR','LTCEUR'].map(s=><option key={s} value={s}>{s}</option>)}
      </select>
      <input className="input" type="number" min={0} step="1" value={alloc} onChange={e=>setAlloc(Number((e.target as HTMLInputElement).value))} style={{maxWidth:160}}/>
      <button className="btn primary" onClick={buy}>BUY (alloc €)</button>
      <input className="input" placeholder="qty (optionnel)" value={qty} onChange={e=>setQty((e.target as HTMLInputElement).value)} style={{maxWidth:160}}/>
      <button className="btn" onClick={sell}>SELL (qty)</button>
      <button className="btn" onClick={closeAll}>Close All</button>
    </div>
  );
}
