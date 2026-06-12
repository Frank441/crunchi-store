'use client';
import Link from 'next/link';
import { RegisterBox } from './components';

const PageContent = () => {
    return (
        <div className="py-32 w-full flex flex-col justify-center items-center">
            <h1 className="text-white font-ubuntu text-4xl">Crear cuenta</h1>
            <RegisterBox />
            <p className="mt-8 text-white/60 font-inter text-sm">
                ¿Ya tenés cuenta?{' '}
                <Link href="/login" className="text-primary hover:underline">Acceder</Link>
            </p>
        </div>
    )
}

export default PageContent;
