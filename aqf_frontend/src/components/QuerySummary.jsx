
export default function QuerySummary({conditions,outputs}){
 return (
  <div className="panel">
   <h3>Current Query</h3>
   {conditions.map((c,i)=><div key={i}>{c.field} {c.operator} {c.value}</div>)}
   <hr/>
   <h3>Output</h3>
   {outputs.map(x=><div key={x}>✓ {x}</div>)}
  </div>
 )
}
