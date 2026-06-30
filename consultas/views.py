from django.shortcuts import render
from django.http import HttpResponse
from . import db


def personas_por_region(request):
    filas = db.personas_por_region()
    return render(request, "consultas/personas_por_region.html", {
        "filas": filas,
    })

def ingreso_por_rama(request):
    regiones = db.listar_regiones()
    cod = request.GET.get("region")
    contexto = {"regiones": regiones, "seleccion": cod}
    if cod:
        try:
            cod_int = int(cod)
        except ValueError:
            contexto["error"] = "Región inválida."
        else:
            contexto["filas"] = db.ingreso_por_rama_en_region(cod_int)
            contexto["region_nombre"] = next(
                (r["nombre"] for r in regiones if r["cod_region"] == cod_int), None
            )
    return render(request, "consultas/ingreso_por_rama.html", contexto)

def brecha_salarial(request):
    regiones = db.listar_regiones()
    cod = request.GET.get("region") or ""
    contexto = {"regiones": regiones, "seleccion": cod}

    cod_int = None
    if cod:
        try:
            cod_int = int(cod)
        except ValueError:
            contexto["error"] = "Región inválida."
            return render(request, "consultas/brecha_salarial.html", contexto)

    filas = db.brecha_salarial_por_nivel(cod_int)
    for f in filas:
        h, m = f["ingreso_hombres"], f["ingreso_mujeres"]
        f["razon"] = round(100 * m / h, 1) if h and m else None
    contexto["filas"] = filas
    if cod_int is not None:
        contexto["region_nombre"] = next(
            (r["nombre"] for r in regiones if r["cod_region"] == cod_int), None
        )
    return render(request, "consultas/brecha_salarial.html", contexto)
