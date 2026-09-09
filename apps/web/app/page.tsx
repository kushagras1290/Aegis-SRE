type Incident={id:string;title:string;severity:string;status:string};
export default async function Home(){
  const incidents:Incident[]=[];
  return <main style={{padding:32,fontFamily:'sans-serif'}}><h1>Aegis SRE</h1><p>AI-native incident response with deterministic safety controls.</p><section><h2>Active incidents</h2>{incidents.length===0?<p>No incidents loaded.</p>:incidents.map(i=><article key={i.id}>{i.severity} · {i.title} · {i.status}</article>)}</section></main>
}
