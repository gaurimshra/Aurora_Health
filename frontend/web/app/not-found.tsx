export default function NotFound() {
  return (
    <main className="flex min-h-screen items-center justify-center px-6">
      <div className="panel max-w-xl p-10 text-center">
        <p className="eyebrow">404</p>
        <h1 className="mt-3 font-display text-5xl text-slate-900">Page not found</h1>
        <p className="mt-4 text-base leading-7 text-slate-500">
          Aurora could not find the page you requested.
        </p>
        <div className="mt-8 flex justify-center">
          <a href="/" className="button-primary">
            Return home
          </a>
        </div>
      </div>
    </main>
  );
}
