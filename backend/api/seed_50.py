"""Dataset de 50 productos reales (figuras, mangas, indumentaria) para Mongo.

Imágenes: URLs reales de cdn.myanimelist.net (resueltas vía Jikan y verificadas
HTTP 200 al generar este archivo). Idempotente: resetea catálogo + contador.

Uso (con Mongo arriba):
    python -m api.seed_50
"""
from db.mongo import mongo as mongo_db

PRODUCTOS = [
    {"nombre": "Figura Naruto Uzumaki - Modo Sabio", "categoria": "Figuras", "precio": 18999.99, "stock": 12, "marca": "Bandai", "descripcion": "Figura Naruto Uzumaki - Modo Sabio. Producto oficial de la franquicia Naruto.", "imagenes": ["https://cdn.myanimelist.net/images/anime/1141/142503l.jpg"]},
    {"nombre": "Manga Naruto Vol. 1", "categoria": "Mangas", "precio": 8499.0, "stock": 30, "marca": "Ivrea", "descripcion": "Manga Naruto Vol. 1. Producto oficial de la franquicia Naruto.", "imagenes": ["https://cdn.myanimelist.net/images/manga/3/249658l.jpg"], "volumen": 1},
    {"nombre": "Remera Naruto - Aldea de la Hoja", "categoria": "Indumentaria", "precio": 12500.0, "stock": 20, "marca": "Crunchi Wear", "descripcion": "Remera Naruto - Aldea de la Hoja. Producto oficial de la franquicia Naruto.", "imagenes": ["https://cdn.myanimelist.net/images/anime/1141/142503l.jpg"], "talles": ["s", "m", "l", "xl", "xxl"]},
    {"nombre": "Figura Monkey D. Luffy Gear 5", "categoria": "Figuras", "precio": 22999.0, "stock": 8, "marca": "Banpresto", "descripcion": "Figura Monkey D. Luffy Gear 5. Producto oficial de la franquicia One Piece.", "imagenes": ["https://cdn.myanimelist.net/images/anime/1770/97704l.jpg"]},
    {"nombre": "Manga One Piece Vol. 1", "categoria": "Mangas", "precio": 8999.5, "stock": 35, "marca": "Ivrea", "descripcion": "Manga One Piece Vol. 1. Producto oficial de la franquicia One Piece.", "imagenes": ["https://cdn.myanimelist.net/images/manga/2/253146l.jpg"], "volumen": 1},
    {"nombre": "Remera One Piece - Jolly Roger", "categoria": "Indumentaria", "precio": 12900.0, "stock": 18, "marca": "Crunchi Wear", "descripcion": "Remera One Piece - Jolly Roger. Producto oficial de la franquicia One Piece.", "imagenes": ["https://cdn.myanimelist.net/images/anime/1770/97704l.jpg"], "talles": ["s", "m", "l", "xl", "xxl"]},
    {"nombre": "Figura Goku Ultra Instinto", "categoria": "Figuras", "precio": 27999.0, "stock": 10, "marca": "Good Smile Company", "descripcion": "Figura Goku Ultra Instinto. Producto oficial de la franquicia Dragon Ball.", "imagenes": ["https://cdn.myanimelist.net/images/anime/1887/92364l.jpg"]},
    {"nombre": "Manga Dragon Ball Vol. 1", "categoria": "Mangas", "precio": 7999.0, "stock": 40, "marca": "Ivrea", "descripcion": "Manga Dragon Ball Vol. 1. Producto oficial de la franquicia Dragon Ball.", "imagenes": ["https://cdn.myanimelist.net/images/manga/1/267793l.jpg"], "volumen": 1},
    {"nombre": "Remera Dragon Ball - Kame House", "categoria": "Indumentaria", "precio": 11900.0, "stock": 25, "marca": "Crunchi Wear", "descripcion": "Remera Dragon Ball - Kame House. Producto oficial de la franquicia Dragon Ball.", "imagenes": ["https://cdn.myanimelist.net/images/anime/1887/92364l.jpg"], "talles": ["s", "m", "l", "xl", "xxl"]},
    {"nombre": "Figura Eren Yeager - Titán de Ataque", "categoria": "Figuras", "precio": 24999.0, "stock": 6, "marca": "Kotobukiya", "descripcion": "Figura Eren Yeager - Titán de Ataque. Producto oficial de la franquicia Attack on Titan.", "imagenes": ["https://cdn.myanimelist.net/images/anime/10/47347l.jpg"]},
    {"nombre": "Manga Attack on Titan Vol. 1", "categoria": "Mangas", "precio": 9499.0, "stock": 22, "marca": "Panini", "descripcion": "Manga Attack on Titan Vol. 1. Producto oficial de la franquicia Attack on Titan.", "imagenes": ["https://cdn.myanimelist.net/images/manga/2/37846l.jpg"], "volumen": 1},
    {"nombre": "Remera Attack on Titan - Legión de Reconocimiento", "categoria": "Indumentaria", "precio": 13500.0, "stock": 15, "marca": "Crunchi Wear", "descripcion": "Remera Attack on Titan - Legión de Reconocimiento. Producto oficial de la franquicia Attack on Titan.", "imagenes": ["https://cdn.myanimelist.net/images/anime/10/47347l.jpg"], "talles": ["s", "m", "l", "xl", "xxl"]},
    {"nombre": "Figura Tanjiro Kamado", "categoria": "Figuras", "precio": 20999.0, "stock": 9, "marca": "Aniplex", "descripcion": "Figura Tanjiro Kamado. Producto oficial de la franquicia Demon Slayer.", "imagenes": ["https://cdn.myanimelist.net/images/anime/1286/99889l.jpg"]},
    {"nombre": "Manga Demon Slayer Vol. 1", "categoria": "Mangas", "precio": 8999.0, "stock": 28, "marca": "Ivrea", "descripcion": "Manga Demon Slayer Vol. 1. Producto oficial de la franquicia Demon Slayer.", "imagenes": ["https://cdn.myanimelist.net/images/manga/3/179023l.jpg"], "volumen": 1},
    {"nombre": "Remera Demon Slayer - Patrón Haori", "categoria": "Indumentaria", "precio": 12900.0, "stock": 17, "marca": "Crunchi Wear", "descripcion": "Remera Demon Slayer - Patrón Haori. Producto oficial de la franquicia Demon Slayer.", "imagenes": ["https://cdn.myanimelist.net/images/anime/1286/99889l.jpg"], "talles": ["s", "m", "l", "xl", "xxl"]},
    {"nombre": "Figura Satoru Gojo", "categoria": "Figuras", "precio": 25999.0, "stock": 7, "marca": "Megahouse", "descripcion": "Figura Satoru Gojo. Producto oficial de la franquicia Jujutsu Kaisen.", "imagenes": ["https://cdn.myanimelist.net/images/anime/1171/109222l.jpg"]},
    {"nombre": "Manga Jujutsu Kaisen Vol. 1", "categoria": "Mangas", "precio": 9299.0, "stock": 26, "marca": "Panini", "descripcion": "Manga Jujutsu Kaisen Vol. 1. Producto oficial de la franquicia Jujutsu Kaisen.", "imagenes": ["https://cdn.myanimelist.net/images/manga/3/210341l.jpg"], "volumen": 1},
    {"nombre": "Remera Jujutsu Kaisen - Tokyo Jujutsu High", "categoria": "Indumentaria", "precio": 12700.0, "stock": 19, "marca": "Crunchi Wear", "descripcion": "Remera Jujutsu Kaisen - Tokyo Jujutsu High. Producto oficial de la franquicia Jujutsu Kaisen.", "imagenes": ["https://cdn.myanimelist.net/images/anime/1171/109222l.jpg"], "talles": ["s", "m", "l", "xl", "xxl"]},
    {"nombre": "Figura Izuku Midoriya", "categoria": "Figuras", "precio": 17999.0, "stock": 11, "marca": "Banpresto", "descripcion": "Figura Izuku Midoriya. Producto oficial de la franquicia My Hero Academia.", "imagenes": ["https://cdn.myanimelist.net/images/anime/10/78745l.jpg"]},
    {"nombre": "Manga My Hero Academia Vol. 1", "categoria": "Mangas", "precio": 8499.0, "stock": 24, "marca": "Ivrea", "descripcion": "Manga My Hero Academia Vol. 1. Producto oficial de la franquicia My Hero Academia.", "imagenes": ["https://cdn.myanimelist.net/images/manga/1/209370l.jpg"], "volumen": 1},
    {"nombre": "Remera My Hero Academia - UA High", "categoria": "Indumentaria", "precio": 12500.0, "stock": 21, "marca": "Crunchi Wear", "descripcion": "Remera My Hero Academia - UA High. Producto oficial de la franquicia My Hero Academia.", "imagenes": ["https://cdn.myanimelist.net/images/anime/10/78745l.jpg"], "talles": ["s", "m", "l", "xl", "xxl"]},
    {"nombre": "Figura Guts - Armadura del Berserker", "categoria": "Figuras", "precio": 38999.0, "stock": 4, "marca": "Good Smile Company", "descripcion": "Figura Guts - Armadura del Berserker. Producto oficial de la franquicia Berserk.", "imagenes": ["https://cdn.myanimelist.net/images/anime/10/79352l.jpg"]},
    {"nombre": "Manga Berserk Vol. 1 (Edición Deluxe)", "categoria": "Mangas", "precio": 13999.0, "stock": 14, "marca": "Panini", "descripcion": "Manga Berserk Vol. 1 (Edición Deluxe). Producto oficial de la franquicia Berserk.", "imagenes": ["https://cdn.myanimelist.net/images/manga/1/157897l.jpg"], "volumen": 1},
    {"nombre": "Figura Ichigo Kurosaki - Bankai", "categoria": "Figuras", "precio": 23999.0, "stock": 8, "marca": "Kotobukiya", "descripcion": "Figura Ichigo Kurosaki - Bankai. Producto oficial de la franquicia Bleach.", "imagenes": ["https://cdn.myanimelist.net/images/anime/1541/147774l.jpg"]},
    {"nombre": "Manga Bleach Vol. 1", "categoria": "Mangas", "precio": 8299.0, "stock": 27, "marca": "Ivrea", "descripcion": "Manga Bleach Vol. 1. Producto oficial de la franquicia Bleach.", "imagenes": ["https://cdn.myanimelist.net/images/manga/3/180031l.jpg"], "volumen": 1},
    {"nombre": "Remera Bleach - Calavera Hollow", "categoria": "Indumentaria", "precio": 12400.0, "stock": 16, "marca": "Crunchi Wear", "descripcion": "Remera Bleach - Calavera Hollow. Producto oficial de la franquicia Bleach.", "imagenes": ["https://cdn.myanimelist.net/images/anime/1541/147774l.jpg"], "talles": ["s", "m", "l", "xl", "xxl"]},
    {"nombre": "Manga Death Note Vol. 1", "categoria": "Mangas", "precio": 8799.0, "stock": 33, "marca": "Ivrea", "descripcion": "Manga Death Note Vol. 1. Producto oficial de la franquicia Death Note.", "imagenes": ["https://cdn.myanimelist.net/images/manga/1/258245l.jpg"], "volumen": 1},
    {"nombre": "Remera Death Note - Manzana de Ryuk", "categoria": "Indumentaria", "precio": 12600.0, "stock": 20, "marca": "Crunchi Wear", "descripcion": "Remera Death Note - Manzana de Ryuk. Producto oficial de la franquicia Death Note.", "imagenes": ["https://cdn.myanimelist.net/images/anime/1079/138100l.jpg"], "talles": ["s", "m", "l", "xl", "xxl"]},
    {"nombre": "Figura Denji - Chainsaw", "categoria": "Figuras", "precio": 21999.0, "stock": 9, "marca": "Megahouse", "descripcion": "Figura Denji - Chainsaw. Producto oficial de la franquicia Chainsaw Man.", "imagenes": ["https://cdn.myanimelist.net/images/anime/1806/126216l.jpg"]},
    {"nombre": "Manga Chainsaw Man Vol. 1", "categoria": "Mangas", "precio": 9199.0, "stock": 29, "marca": "Panini", "descripcion": "Manga Chainsaw Man Vol. 1. Producto oficial de la franquicia Chainsaw Man.", "imagenes": ["https://cdn.myanimelist.net/images/manga/3/216464l.jpg"], "volumen": 1},
    {"nombre": "Remera Chainsaw Man - Pochita", "categoria": "Indumentaria", "precio": 12800.0, "stock": 18, "marca": "Crunchi Wear", "descripcion": "Remera Chainsaw Man - Pochita. Producto oficial de la franquicia Chainsaw Man.", "imagenes": ["https://cdn.myanimelist.net/images/anime/1806/126216l.jpg"], "talles": ["s", "m", "l", "xl", "xxl"]},
    {"nombre": "Figura Anya Forger", "categoria": "Figuras", "precio": 19999.0, "stock": 13, "marca": "Good Smile Company", "descripcion": "Figura Anya Forger. Producto oficial de la franquicia Spy x Family.", "imagenes": ["https://cdn.myanimelist.net/images/anime/1441/122795l.jpg"]},
    {"nombre": "Manga Spy x Family Vol. 1", "categoria": "Mangas", "precio": 8999.0, "stock": 31, "marca": "Ivrea", "descripcion": "Manga Spy x Family Vol. 1. Producto oficial de la franquicia Spy x Family.", "imagenes": ["https://cdn.myanimelist.net/images/manga/3/219741l.jpg"], "volumen": 1},
    {"nombre": "Figura Gon Freecss", "categoria": "Figuras", "precio": 16999.0, "stock": 10, "marca": "Banpresto", "descripcion": "Figura Gon Freecss. Producto oficial de la franquicia Hunter x Hunter.", "imagenes": ["https://cdn.myanimelist.net/images/anime/1305/132237l.jpg"]},
    {"nombre": "Manga Hunter x Hunter Vol. 1", "categoria": "Mangas", "precio": 8399.0, "stock": 23, "marca": "Ivrea", "descripcion": "Manga Hunter x Hunter Vol. 1. Producto oficial de la franquicia Hunter x Hunter.", "imagenes": ["https://cdn.myanimelist.net/images/manga/2/253119l.jpg"], "volumen": 1},
    {"nombre": "Figura Saitama", "categoria": "Figuras", "precio": 18499.0, "stock": 12, "marca": "Bandai", "descripcion": "Figura Saitama. Producto oficial de la franquicia One Punch Man.", "imagenes": ["https://cdn.myanimelist.net/images/anime/12/76049l.jpg"]},
    {"nombre": "Manga One Punch Man Vol. 1", "categoria": "Mangas", "precio": 9099.0, "stock": 25, "marca": "Panini", "descripcion": "Manga One Punch Man Vol. 1. Producto oficial de la franquicia One Punch Man.", "imagenes": ["https://cdn.myanimelist.net/images/manga/3/80661l.jpg"], "volumen": 1},
    {"nombre": "Figura Rei Ayanami", "categoria": "Figuras", "precio": 26999.0, "stock": 6, "marca": "Kotobukiya", "descripcion": "Figura Rei Ayanami. Producto oficial de la franquicia Evangelion.", "imagenes": ["https://cdn.myanimelist.net/images/anime/1314/108941l.jpg"]},
    {"nombre": "Remera Evangelion - NERV", "categoria": "Indumentaria", "precio": 13200.0, "stock": 17, "marca": "Crunchi Wear", "descripcion": "Remera Evangelion - NERV. Producto oficial de la franquicia Evangelion.", "imagenes": ["https://cdn.myanimelist.net/images/anime/1314/108941l.jpg"], "talles": ["s", "m", "l", "xl", "xxl"]},
    {"nombre": "Figura Jotaro Kujo", "categoria": "Figuras", "precio": 24999.0, "stock": 7, "marca": "Medicos", "descripcion": "Figura Jotaro Kujo. Producto oficial de la franquicia JoJo.", "imagenes": ["https://cdn.myanimelist.net/images/anime/1171/106036l.jpg"]},
    {"nombre": "Manga JoJo's Bizarre Adventure Vol. 1", "categoria": "Mangas", "precio": 9599.0, "stock": 19, "marca": "Ivrea", "descripcion": "Manga JoJo's Bizarre Adventure Vol. 1. Producto oficial de la franquicia JoJo.", "imagenes": ["https://cdn.myanimelist.net/images/manga/2/270475l.jpg"], "volumen": 1},
    {"nombre": "Manga Fullmetal Alchemist Vol. 1", "categoria": "Mangas", "precio": 8899.0, "stock": 26, "marca": "Panini", "descripcion": "Manga Fullmetal Alchemist Vol. 1. Producto oficial de la franquicia Fullmetal Alchemist.", "imagenes": ["https://cdn.myanimelist.net/images/manga/3/243675l.jpg"], "volumen": 1},
    {"nombre": "Remera Fullmetal Alchemist - Flamel", "categoria": "Indumentaria", "precio": 12500.0, "stock": 18, "marca": "Crunchi Wear", "descripcion": "Remera Fullmetal Alchemist - Flamel. Producto oficial de la franquicia Fullmetal Alchemist.", "imagenes": ["https://cdn.myanimelist.net/images/anime/1208/94745l.jpg"], "talles": ["s", "m", "l", "xl", "xxl"]},
    {"nombre": "Manga Tokyo Ghoul Vol. 1", "categoria": "Mangas", "precio": 8699.0, "stock": 24, "marca": "Ivrea", "descripcion": "Manga Tokyo Ghoul Vol. 1. Producto oficial de la franquicia Tokyo Ghoul.", "imagenes": ["https://cdn.myanimelist.net/images/manga/3/194456l.jpg"], "volumen": 1},
    {"nombre": "Remera Tokyo Ghoul - Máscara de Kaneki", "categoria": "Indumentaria", "precio": 12700.0, "stock": 16, "marca": "Crunchi Wear", "descripcion": "Remera Tokyo Ghoul - Máscara de Kaneki. Producto oficial de la franquicia Tokyo Ghoul.", "imagenes": ["https://cdn.myanimelist.net/images/anime/1498/134443l.jpg"], "talles": ["s", "m", "l", "xl", "xxl"]},
    {"nombre": "Manga Vinland Saga Vol. 1", "categoria": "Mangas", "precio": 10499.0, "stock": 20, "marca": "Panini", "descripcion": "Manga Vinland Saga Vol. 1. Producto oficial de la franquicia Vinland Saga.", "imagenes": ["https://cdn.myanimelist.net/images/manga/2/188925l.jpg"], "volumen": 1},
    {"nombre": "Manga Gintama Vol. 1", "categoria": "Mangas", "precio": 8199.0, "stock": 22, "marca": "Ivrea", "descripcion": "Manga Gintama Vol. 1. Producto oficial de la franquicia Gintama.", "imagenes": ["https://cdn.myanimelist.net/images/manga/3/267795l.jpg"], "volumen": 1},
    {"nombre": "Figura Sailor Moon", "categoria": "Figuras", "precio": 19999.0, "stock": 11, "marca": "Bandai", "descripcion": "Figura Sailor Moon. Producto oficial de la franquicia Sailor Moon.", "imagenes": ["https://cdn.myanimelist.net/images/anime/1440/92258l.jpg"]},
    {"nombre": "Remera Sailor Moon - Luna", "categoria": "Indumentaria", "precio": 12300.0, "stock": 19, "marca": "Crunchi Wear", "descripcion": "Remera Sailor Moon - Luna. Producto oficial de la franquicia Sailor Moon.", "imagenes": ["https://cdn.myanimelist.net/images/anime/1440/92258l.jpg"], "talles": ["s", "m", "l", "xl", "xxl"]},
    {"nombre": "Figura Shigeo Kageyama (Mob)", "categoria": "Figuras", "precio": 20499.0, "stock": 9, "marca": "Good Smile Company", "descripcion": "Figura Shigeo Kageyama (Mob). Producto oficial de la franquicia Mob Psycho 100.", "imagenes": ["https://cdn.myanimelist.net/images/anime/8/80356l.jpg"]},
]


def seed() -> None:
    mongo_db.productos.delete_many({})
    mongo_db.contadores.delete_one({"_id": "productos"})
    mongo_db.init_indexes()

    documentos = []
    for p in PRODUCTOS:
        nuevo_id = mongo_db.siguiente_id("productos")
        documentos.append({"id": nuevo_id, **p})

    if documentos:
        mongo_db.productos.insert_many(documentos)

    print(f"[seed_50] {len(documentos)} productos insertados en Mongo (db='{mongo_db.MONGO_DB}').")


if __name__ == "__main__":
    seed()
