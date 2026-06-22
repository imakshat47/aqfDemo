import React from 'react';
import { displayFieldLabel, displaySectionLabel } from '../utils/clinicalTerminology';

const FormPreview = ({
  groups = [],
  selectedGroups = [],
  selectedSections = [],
  fieldState = {},
  fieldIndex
}) => {
  const lines = [];
  const outputLabels = [];

  groups.forEach((group) => {
    if (!selectedGroups.includes(group.label)) return;
    lines.push({ text: group.displayLabel || group.label, type: 'group' });
    
    (group.sections || []).forEach((section) => {
      if (!selectedSections.includes(section.key)) return;
      lines.push({ text: `↳ ${section.displayLabel || displaySectionLabel(section.label)}`, type: 'section' });
      
      (section.fields || []).forEach((field) => {
        const state = fieldState[field.key];
        if (!state || !state.value) return;
        const fieldLabel = field.displayLabel || displayFieldLabel(field.label);
        lines.push({ text: `  • ${fieldLabel} ${state.operator || '='} "${state.value}"`, type: 'criteria' });
      });
    });
  });

  Object.entries(fieldState)
    .filter(([, val]) => val?.show)
    .forEach(([key]) => {
      const entry = fieldIndex?.get(key);
      outputLabels.push(entry?.displayLabel || entry?.label || key);
    });

  return (
    <div className="flex flex-col h-full">
      <h3 className="text-sm font-semibold text-slate-800 mb-3">Current Search Context</h3>
      
      {/* Code-style dynamic block */}
      <div className="bg-slate-800 rounded-lg p-4 font-mono text-xs overflow-x-auto shadow-inner space-y-1 max-h-64 overflow-y-auto">
        {lines.length > 0 ? (
          lines.map((line, idx) => {
            if (line.type === 'group') return <div key={idx} className="text-teal-400 font-semibold mt-2 first:mt-0">{line.text}</div>;
            if (line.type === 'section') return <div key={idx} className="text-slate-300 pl-2">{line.text}</div>;
            return <div key={idx} className="text-slate-400 pl-6">{line.text}</div>;
          })
        ) : (
          <div className="text-slate-500 italic">No components or criteria selected.</div>
        )}
      </div>

      <div className="mt-6 pt-4 border-t border-slate-100">
        <h3 className="text-sm font-semibold text-slate-800 mb-1">Output Fields</h3>
        <p className="text-xs text-slate-500 mb-3">
          Fields selected to show in results: <span className="font-bold text-slate-700">{outputLabels.length}</span>
        </p>
        
        {outputLabels.length > 0 ? (
          <div className="flex flex-wrap gap-1.5">
            {outputLabels.map((tag, idx) => (
              <span key={idx} className="text-[11px] bg-teal-50 text-teal-700 font-medium px-2 py-0.5 rounded border border-teal-100">
                {tag}
              </span>
            ))}
          </div>
        ) : (
          <div className="text-xs italic text-slate-400 bg-slate-50 p-3 rounded border border-slate-100 border-dashed">
            No output fields selected yet. Toggle "Show in results" within the fields list.
          </div>
        )}
      </div>
    </div>
  );
};

export default FormPreview;