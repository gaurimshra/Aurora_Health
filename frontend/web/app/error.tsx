"use client";

export default function ErrorPage({
  error,
  reset,
}: Readonly<{
  error: Error & { digest?: string };
  reset: () => void;
}>) {
  return (
    <main className="flex min-h-screen items-center justify-center px-6">
      <div className="panel max-w-xl p-10 text-center">
        <p className="eyebrow">500</p>
        <h1 className="mt-3 font-display text-5xl text-slate-900">Something went wrong</h1>
        <p className="mt-4 text-base leading-7 text-slate-500">
          {error.message || "Aurora hit an unexpected rendering error."}
        </p>
        <div className="mt-8 flex flex-wrap justify-center gap-3">
          <button type="button" className="button-primary" onClick={reset}>
            Try again
          </button>
          <a href="/" className="button-secondary">
            Return home
          </a>
        </div>
      </div>
    </main>
  );
}
