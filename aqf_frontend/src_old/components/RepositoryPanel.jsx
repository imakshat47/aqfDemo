
export default function RepositoryPanel({
  compositions,selectedCompositions,setSelectedCompositions,
  selectedSections,setSelectedSections
}){
  const toggleComp=(name)=>{
    const next=selectedCompositions.includes(name)
      ? selectedCompositions.filter(x=>x!==name)
      : [...selectedCompositions,name];
    setSelectedCompositions(next);
  };

  const visible=compositions.filter(c=>selectedCompositions.includes(c.name));

  return (
    <div className="panel">
      <h3>Clinical Repository</h3>
      {compositions.map(c=>(
        <label key={c.name}>
          <input type="checkbox"
            checked={selectedCompositions.includes(c.name)}
            onChange={()=>toggleComp(c.name)} />
          {c.name}
        </label>
      ))}
      <hr/>
      <h3>Sections</h3>
      {visible.flatMap(c=>c.sections).map(s=>(
        <label key={s.key}>
          <input type="checkbox"
            checked={selectedSections.includes(s.key)}
            onChange={()=>{
              const next=selectedSections.includes(s.key)
               ? selectedSections.filter(x=>x!==s.key)
               : [...selectedSections,s.key];
              setSelectedSections(next);
            }}
          />
          {s.label}
        </label>
      ))}
    </div>
  )
}
