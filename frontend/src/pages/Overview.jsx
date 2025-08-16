import React, {useEffect, useState} from 'react'
import {api} from '../api'

export default function Overview(){
  const [cfg,setCfg] = useState(null)
  const [pf,setPf] = useState(null)
  useEffect(()=>{
    api('/config').then(setCfg)
    api('/portfolio').then(setPf)
  },[])
  if(!cfg || !pf) return <div>Chargement…</div>
  return (
    <div>
      <h3>Overview</h3>
      <div>Mode: <b>{pf.mode}</b> | Timeframe: <b>{cfg.timeframe}</b></div>
      <div>Budget: <b>{pf.budget_eur}€</b> | Alloc/trade: <b>{pf.alloc_per_trade_eur}€</b> | Max pos: <b>{pf.max_concurrent_pos}</b></div>
      <div>Paires: {cfg.pairs.join(', ')} / {cfg.quote_asset}</div>
      <div style={{marginTop:12}}>
        <button onClick={()=>api('/paper/start',{method:'POST'}).then(()=>location.reload())}>Paper Start</button>
        <button onClick={()=>api('/paper/stop',{method:'POST'}).then(()=>location.reload())} style={{marginLeft:8}}>Stop</button>
      </div>
    </div>
  )
}
