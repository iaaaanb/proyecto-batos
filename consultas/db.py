"""Acceso a datos. Todo el SQL vive aquí.
Lectura por la conexión 'readonly' (webuser, solo SELECT).
Parámetros con %s = sentencias preparadas, seguras contra inyección.
Tablas y vistas calificadas con esquema public.
"""
from django.db import connections


def _consultar(sql, params=None):
    with connections["readonly"].cursor() as cursor:
        cursor.execute(sql, params or [])
        cols = [c[0] for c in cursor.description]
        return [dict(zip(cols, row)) for row in cursor.fetchall()]


# --- Consulta 1: distribución de ingreso por rama (vista materializada) ---
def distribucion_ingreso_rama():
    return _consultar("""
        SELECT rama, n_muestra, ingreso_promedio, p25, mediana, p75
        FROM public.mv_ingreso_rama
        ORDER BY ingreso_promedio DESC;
    """)


# --- Consulta 2: indicadores por región (vista materializada) ---
def indicadores_region():
    return _consultar("""
        SELECT region, ingreso_promedio, ingreso_mediano,
               tasa_ocupacion, tasa_participacion, pct_educacion_superior
        FROM public.mv_indicadores_region
        ORDER BY ingreso_promedio DESC;
    """)


# --- Para el menú desplegable de la consulta 3 ---
def listar_regiones():
    return _consultar(
        "SELECT cod_region, nombre FROM public.region ORDER BY nombre;"
    )


# --- Consulta 3: brecha salarial por sexo en una región (vista normal + índice) ---
def brecha_sexo_region(cod_region):
    return _consultar("""
        SELECT ne.descripcion AS nivel,
               ROUND((SUM(g.yoprcor*g.expr) FILTER (WHERE g.sexo=1)
                    / NULLIF(SUM(g.expr)    FILTER (WHERE g.sexo=1),0))::numeric) AS ing_hombres,
               ROUND((SUM(g.yoprcor*g.expr) FILTER (WHERE g.sexo=2)
                    / NULLIF(SUM(g.expr)    FILTER (WHERE g.sexo=2),0))::numeric) AS ing_mujeres,
               COUNT(*) FILTER (WHERE g.sexo=1) AS n_h,
               COUNT(*) FILTER (WHERE g.sexo=2) AS n_m
        FROM public.v_persona_geo g
        JOIN public.nivel_educacional ne ON g.codigo_nivel = ne.codigo
        WHERE g.cod_region = %s AND g.activ = 1 AND g.yoprcor IS NOT NULL
        GROUP BY ne.codigo, ne.descripcion
        ORDER BY ne.codigo;
    """, [cod_region])
