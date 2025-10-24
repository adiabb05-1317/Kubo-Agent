"use client";

import Link from "next/link";

interface HeaderProps {
  heroCopy: {
    title: string;
    subtitle: string;
  };
  isAuthenticated: boolean;
  onLogout: () => Promise<void> | void;
}

export function Header({ heroCopy, isAuthenticated, onLogout }: HeaderProps) {
  return (
    <header className="glass-panel gradient-border relative flex flex-col gap-6 overflow-hidden p-8 md:flex-row md:items-center md:justify-between">
      <div className="flex flex-col gap-3">
        <div className="inline-flex items-center gap-2 rounded-full bg-[rgba(47,128,237,0.12)] px-4 py-1 text-sm text-[rgba(255,255,255,0.75)]">
          <span className="inline-block h-2 w-2 rounded-full bg-[rgba(47,128,237,0.9)]" />
          Pods live sync enabled
        </div>
        <h1 className="text-balance text-3xl font-semibold tracking-tight md:text-5xl">{heroCopy.title}</h1>
        <p className="max-w-2xl text-lg text-[rgba(240,243,255,0.78)]">{heroCopy.subtitle}</p>
      </div>
      <nav className="flex flex-wrap items-center gap-3 text-sm text-[rgba(255,255,255,0.8)]">
        <HeaderLink href="#auth" label="Auth" />
        <HeaderLink href="#pods" label="Pods" />
        <HeaderLink href="#chat" label="Chat Concierge" />
        {isAuthenticated ? (
          <button
            className="rounded-full border border-[rgba(255,255,255,0.2)] px-4 py-2 text-xs uppercase tracking-wide text-[rgba(255,255,255,0.85)] transition hover:border-white"
            onClick={() => void onLogout()}
          >
            Log out
          </button>
        ) : null}
      </nav>
    </header>
  );
}

function HeaderLink({ href, label }: { href: string; label: string }) {
  return (
    <Link className="rounded-full border border-transparent px-4 py-2 transition hover:border-[rgba(255,255,255,0.18)]" href={href}>
      {label}
    </Link>
  );
}


