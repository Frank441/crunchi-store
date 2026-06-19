import { redirect } from 'next/navigation';
import { getSessionUser } from '@/lib/auth/getSessionUser';
import { logEvent } from '@/lib/events/logEvent';
import { EVENT_TYPES } from '@/constants/events';
import PageContent from './PageContent';


export default async function ProductoDetallePage({ params }: { params: Promise<{ id: string }> }) {
    const user = await getSessionUser();
    if (!user) redirect('/login');

    const { id } = await params;

    await logEvent(user.id, Number(id), EVENT_TYPES.VIEW_PRODUCT);

    return (
        <div className="min-h-screen bg-background px-8 pb-16 pt-28">
            <PageContent id={id} /> 
        </div>
    );
}
