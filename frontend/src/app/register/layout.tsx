import type { Metadata } from 'next';
import React from 'react';

export const metadata: Metadata = {
    title: 'Crear cuenta - CrunchiStore'
}

export default function RegisterLayout ({children}: {children: React.ReactNode}){
    return (
        <div className="bg-background">
            {children}
        </div>
    )
}
