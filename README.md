# Biblioteca · C.E.I.P. Carlos III

Lector de libros en https://ceipcarlostercero.github.io/libros/

## Añadir un libro

1. Sube una carpeta con las páginas escaneadas (jpg, png o webp), con el nombre del libro.
   La primera imagen es la portada. Da igual cómo se llamen: se ordenan por el número del nombre (p1, p2… p10).
2. Al subirla, la acción **Preparar libros** (`tools/catalogo.py`) en uno o dos minutos:
   - ordena y renombra las páginas a `p000.webp`, `p001.webp`…, y las convierte a webp más ligero;
   - parte en dos las imágenes apaisadas (dobles páginas escaneadas de una vez);
   - renombra la carpeta sin acentos ni espacios y guarda el título en `libro.json`;
   - añade el libro al catálogo (`libros.js`).
3. Para cambiar el título o poner el autor, edita `libro.json` dentro de la carpeta del libro.
