'use client';
import Link from 'next/link';
import { LoginBox } from './components';

const LoginPageContent = () => {
    return (
        <div className="py-32 w-full flex flex-col justify-center items-center">
            <h1 className="text-white font-ubuntu text-4xl"> Acceder</h1>
            <LoginBox />
            <p className="mt-8 text-white/60 font-inter text-sm">
                ¿No tenés cuenta?{' '}
                <Link href="/register" className="text-primary hover:underline">Crear cuenta</Link>
            </p>
        </div>
    )
}

export default LoginPageContent;
