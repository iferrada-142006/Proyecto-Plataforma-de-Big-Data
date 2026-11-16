"""Perfilamiento de los datos entregados (E1, anexo E).

La E1 no exige programar; este script solo respalda las cifras de volumen y
calidad citadas en el informe. Lee los datos tal como vienen de Canvas desde
datos/ (ver datos/README.md) y no modifica nada.

Uso (desde la raíz del repositorio):
    pip install duckdb
    python entregas/E1/anexos/perfilamiento.py
"""

import os
import tempfile
from pathlib import Path

import duckdb

RAIZ = Path(__file__).resolve().parents[3]
DATOS = RAIZ / "datos"
RECETAS = DATOS / "foodcom" / "recipes.parquet"
RESENAS = DATOS / "foodcom" / "reviews.parquet"
DISPOSITIVOS = DATOS / "wearable" / "dispositivos.csv"
COMIDAS = DATOS / "wearable" / "comidas.csv"
SESIONES = DATOS / "wearable" / "sesiones.jsonl"
MEDICIONES = DATOS / "wearable" / "mediciones" / "*" / "*.jsonl.gz"

# Los dos modelos de reloj usan nombres distintos; se leen todas las columnas
# posibles y se unifican con COALESCE (schema-on-read).
COLUMNAS_MEDICION = {
    "device_id": "VARCHAR", "ts_medicion": "VARCHAR", "ts_recepcion": "VARCHAR",
    "frecuencia_cardiaca": "INTEGER", "pasos": "INTEGER", "calorias": "DOUBLE",
    "dev": "VARCHAR", "timestamp": "BIGINT", "received_at": "VARCHAR",
    "fc": "INTEGER", "steps": "INTEGER", "kcal": "DOUBLE",
}


def mostrar(con, titulo, sql):
    rel = con.sql(sql)
    print(f"\n## {titulo}")
    print(" | ".join(rel.columns))
    for fila in rel.fetchall():
        print(" | ".join(str(v) for v in fila))


def main():
    # Base en disco para no agotar la memoria con 15,5 M de mediciones.
    tmp = Path(tempfile.mkdtemp()) / "perfil.duckdb"
    con = duckdb.connect(str(tmp))
    con.sql("SET TimeZone='UTC'; SET preserve_insertion_order=false")

    mostrar(con, "Recetas", f"""
        SELECT count(*) filas, count(DISTINCT RecipeCategory) categorias,
               count(*) FILTER (WHERE Calories > 5000) kcal_porcion_gt_5000,
               count(*) FILTER (WHERE RecipeServings IS NULL) sin_porciones,
               typeof(any_value(RecipeId)) tipo_recipeid
        FROM '{RECETAS}'""")

    mostrar(con, "Reseñas", f"""
        SELECT count(*) filas, count(DISTINCT AuthorId) usuarios,
               count(*) FILTER (WHERE Rating = 0) rating_cero,
               min(DateSubmitted)::VARCHAR desde, max(DateSubmitted)::VARCHAR hasta
        FROM '{RESENAS}'""")

    mostrar(con, "Dispositivos", f"""
        SELECT modelo, count(*) relojes, count(DISTINCT AuthorId) usuarios,
               count(fecha_desvinculacion) desvinculados,
               count(*) FILTER (WHERE AuthorId NOT IN (SELECT AuthorId FROM '{RESENAS}')) sin_resenas
        FROM '{DISPOSITIVOS}' GROUP BY 1""")

    mostrar(con, "Comidas", f"""
        SELECT count(*) filas, count(DISTINCT AuthorId) usuarios,
               count(*) - count(DISTINCT comida_id) ids_repetidos,
               count(*) FILTER (WHERE RecipeId NOT IN (SELECT RecipeId FROM '{RECETAS}')) receta_inexistente,
               min(porciones) min_porciones, max(porciones) max_porciones
        FROM '{COMIDAS}'""")

    mostrar(con, "Sesiones", f"""
        SELECT count(*) filas, count(DISTINCT session_id) sesiones_unicas,
               count(*) - (SELECT count(*) FROM (SELECT DISTINCT * FROM read_json_auto('{SESIONES}'))) duplicadas_identicas,
               count(*) FILTER (WHERE tipo = 'fuerza' AND distancia_km IS NULL) fuerza_sin_distancia
        FROM read_json_auto('{SESIONES}')""")

    cols = "{" + ", ".join(f"{k}: '{v}'" for k, v in COLUMNAS_MEDICION.items()) + "}"
    con.sql(f"""
        CREATE TABLE medicion AS
        SELECT coalesce(device_id, dev) device_id,
               coalesce(ts_medicion::TIMESTAMP, make_timestamp(timestamp * 1000)) ts_medicion,
               coalesce(ts_recepcion, received_at)::TIMESTAMP ts_recepcion,
               coalesce(frecuencia_cardiaca, fc) fc,
               coalesce(pasos, steps) pasos,
               coalesce(calorias, kcal) kcal,
               CASE WHEN dev IS NULL THEN 'Pulso S' ELSE 'FitBand 2' END formato
        FROM read_json('{MEDICIONES}', columns = {cols}, format = 'newline_delimited')""")

    mostrar(con, "Mediciones por formato", """
        SELECT formato, count(*) filas, count(*) - count(fc) fc_nula,
               count(*) FILTER (WHERE fc < 30 OR fc > 220) fc_fuera_rango,
               min(ts_medicion)::VARCHAR desde, max(ts_medicion)::VARCHAR hasta
        FROM medicion GROUP BY 1""")

    mostrar(con, "Mediciones repetidas", """
        SELECT count(*) - (SELECT count(*) FROM (SELECT DISTINCT device_id, ts_medicion FROM medicion)) repetidas_por_clave,
               (SELECT count(*) FROM (SELECT device_id, ts_medicion FROM medicion GROUP BY ALL
                  HAVING count(DISTINCT fc) > 1 OR count(DISTINCT pasos) > 1)) repetidas_con_valores_distintos
        FROM medicion""")

    mostrar(con, "Atraso de recepción (ts_recepcion - ts_medicion)", """
        SELECT quantile_cont(epoch(ts_recepcion - ts_medicion) / 60, 0.5) p50_min,
               quantile_cont(epoch(ts_recepcion - ts_medicion) / 60, 0.9) p90_min,
               max(epoch(ts_recepcion - ts_medicion)) / 3600 max_horas,
               round(100.0 * count(*) FILTER (WHERE ts_recepcion - ts_medicion > INTERVAL 3 HOUR) / count(*), 2) pct_mas_3h,
               round(100.0 * count(*) FILTER (WHERE ts_recepcion - ts_medicion > INTERVAL 1 DAY) / count(*), 2) pct_mas_24h
        FROM medicion""")

    mostrar(con, "Ritmo de llegada", """
        SELECT count(DISTINCT ts_recepcion::DATE) dias,
               count(*) // count(DISTINCT ts_recepcion::DATE) filas_por_dia,
               count(DISTINCT (device_id, ts_recepcion)) lotes,
               count(*) // count(DISTINCT (device_id, ts_recepcion)) filas_por_lote
        FROM medicion""")

    con.close()
    os.remove(tmp)


if __name__ == "__main__":
    main()
