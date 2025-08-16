export async function api(path, opts={}) {
  const res = await fetch(`/api${path}`, {headers: {'Content-Type':'application/json'}, ...opts});
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
