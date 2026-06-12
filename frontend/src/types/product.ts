export interface Product {
    id: number;
    nombre: string;
    categoria: string;
    precio: number;
    stock: number;
    marca: string;
    descripcion: string;
    imagenes: string[];
    talles?: string[] | null;
    volumen?: number | null;
}
