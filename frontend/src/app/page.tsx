import Image from 'next/image';

export default function Home() {
  return (
    <div className="w-full relative flex flex-col items-center justify-center h-full">
      <div className="w-full absolute h-full bg-linear-to-r from-black to-transparent z-10">
      </div>
      <Image src="/hero_image_background.webp" alt="Hero Background Image" width={1920} height={1080} className="w-7xl" style={{maskImage: 'linear-gradient(to right, transparent 0%, black 10%, black 90%, transparent 100%)'}} />
      <div className="w-6xl absolute z-20 flex flex-col items-start justify-start gap-8">
        <h2 className="font-ubuntu text-white font-extrabold text-4xl w-xl">Encontrá el manga que estás buscando.</h2>
        <button className="bg-primary text-black text-xl py-4 px-16 rounded-full font-extrabold font-ubuntu tracking-wide cursor-pointer transition-all duration-300 hover:bg-[#9ab6ff]">Probá CrunchiStore Plus gratis por 7 días.</button>
        <p className="w-xl font-inter text-white/80">Tras tu prueba gratuita de CrunchiStore Plus, tu cuenta se renovará automáticamente al precio de ARS 6,099.00 al mes. Puedes cancelar en cualquier momento.</p>
      </div>
    </div>
  )
}