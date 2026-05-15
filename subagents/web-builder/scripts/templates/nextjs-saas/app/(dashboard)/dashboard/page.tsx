import { auth, currentUser } from "@clerk/nextjs/server";

export default async function DashboardPage() {
  const { userId } = await auth();
  const user = await currentUser();

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold">Dashboard</h1>
      <p className="mt-2 text-gray-600">
        Benvenuto{user?.firstName ? `, ${user.firstName}` : ""}!
      </p>
      <div className="mt-6 rounded-md bg-gray-50 p-4 text-sm">
        <p>
          User ID: <code className="font-mono">{userId}</code>
        </p>
        <p className="mt-1 text-gray-500">
          Questa pagina è protetta da Clerk middleware. Edit
          `app/(dashboard)/dashboard/page.tsx` per personalizzare.
        </p>
      </div>
    </div>
  );
}
