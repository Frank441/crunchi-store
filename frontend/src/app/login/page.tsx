import LoginPageContent from './LoginPageContent';
import { getSessionUser } from '@/lib/auth/getSessionUser';
import { redirect } from 'next/navigation';

export default async function LoginPage() {
    const user = await getSessionUser();

    if (user) redirect('/home');
    return (
        <LoginPageContent />
    )
}