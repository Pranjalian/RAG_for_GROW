export default function ComparePage() {
  return (
    <div className="flex-1 p-lg overflow-y-auto pb-[120px]">
      <div className="max-w-6xl mx-auto flex flex-col gap-xl">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="font-headline-lg text-headline-lg font-bold text-primary">Compare Funds</h1>
            <p className="text-on-surface-variant font-title-md mt-2">Compare up to 4 mutual funds side by side</p>
          </div>
          <button className="bg-primary-container text-black px-4 py-2 rounded-lg font-title-md font-bold hover:bg-primary transition-colors flex items-center gap-2">
            <span className="material-symbols-outlined">add</span>
            Add Fund
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Fund 1 */}
          <div className="glass-panel p-xl rounded-2xl flex flex-col gap-6 relative group">
            <button className="absolute top-4 right-4 p-2 text-on-surface-variant hover:text-error opacity-0 group-hover:opacity-100 transition-opacity">
              <span className="material-symbols-outlined text-sm">close</span>
            </button>
            <div>
              <h3 className="font-headline-md text-headline-md text-primary">Parag Parikh Flexi Cap</h3>
              <p className="font-caption text-caption text-on-surface-variant">Growth • Direct Plan</p>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-on-surface-variant mb-1">NAV</p>
                <p className="font-headline-md text-headline-md">₹74.52</p>
              </div>
              <div>
                <p className="text-sm text-on-surface-variant mb-1">3Y Return</p>
                <p className="font-headline-md text-headline-md text-primary">+21.4%</p>
              </div>
              <div>
                <p className="text-sm text-on-surface-variant mb-1">Expense Ratio</p>
                <p className="font-title-md text-title-md text-on-surface">0.65%</p>
              </div>
              <div>
                <p className="text-sm text-on-surface-variant mb-1">Fund Size</p>
                <p className="font-title-md text-title-md text-on-surface">₹55,000 Cr</p>
              </div>
            </div>

            <div className="pt-4 border-t border-white/10">
              <p className="text-sm text-on-surface-variant mb-3">Top Sectors</p>
              <div className="flex flex-wrap gap-2">
                <span className="px-3 py-1 bg-surface-container-highest rounded text-sm">Financials (32%)</span>
                <span className="px-3 py-1 bg-surface-container-highest rounded text-sm">Tech (18%)</span>
                <span className="px-3 py-1 bg-surface-container-highest rounded text-sm">Cons (14%)</span>
              </div>
            </div>
          </div>

          {/* Fund 2 */}
          <div className="glass-panel p-xl rounded-2xl flex flex-col gap-6 relative group">
            <button className="absolute top-4 right-4 p-2 text-on-surface-variant hover:text-error opacity-0 group-hover:opacity-100 transition-opacity">
              <span className="material-symbols-outlined text-sm">close</span>
            </button>
            <div>
              <h3 className="font-headline-md text-headline-md text-tertiary-container">HDFC Flexi Cap</h3>
              <p className="font-caption text-caption text-on-surface-variant">Growth • Direct Plan</p>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-on-surface-variant mb-1">NAV</p>
                <p className="font-headline-md text-headline-md">₹1,642.10</p>
              </div>
              <div>
                <p className="text-sm text-on-surface-variant mb-1">3Y Return</p>
                <p className="font-headline-md text-headline-md text-primary">+24.8%</p>
              </div>
              <div>
                <p className="text-sm text-on-surface-variant mb-1">Expense Ratio</p>
                <p className="font-title-md text-title-md text-on-surface">0.85%</p>
              </div>
              <div>
                <p className="text-sm text-on-surface-variant mb-1">Fund Size</p>
                <p className="font-title-md text-title-md text-on-surface">₹48,000 Cr</p>
              </div>
            </div>

            <div className="pt-4 border-t border-white/10">
              <p className="text-sm text-on-surface-variant mb-3">Top Sectors</p>
              <div className="flex flex-wrap gap-2">
                <span className="px-3 py-1 bg-surface-container-highest rounded text-sm">Financials (38%)</span>
                <span className="px-3 py-1 bg-surface-container-highest rounded text-sm">Industrials (12%)</span>
                <span className="px-3 py-1 bg-surface-container-highest rounded text-sm">IT (10%)</span>
              </div>
            </div>
          </div>

          {/* Empty Slot */}
          <div className="glass-panel p-xl rounded-2xl flex flex-col items-center justify-center gap-4 border-dashed border-2 border-white/20 hover:border-primary/50 transition-colors cursor-pointer opacity-50 hover:opacity-100">
            <div className="w-16 h-16 rounded-full bg-surface-container-highest flex items-center justify-center">
              <span className="material-symbols-outlined text-3xl">add</span>
            </div>
            <p className="font-title-md text-title-md text-on-surface-variant">Add Fund to Compare</p>
          </div>
        </div>
      </div>
    </div>
  );
}
