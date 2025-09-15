'use client';
export type PositionRow = {
  symbol: string;
  qty: number;
  avg_price: number;
  stop_price?: number;
  opened_at?: string;
  updated_at?: string;
}

export function PositionsTable({ rows, onClose }: { rows: PositionRow[]; onClose?: (symbol:string)=>void }){
  return (
    <div className="card">
      <h3>Positions ouvertes</h3>
      <table className="table">
        <thead>
          <tr>
            <th>Symbole</th><th>Qty</th><th>Prix moyen</th><th>Stop</th><th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {(!rows || rows.length===0) && (
            <tr><td colSpan={5} className="sub">Aucune position</td></tr>
          )}
          {rows?.map((r)=>(
            <tr key={r.symbol}>
              <td><span className="badge">{r.symbol}</span></td>
              <td>{r.qty}</td>
              <td>{Number(r.avg_price||0).toLocaleString()}</td>
              <td>{Number(r.stop_price||0).toLocaleString()}</td>
              <td>{onClose && <button className="btn" onClick={()=>onClose(r.symbol)}>Close</button>}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
