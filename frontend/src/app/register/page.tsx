import PageContent from './PageContent';
import { getSessionUser } from '@/lib/auth/getSessionUser';
import { redirect } from 'next/navigation';

export default async function RegisterPage() {
    const user = await getSessionUser();

    if (user) redirect('/home');
    return (
        <PageContent />
    )
}
