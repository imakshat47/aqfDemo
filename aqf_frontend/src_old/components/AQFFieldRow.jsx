import React, { useEffect, useState, useMemo } from 'react';
import { getSuggestions } from '../services/queryApi';
import { displayDatatypeLabel } from '../utils/clinicalTerminology';
import { humanizeOperator } from '../utils/operatorLabels';

export default function AQFFieldRow({ field, valueState, onChange }) {
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(false);

  // 1. Live Suggestion Fetcher
  useEffect(() => {
    let alive = true;
    (async () => {
      setLoading(true);
      try {
        const data = await getSuggestions(field.path || field.label);
        if (!alive) return;
        const list = Array.isArray(data?.suggestions) ? data.suggestions : [];
        setSuggestions(list.slice(0, 6)); // Keep a tidy row of suggestions
      } catch (err) {
        console.error(err);
      } finally {
        if (alive) setLoading(false);
      }
    })();
    return () => { alive = false };
  }, [field.path, field.label]);

  // 2. Dynamic Operators
  const operatorOptions = useMemo(() => {
    const ops = field.allowed_operators || ['=', '!=', 'contains', 'starts_with'];
    return Array.from(new Set(ops));
  }, [field.allowed_operators]);

  const label = field.displayLabel || field.label;
  const datatype = field.displayDatatype || displayDatatypeLabel(field.datatype);

  return (
    <div className="group flex flex-col gap-2 py-3 border-b border-slate-100 last:border-0 hover:bg-slate-50/50 transition-colors rounded-lg px-2 -mx-2">
      
      {/* Controls Row */}
      <div className="flex items-center gap-4 w-full">
        {/* Field Name & Type Badge */}
        <div className="w-1/3 flex flex-col gap-1">
          <label className="text-sm font-medium text-slate-700 truncate" title={label}>
            {label}
          </label>
          <span className="w-fit text-[10px] uppercase tracking-wider font-semibold text-slate-400 bg-slate-100 px-1.5 py-0.5 rounded">
            {datatype || 'Text'}
          </span>
        </div>

        {/* Condition Dropdown (Controlled) */}
        <div className="w-1/4">
          <select 
            className="w-full text-sm border-slate-200 rounded-md shadow-sm focus:border-teal-500 focus:ring-teal-500 text-slate-600 bg-white"
            value={valueState.operator}
            onChange={(e) => onChange({ ...valueState, operator: e.target.value })}
          >
            {operatorOptions.map((op) => (
              <option key={op} value={op}>
                {humanizeOperator(op)}
              </option>
            ))}
          </select>
        </div>

        {/* Value Input (Controlled) */}
        <div className="w-1/3">
          <input 
            type="text" 
            placeholder={loading ? "Loading suggestions..." : "Enter value..."}
            value={valueState.value}
            onChange={(e) => onChange({ ...valueState, value: e.target.value })}
            className="w-full text-sm border-slate-200 rounded-md shadow-sm focus:border-teal-500 focus:ring-teal-500 placeholder-slate-400"
          />
        </div>

        {/* Output Toggle (Functional Switch) */}
        <div className="w-auto flex items-center justify-end pr-2">
          <label className="flex items-center cursor-pointer select-none">
            <div className="relative">
              <input 
                type="checkbox" 
                className="sr-only" 
                checked={Boolean(valueState.show)}
                onChange={(e) => onChange({ ...valueState, show: e.target.checked })}
              />
              {/* Dynamic background color based on checked state */}
              <div className={`block w-8 h-5 rounded-full transition-colors ${valueState.show ? 'bg-teal-500' : 'bg-slate-200'}`}></div>
              {/* Sliding dot behavior */}
              <div className={`dot absolute left-1 top-1 bg-white w-3 h-3 rounded-full transition-transform ${valueState.show ? 'transform translate-x-3' : ''}`}></div>
            </div>
          </label>
        </div>
      </div>

      {/* Auto-Suggestions Row (Appears right under the input if suggestions exist) */}
      {suggestions.length > 0 && (
        <div className="flex flex-wrap gap-1.5 pl-[33.33%] mt-0.5">
          {suggestions.map((s) => (
            <button
              type="button"
              key={String(s.value)}
              onClick={() => onChange({ ...valueState, value: String(s.value) })}
              className="text-[11px] text-slate-500 bg-slate-100 hover:bg-teal-50 hover:text-teal-700 rounded-md px-2 py-0.5 transition-colors border border-transparent hover:border-teal-200"
            >
              {String(s.value)}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}