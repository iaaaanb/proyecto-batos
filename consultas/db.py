from django.db import connections


def _consultar(sql, params=None):

    with connections["readonly"].cursor() as cursor:
        cursor.execute(sql, params or [])
        columnas = [col[0] for col in cursor.description]
        return [dict(zip(columnas, fila)) for fila in cursor.fetchall()]


def personas_por_region():

    sql = """
        SELECT r.nombre AS region,
               COUNT(*)  AS personas
        FROM public.persona   p
        JOIN public.hogar     h  ON p.folio        = h.folio
        JOIN public.comuna    c  ON h.cod_comuna   = c.cod_comuna
        JOIN public.provincia pr ON c.cod_provincia = pr.cod_provincia
        JOIN public.region    r  ON pr.cod_region  = r.cod_region
        GROUP BY r.nombre
        ORDER BY personas DESC;
    """
    return _consultar(sql)

def listar_regiones():

    return _consultar(
        "SELECT cod_region, nombre FROM public.region ORDER BY nombre;"
    )


def ingreso_por_rama_en_region(cod_region):

    sql = """
        SELECT re.descripcion AS rama,
               ROUND( (SUM(p.yoprcor * h.expr) / SUM(h.expr))::numeric ) AS ingreso_promedio,
               COUNT(*) AS n_muestra
        FROM public.persona           p
        JOIN public.hogar             h   ON p.folio          = h.folio
        JOIN public.comuna            c   ON h.cod_comuna     = c.cod_comuna
        JOIN public.provincia         pr  ON c.cod_provincia  = pr.cod_provincia
        JOIN public.subrama_economica sre ON p.codigo_subrama = sre.codigo
        JOIN public.rama_economica    re  ON sre.codigo_rama  = re.codigo
        WHERE pr.cod_region = %s
          AND p.activ = 1
          AND p.yoprcor IS NOT NULL
        GROUP BY re.descripcion
        ORDER BY ingreso_promedio DESC;
    """
    return _consultar(sql, [cod_region])

def brecha_salarial_por_nivel(cod_region=None):

    sql = """
        SELECT ne.descripcion AS nivel,
               ROUND( (SUM(p.yoprcor * h.expr) FILTER (WHERE p.sexo = 1)
                     / NULLIF(SUM(h.expr)      FILTER (WHERE p.sexo = 1), 0))::numeric ) AS ingreso_hombres,
               ROUND( (SUM(p.yoprcor * h.expr) FILTER (WHERE p.sexo = 2)
                     / NULLIF(SUM(h.expr)      FILTER (WHERE p.sexo = 2), 0))::numeric ) AS ingreso_mujeres,
               COUNT(*) FILTER (WHERE p.sexo = 1) AS n_hombres,
               COUNT(*) FILTER (WHERE p.sexo = 2) AS n_mujeres
        FROM public.persona           p
        JOIN public.hogar             h  ON p.folio       = h.folio
        JOIN public.comuna            c  ON h.cod_comuna  = c.cod_comuna
        JOIN public.provincia         pr ON c.cod_provincia = pr.cod_provincia
        JOIN public.nivel_educacional ne ON p.codigo_nivel = ne.codigo
        WHERE p.activ = 1
          AND p.yoprcor IS NOT NULL
          AND (%s IS NULL OR pr.cod_region = %s)
        GROUP BY ne.codigo, ne.descripcion
        ORDER BY ne.codigo;
    """
    return _consultar(sql, [cod_region, cod_region])
