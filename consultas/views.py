from django.shortcuts import render
from . import db


def inicio(request):
    return render(request, "consultas/inicio.html")


def distribucion_rama(request):
    regiones = db.listar_regiones()
    cod = request.GET.get("region") or ""
    ctx = {"regiones": regiones, "seleccion": cod}
    if cod:
        try:
            cod_int = int(cod)
        except ValueError:
            ctx["error"] = "Región inválida."
            return render(request, "consultas/distribucion_rama.html", ctx)
        ctx["filas"] = db.distribucion_ingreso_rama_region(cod_int)
        ctx["region_nombre"] = next(
            (r["nombre"] for r in regiones if r["cod_region"] == cod_int), None
        )
    else:
        ctx["filas"] = db.distribucion_ingreso_rama()
        ctx["region_nombre"] = None
    return render(request, "consultas/distribucion_rama.html", ctx)


def indicadores(request):
    filas = db.indicadores_region()
    return render(request, "consultas/indicadores.html", {"filas": filas})


def brecha(request):
    regiones = db.listar_regiones()
    cod = request.GET.get("region") or ""
    ctx = {"regiones": regiones, "seleccion": cod}
    if cod:
        try:
            cod_int = int(cod)
        except ValueError:
            ctx["error"] = "Región inválida."
            return render(request, "consultas/brecha.html", ctx)
        filas = db.brecha_sexo_region(cod_int)
        for f in filas:  # razón mujer/hombre en %
            h, m = f["ing_hombres"], f["ing_mujeres"]
            f["razon"] = round(100 * m / h, 1) if h and m else None
        ctx["filas"] = filas
        ctx["region_nombre"] = next(
            (r["nombre"] for r in regiones if r["cod_region"] == cod_int), None
        )
    return render(request, "consultas/brecha.html", ctx)
