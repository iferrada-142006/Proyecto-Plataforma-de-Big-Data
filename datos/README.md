# Datos

Los datos no se versionan en el repositorio (≈450 MB). Se descargan desde Canvas del curso.

## Cómo obtenerlos

1. En Canvas (INF3862 → Archivos), descarga el archivo de datos del proyecto.
2. Descomprime y copia las carpetas `foodcom/` y `wearable/` dentro de esta carpeta `datos/`.

La estructura esperada es:

```
datos/
  foodcom/
    recipes.parquet        522.517 recetas (171 MB)
    reviews.parquet        1.401.982 reseñas (166 MB)
  wearable/
    dispositivos.csv       315 relojes
    comidas.csv            22.106 comidas registradas
    sesiones.jsonl         4.840 sesiones de actividad
    LEEME.md               diccionario de datos del wearable
    mediciones/
      AAAA-MM-DD/HH.jsonl.gz   1.449 archivos, 15,5 M mediciones (114 MB)
```

## Relaciones entre fuentes

- `wearable/dispositivos.csv` → `AuthorId` es el usuario de `foodcom/reviews.parquet`.
- `wearable/comidas.csv` → `AuthorId` (usuario) y `RecipeId` (receta de `foodcom/recipes.parquet`).
- En `foodcom/recipes.parquet`, `AuthorId` es el autor de la receta, no quien la cocina o la reseña.
- Todas las fechas del wearable están en UTC; `zona_horaria` (en `dispositivos.csv`) permite pasar a hora local.

## Muestra para la E2

La E1 usa los datos completos solo para perfilarlos. La selección de la muestra (por ejemplo, un subconjunto de
usuarios o algunas semanas de mediciones) se documentará aquí en la E2.
