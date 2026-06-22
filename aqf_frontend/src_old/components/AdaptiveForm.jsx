{/* Left Column: Explorer */}
        <div className="col-span-3 bg-white rounded-xl shadow-sm ring-1 ring-slate-200 p-5 h-[calc(100vh-8rem)] overflow-y-auto">
          <div className="flex items-center gap-2 mb-4 pb-3 border-b border-slate-100">
            <span className="flex h-6 w-6 items-center justify-center rounded-full bg-teal-100 text-xs font-bold text-teal-700">1</span>
            <h2 className="text-base font-semibold text-slate-800">Repository Explorer</h2>
          </div>
          <CompositionSelector 
            groups={groups}
            selectedGroups={selectedGroups}
            selectedSections={selectedSections}
            onToggleGroup={onToggleGroup}
            onToggleSection={onToggleSection}
          />
        </div>