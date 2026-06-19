import { redirect } from 'next/navigation';
import { Suspense } from 'react';
import { getSessionUser } from '@/lib/auth/getSessionUser';
import PageContent from './PageContent';

export default async function HomePage() {
  const user = await getSessionUser();

  if (!user) redirect('/login');

  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-background px-8 pb-8 pt-28">
          <div className="max-w-5xl mx-auto">
            <h1 className="text-4xl font-extrabold font-ubuntu mb-10">Hola, {user.alias}</h1>
            <p className="text-lg text-gray-400 font-inter">Cargando catálogo...</p>
          </div>
        </div>
      }
    >
      <PageContent alias={user.alias} />
    </Suspense>
  );
}
