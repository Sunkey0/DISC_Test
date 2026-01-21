import math
from typing import Dict, Tuple
import matplotlib.pyplot as plt

def bar_chart(raw: Dict[str, int], out_png: str) -> None:
    dims = ["D", "I", "S", "C"]
    vals = [raw[d] for d in dims]
    plt.figure()
    plt.title("DISC - Puntajes crudos")
    plt.bar(dims, vals)
    plt.xlabel("Dimensión")
    plt.ylabel("Puntaje")
    plt.tight_layout()
    plt.savefig(out_png, dpi=200)
    plt.close()

def radar_chart(pct: Dict[str, float], out_png: str) -> None:
    dims = ["D", "I", "S", "C"]
    vals = [pct[d] for d in dims]
    # cerrar el polígono
    vals += vals[:1]
    angles = [i * 2 * math.pi / 4 for i in range(4)]
    angles += angles[:1]

    plt.figure()
    ax = plt.subplot(111, polar=True)
    ax.set_title("DISC - Diagrama de araña (0–100%)")
    ax.plot(angles, vals)
    ax.fill(angles, vals, alpha=0.15)
    ax.set_thetagrids([a * 180 / math.pi for a in angles[:-1]], dims)
    ax.set_ylim(0, 100)
    plt.tight_layout()
    plt.savefig(out_png, dpi=200)
    plt.close()

def quadrant_chart(z: Dict[str, float], out_png: str) -> None:
    """
    Cuadrante típico: eje X = (D + I) - (S + C)   (rápido/activo vs estable/analítico)
                      eje Y = (D + C) - (I + S)   (tarea vs personas)  (aprox.)
    Esto es un esquema interno (no estándar universal), pero sirve para visual.
    """
    x = (z["D"] + z["I"]) - (z["S"] + z["C"])
    y = (z["D"] + z["C"]) - (z["I"] + z["S"])

    plt.figure()
    plt.title("Mapa conductual (esquema)")
    plt.axhline(0)
    plt.axvline(0)
    plt.scatter([x], [y])
    plt.xlim(-4, 4)
    plt.ylim(-4, 4)
    plt.xlabel("Activo/Rápido  ←→  Estable/Metódico")
    plt.ylabel("Orientado a tarea  ←→  Orientado a personas")
    plt.tight_layout()
    plt.savefig(out_png, dpi=200)
    plt.close()
