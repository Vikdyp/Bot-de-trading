export function StatCard({ title, value, hint, accent }: { title:string; value:string|number; hint?:string; accent?:'ok'|'danger'|'warn' }) {
  const color = accent==="ok" ? "kpi-up" : accent==="danger" ? "kpi-down" : accent==="warn" ? "kpi-warn" : "";
  return (
    <div className="card">
      <h3>{title}</h3>
      <div className={`value ${color||''}`}>{value}</div>
      {hint ? <div className="sub">{hint}</div> : null}
    </div>
  );
}
