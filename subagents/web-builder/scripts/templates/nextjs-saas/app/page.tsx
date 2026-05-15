import Link from "next/link";

export default function HomePage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8">
      <h1 className="text-4xl font-bold">{{ PROJECT_NAME_TITLE }}</h1>
      <p className="mt-4 text-lg text-gray-600">{{ DESCRIPTION }}</p>
      <div className="mt-8 flex gap-4">
        <Link
          href="/sign-in"
          className="rounded-md bg-black px-4 py-2 text-white hover:bg-gray-800"
        >
          Accedi
        </Link>
        <Link
          href="/sign-up"
          className="rounded-md border border-black px-4 py-2 hover:bg-gray-100"
        >
          Registrati
        </Link>
      </div>
    </main>
  );
}
