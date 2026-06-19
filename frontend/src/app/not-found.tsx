"use client";

import Image from 'next/image';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

export default function NotFound() {
	const router = useRouter();

	return (
		<main className="relative min-h-[calc(100vh-0)] overflow-hidden bg-background text-white">
			<div className="absolute inset-0 bg-[radial-gradient(circle_at_top,rgba(91,128,220,0.22),transparent_34%),radial-gradient(circle_at_bottom_right,rgba(153,182,254,0.16),transparent_26%),linear-gradient(180deg,rgba(255,255,255,0.03),transparent_28%)]" />
			<div className="absolute -left-24 top-20 h-72 w-72 rounded-full bg-primary/15 blur-3xl" />
			<div className="absolute -right-20 bottom-10 h-80 w-80 rounded-full bg-primary-hovered/10 blur-3xl" />

			<section className="relative mx-auto flex min-h-screen max-w-6xl flex-col items-center justify-center px-6 py-20 text-center">
				<div className="mb-10 flex items-center gap-3 rounded-full border border-white/10 bg-white/5 px-4 py-2 backdrop-blur-sm">
					<Image src="/logo.png" alt="CrunchiStore" width={28} height={28} className="h-7 w-7" />
					<span className="font-ubuntu text-sm font-semibold uppercase tracking-[0.3em] text-primary">CrunchiStore</span>
				</div>

				<div className="relative mb-10">
					<div className="absolute inset-0 rounded-full bg-primary/10 blur-3xl" />
					<h1 className="relative font-ubuntu text-[7rem] font-extrabold leading-none tracking-[-0.08em] text-white md:text-[11rem]">
						404
					</h1>
				</div>

				<div className="max-w-2xl space-y-6">
					<p className="font-ubuntu text-3xl font-bold text-white md:text-5xl">
						Esta página se perdió entre los tomos.
					</p>
					<p className="mx-auto max-w-xl text-base leading-7 text-white/72 md:text-lg">
						La URL que buscás no existe o fue movida. Volvé al catálogo, seguí explorando y encontrá otra serie para sumar a tu biblioteca.
					</p>
				</div>

				<div className="mt-10 flex flex-col gap-4 sm:flex-row">
					<button
						onClick={() => router.back()}
						className="cursor-pointer rounded-full border border-white/15 bg-white/5 px-8 py-4 font-ubuntu text-sm font-bold uppercase tracking-[0.22em] text-white transition-all duration-300 hover:border-white/30 hover:bg-white/10"
					>
						Volver atrás
					</button>

					<Link
						href="/"
						className="rounded-full bg-primary px-8 py-4 font-ubuntu text-sm font-bold uppercase tracking-[0.22em] text-black transition-all duration-300 hover:bg-primary-hovered"
					>
						Ir al inicio
					</Link>
				</div>

				<div className="mt-16 grid w-full max-w-3xl grid-cols-1 gap-4 sm:grid-cols-3">
					<div className="rounded-3xl border border-white/10 bg-white/5 p-5 text-left backdrop-blur-sm">
						<p className="font-ubuntu text-xs font-semibold uppercase tracking-[0.25em] text-primary">Atajo</p>
						<p className="mt-3 text-sm leading-6 text-white/75">Buscá títulos desde la home y retomá tu recorrido en segundos.</p>
					</div>
					<div className="rounded-3xl border border-white/10 bg-white/5 p-5 text-left backdrop-blur-sm">
						<p className="font-ubuntu text-xs font-semibold uppercase tracking-[0.25em] text-primary">Marca</p>
						<p className="mt-3 text-sm leading-6 text-white/75">La experiencia mantiene el lenguaje visual del sitio: negro, azul y contraste fuerte.</p>
					</div>
					<div className="rounded-3xl border border-white/10 bg-white/5 p-5 text-left backdrop-blur-sm">
						<p className="font-ubuntu text-xs font-semibold uppercase tracking-[0.25em] text-primary">Cliente</p>
						<p className="mt-3 text-sm leading-6 text-white/75">La página se renderiza como componente cliente para habilitar navegación inmediata.</p>
					</div>
				</div>
			</section>
		</main>
	);
}
