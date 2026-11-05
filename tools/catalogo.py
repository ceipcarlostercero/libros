"""Prepara los libros del repositorio y genera libros.js.

Cada carpeta de la raíz con imágenes es un libro. Si sus páginas no están ya como
p000.webp, p001.webp... (p000 = portada):
  - las ordena por los números del nombre (p1, p2, ..., p10, no p1, p10, p2),
  - parte en dos las imágenes apaisadas (dobles páginas escaneadas juntas),
  - las convierte a webp con un alto máximo de 1800 px y las renombra.
Si la carpeta tiene acentos o espacios, la renombra (los coches mágicos -> los-coches-magicos)
y guarda el nombre original como título en libro.json, donde también se puede poner el autor.
"""
import json, os, re, shutil, statistics, sys, unicodedata
from PIL import Image, ImageOps

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXT = ('.jpg', '.jpeg', '.png', '.webp')
NORMAL = re.compile(r'^p\d{3}\.webp$')
ALTO_MAX = 1800

def slug(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')

def natural(s):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r'(\d+)', s)]

def preparar(carpeta):
    fs = sorted((f for f in os.listdir(carpeta) if f.lower().endswith(EXT)), key=natural)
    if all(NORMAL.match(f) for f in fs) and fs == ['p%03d.webp' % i for i in range(len(fs))]:
        return False
    tmp = os.path.join(carpeta, '.tmp'); os.makedirs(tmp, exist_ok=True)
    n = 0
    for f in fs:
        im = ImageOps.exif_transpose(Image.open(os.path.join(carpeta, f))).convert('RGB')
        w, h = im.size
        partes = [im.crop((0, 0, w // 2, h)), im.crop((w // 2, 0, w, h))] if w > h * 1.2 and n > 0 else [im]
        for p in partes:
            if p.height > ALTO_MAX:
                p = p.resize((round(p.width * ALTO_MAX / p.height), ALTO_MAX), Image.LANCZOS)
            p.save(os.path.join(tmp, 'p%03d.webp' % n), 'WEBP', quality=82, method=5)
            n += 1
    for f in fs: os.remove(os.path.join(carpeta, f))
    for f in os.listdir(tmp): shutil.move(os.path.join(tmp, f), os.path.join(carpeta, f))
    os.rmdir(tmp)
    print('preparado', carpeta, n, 'páginas')
    return True

def main():
    libros = []
    for nombre in sorted(os.listdir(RAIZ)):
        ruta = os.path.join(RAIZ, nombre)
        if nombre.startswith('.') or not os.path.isdir(ruta) or nombre == 'tools':
            continue
        if not any(f.lower().endswith(EXT) for f in os.listdir(ruta)):
            continue
        nombre = unicodedata.normalize('NFC', nombre)
        meta_f = os.path.join(ruta, 'libro.json')
        meta = json.load(open(meta_f, encoding='utf-8')) if os.path.exists(meta_f) else {}
        if 'titulo' not in meta:
            meta['titulo'] = nombre[0].upper() + nombre[1:] if slug(nombre) != nombre else nombre.replace('-', ' ').capitalize()
        ident = slug(nombre)
        if ident != os.path.basename(ruta):
            nueva = os.path.join(RAIZ, ident)
            os.rename(ruta, nueva); ruta = nueva
            print('renombrada', nombre, '->', ident)
        preparar(ruta)
        with open(os.path.join(ruta, 'libro.json'), 'w', encoding='utf-8') as fh:
            json.dump(meta, fh, ensure_ascii=False, indent=2); fh.write('\n')
        pags = sorted(f for f in os.listdir(ruta) if NORMAL.match(f))
        tam = [Image.open(os.path.join(ruta, f)).size for f in pags[1:] or pags]
        libro = {'id': ident, 'titulo': meta['titulo'], 'paginas': len(pags),
                 'ancho': round(statistics.median(t[0] for t in tam)), 'alto': round(statistics.median(t[1] for t in tam))}
        if meta.get('autor'): libro['autor'] = meta['autor']
        libros.append(libro)
    libros.sort(key=lambda b: natural(slug(b['titulo'])))
    with open(os.path.join(RAIZ, 'libros.js'), 'w', encoding='utf-8') as fh:
        fh.write('// GENERADO por tools/catalogo.py al subir libros: no editar a mano.\n'
                 '// Título y autor se cambian en libro.json, dentro de la carpeta de cada libro.\n')
        fh.write('var LIBROS = ' + json.dumps(libros, ensure_ascii=False, indent=2) + ';\n')

if __name__ == '__main__':
    sys.exit(main())
