"use client";

export function BackgroundOrbs() {
  return (
    <div className="pointer-events-none absolute left-0 top-0 -z-10 h-full w-full overflow-hidden">
      <div className="absolute left-[-10%] top-[-10%] h-[380px] w-[380px] rounded-full bg-[radial-gradient(circle_at_center,rgba(47,128,237,0.35),transparent_60%)] blur-2xl" />
      <div className="absolute right-[-10%] top-[10%] h-[420px] w-[420px] rounded-full bg-[radial-gradient(circle_at_center,rgba(174,109,255,0.35),transparent_60%)] blur-2xl" />
      <div className="absolute bottom-[-10%] left-[15%] h-[460px] w-[460px] rounded-full bg-[radial-gradient(circle_at_center,rgba(72,255,203,0.28),transparent_60%)] blur-2xl" />
    </div>
  );
}
