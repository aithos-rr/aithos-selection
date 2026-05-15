export default function HomePage() {
  return (
    <main className="min-h-screen">
      {/* Hero */}
      <section className="container mx-auto px-4 py-24 text-center">
        <h1 className="text-5xl font-bold tracking-tight md:text-7xl">
          {{ PROJECT_NAME_TITLE }}
        </h1>
        <p className="mx-auto mt-6 max-w-2xl text-lg text-gray-600 md:text-xl">
          {{ DESCRIPTION }}
        </p>
        <div className="mt-10 flex justify-center gap-4">
          <a
            href="#cta"
            className="rounded-md bg-black px-6 py-3 font-medium text-white hover:bg-gray-800"
          >
            Inizia ora
          </a>
          <a
            href="#features"
            className="rounded-md border border-black px-6 py-3 font-medium hover:bg-gray-100"
          >
            Scopri di più
          </a>
        </div>
      </section>

      {/* Features placeholder */}
      <section id="features" className="container mx-auto px-4 py-24">
        <h2 className="text-center text-3xl font-bold">Caratteristiche</h2>
        <div className="mt-12 grid gap-8 md:grid-cols-3">
          {[
            { title: "Veloce", desc: "Tempo di caricamento sotto 1 secondo" },
            { title: "Semplice", desc: "Interfaccia pulita e intuitiva" },
            { title: "Affidabile", desc: "99.9% uptime garantito" },
          ].map((f) => (
            <div key={f.title} className="rounded-lg border p-6">
              <h3 className="text-xl font-semibold">{f.title}</h3>
              <p className="mt-2 text-gray-600">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section id="cta" className="bg-gray-50 py-24">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold">Pronto a iniziare?</h2>
          <p className="mt-4 text-gray-600">Unisciti a noi oggi.</p>
          <a
            href="mailto:hello@{{DOMAIN}}"
            className="mt-8 inline-block rounded-md bg-black px-6 py-3 font-medium text-white hover:bg-gray-800"
          >
            Contattaci
          </a>
        </div>
      </section>

      <footer className="border-t py-8 text-center text-sm text-gray-500">
        © {{ YEAR }} {{ PROJECT_NAME_TITLE }}. Built with /web-builder.
      </footer>
    </main>
  );
}
