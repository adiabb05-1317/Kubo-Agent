export function BackgroundOrbs() {
  return (
    <div aria-hidden className="pointer-events-none fixed inset-0 -z-10 overflow-hidden">
      <div className="absolute -top-24 right-[-20%] h-[320px] w-[480px] rounded-full bg-[rgba(47,128,237,0.18)] blur-[160px]" />
      <div className="absolute top-1/3 left-[-10%] h-[360px] w-[420px] rounded-full bg-[rgba(144,95,255,0.22)] blur-[180px]" />
      <div className="absolute bottom-[-20%] right-1/4 h-[280px] w-[380px] rounded-full bg-[rgba(72,255,203,0.18)] blur-[160px]" />
    </div>
  );
}


