import React from 'react';

export default function CompositionSelector({
  groups = [],
  selectedGroups = [],
  selectedSections = [],
  onToggleGroup,
  onToggleSection
}) {
  return (
    <div className="space-y-2">
      {groups.map((group) => {
        const isGroupSelected = selectedGroups.includes(group.label);
        const sectionCount = group.sections?.length || 0;
        const fieldCount = group.fields?.length || 0;
        const groupTitle = group.displayLabel || group.label;

        return (
          <div key={group.group_id || group.label} className="flex flex-col">
            
            {/* Parent Clinical Category */}
            <label className="flex items-start gap-3 p-2 hover:bg-slate-50 rounded-md cursor-pointer group transition-colors">
              <input 
                type="checkbox" 
                checked={isGroupSelected}
                onChange={() => onToggleGroup(group.label)}
                className="mt-1 h-4 w-4 rounded border-slate-300 text-teal-600 focus:ring-teal-500 cursor-pointer"
              />
              <div className="flex flex-col min-w-0">
                <span className="text-sm font-medium text-slate-700 group-hover:text-slate-900 truncate" title={groupTitle}>
                  {groupTitle}
                </span>
                <span className="text-xs text-slate-400 font-medium">
                  {fieldCount} fields &middot; {sectionCount} sections
                </span>
              </div>
            </label>

            {/* Children (Indented Tree View) */}
            {isGroupSelected && group.sections && (
              <div className="ml-7 border-l border-slate-200 flex flex-col gap-1 mt-1">
                {group.sections.map((section) => {
                  const isSectionChecked = selectedSections.includes(section.key);
                  const sectionTitle = section.displayLabel || section.label;

                  return (
                    <label 
                      key={section.key} 
                      className={`flex items-center gap-2.5 pl-3 py-1.5 hover:bg-slate-50/80 rounded-r-md cursor-pointer group relative transition-colors ${
                        isSectionChecked ? 'text-teal-900 font-medium' : 'text-slate-600'
                      }`}
                    >
                      {/* Active section visual indicator line highlight */}
                      {isSectionChecked && (
                        <div className="absolute left-[-14px] top-0 bottom-0 w-[2px] bg-teal-500 rounded-full" />
                      )}

                      <input 
                        type="checkbox" 
                        checked={isSectionChecked}
                        onChange={() => onToggleSection(section.key)}
                        className="h-3.5 w-3.5 rounded border-slate-300 text-teal-500 focus:ring-teal-500 cursor-pointer"
                      />
                      <span className="text-xs tracking-wide truncate" title={sectionTitle}>
                        {sectionTitle}
                      </span>
                    </label>
                  );
                })}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}