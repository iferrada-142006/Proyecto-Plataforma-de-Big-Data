# ¿Qué ceno hoy? · Recetas y wearables

Proyecto del curso **INF3862 · Plataformas Big Data para Data Science** (Magíster en Inteligencia Artificial UC).

**Integrantes:** Sebastián Muñoz · Ignacio Ferrada

## Caso de uso

Una app de recetas basada en Food.com se integra con relojes inteligentes. Nuestro producto de datos es un
**recomendador de cena**: cada día, a las 17:30 hora local, la app sugiere cinco recetas acordes al
**balance energético del día** del usuario, es decir, las kcal gastadas según el reloj menos las kcal consumidas
según las comidas que registró. También considera el tipo de actividad (más proteína después de correr o de una
sesión de fuerza) y las recetas que el usuario cocinó y calificó bien antes.

Combina el wearable (mediciones, sesiones, comidas, dispositivos) con Food.com (recetas y reseñas).

## Entregables

| Entrega | Fecha | Contenido |
|---|---|---|
| **E1 · Diseño de datos** | 16-11-2026 | [Informe PDF](entregas/E1/informe.pdf) · [fuente HTML](entregas/E1/fuente/informe.html) · [anexos](entregas/E1/anexos/) |
| E2 · Ingesta y procesamiento | 30-11-2026 | pendiente |
| E3 · Datos para ML y arquitectura final | 14-12-2026 | pendiente |

Registro de decisiones: [decisiones.md](decisiones.md).

### E1 en breve

- **Objetivo** respondido con las cinco preguntas de la Clase 0.
- **Fuentes**: volumen, modo de recepción, problemas observados y elección entre schema-on-read y schema-on-write para cada una.
- **OLTP**: modelo relacional para usuarios, recetas, reseñas, comidas, vinculaciones y sesiones; series temporales para las
  mediciones; clave-valor para la recomendación del día. Regla transaccional: un reloj activo por usuario y un usuario por reloj.
- **OLAP**: `fact_balance_diario` (una fila por usuario y día local) y `fact_comida` (una fila por comida), con cinco
  dimensiones. Lakehouse bronce, plata y oro con tablas Delta sobre Parquet, particionado por fecha de medición.
- **Consultas**: 3 OLTP, 3 OLAP y 1 de frontera, en pseudocódigo SQL.
- **Arquitectura inicial** por capacidades, sin productos.

La E1 no exige programar. El script [`entregas/E1/anexos/perfilamiento.py`](entregas/E1/anexos/perfilamiento.py)
solo respalda las cifras de volumen y calidad del informe. Su salida está en
[`perfilamiento_salida.txt`](entregas/E1/anexos/perfilamiento_salida.txt).

## Estructura del repositorio

```
README.md
decisiones.md          registro de decisiones (sección 7 del enunciado)
datos/README.md        cómo obtener los datos desde Canvas (no se versionan)
entregas/
  E1/
    informe.pdf        informe (3 páginas + anexos A–E)
    fuente/            HTML del informe y sus diagramas (SVG)
    anexos/            script de perfilamiento y su salida
```

Desde la E2 se agregarán `pyproject.toml` y `uv.lock`, para preparar el entorno con `uv sync` y ejecutar con `uv run`,
además de `src/` y las carpetas `entregas/E2` y `entregas/E3`.

## Reproducir el perfilamiento de la E1

1. Descarga los datos según [datos/README.md](datos/README.md).
2. Desde la raíz del repositorio:

```bash
pip install duckdb
python entregas/E1/anexos/perfilamiento.py
```

Tarda unos minutos: lee las 15,5 M de mediciones comprimidas con DuckDB.

## Regenerar el PDF del informe

El informe se escribe en `entregas/E1/fuente/informe.html` y se imprime a PDF con Chrome o Edge en modo headless:

```bash
chrome --headless=new --no-pdf-header-footer --print-to-pdf=entregas/E1/informe.pdf entregas/E1/fuente/informe.html
```

## Fuentes de datos

- Food.com - Recipes and Reviews (Kaggle, licencia CC0): https://www.kaggle.com/datasets/irkaal/foodcom-recipes-and-reviews
- Wearable: datos sintéticos creados por el equipo docente del curso (Canvas).
