"use client";

interface Props {
  title: string;
  subtitle?: string;
}

export default function ScanOverlay({ title, subtitle }: Props) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm">
      <div className="bg-surface-card border border-border-primary rounded-2xl p-8 w-full max-w-sm mx-4 shadow-2xl">
        {/* Animated icon */}
        <div className="flex justify-center mb-5">
          <div className="relative w-12 h-12">
            <div className="absolute inset-0 rounded-full border-2 border-accent/20" />
            <div className="absolute inset-0 rounded-full border-2 border-transparent border-t-accent animate-spin" />
            <div className="absolute inset-2 rounded-full bg-accent/10 flex items-center justify-center">
              <svg className="w-4 h-4 text-accent" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
          </div>
        </div>

        {/* Title */}
        <h2 className="text-base font-semibold text-text-primary text-center mb-1">{title}</h2>
        {subtitle && (
          <p className="text-xs text-text-muted text-center mb-5">{subtitle}</p>
        )}

        {/* Progress bar */}
        <div className="relative h-1.5 bg-surface-active rounded-full overflow-hidden">
          <div
            className="absolute top-0 h-full w-2/5 rounded-full bg-accent"
            style={{ animation: "scan-slide 1.6s ease-in-out infinite" }}
          />
        </div>

        <p className="text-[10px] text-text-muted text-center mt-3 uppercase tracking-widest">
          Please wait
        </p>
      </div>
    </div>
  );
}
