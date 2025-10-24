"use client";

interface HeaderProps {
  heroCopy: { title: string; subtitle: string };
  isAuthenticated: boolean;
  onLogout: () => Promise<void> | void;
}

export function Header({ heroCopy, isAuthenticated, onLogout }: HeaderProps) {
  return (
    <header className="flex items-start justify-between gap-4">
      <div className="flex max-w-3xl flex-col gap-3">
        <h1 className="text-4xl font-bold tracking-tight text-white md:text-5xl">{heroCopy.title}</h1>
        <p className="text-sm leading-relaxed text-[rgba(220,230,255,0.75)] md:text-base">{heroCopy.subtitle}</p>
      </div>
      {isAuthenticated ? (
        <button
          onClick={() => void onLogout()}
          className="rounded-full bg-[rgba(255,255,255,0.12)] px-4 py-2 text-xs font-semibold uppercase tracking-[0.18em] text-white transition hover:bg-[rgba(255,255,255,0.2)]"
        >
          Logout
        </button>
      ) : null}
    </header>
  );
}
