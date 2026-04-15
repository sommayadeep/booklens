export function LoadingDots() {
  return (
    <span className="inline-flex items-center gap-1">
      <span className="h-2 w-2 animate-pulseSoft rounded-full bg-accent" />
      <span className="h-2 w-2 animate-pulseSoft rounded-full bg-accent [animation-delay:120ms]" />
      <span className="h-2 w-2 animate-pulseSoft rounded-full bg-accent [animation-delay:240ms]" />
    </span>
  );
}
