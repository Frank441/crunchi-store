export interface EventoPorUsuario {
  id_usuario: number;
  fecha_hora: string;
  id_evento: string;
  evento: string;
  id_producto: number;
}

export interface EventoPorProducto {
  id_producto: number;
  evento: string;
  id_evento: string;
  fecha_hora: string;
  id_usuario: number;
}