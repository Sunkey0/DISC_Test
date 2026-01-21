# report_pdf.py
from typing import List
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

from interpretation import DIM_NAMES, STRENGTHS, DEVELOP, blend_insights

def build_pdf(out_pdf: str,
              person_name: str,
              role: str,
              raw: dict, pct: dict, z: dict,
              primary: str, secondary: List[str],
              validity_score: int, notes: List[str],
              img_bar: str, img_radar: str, img_quad: str) -> None:
    c = canvas.Canvas(out_pdf, pagesize=A4)
    width, height = A4
    y = height - 2*cm

    def line(txt, dy=0.7*cm, size=11, bold=False):
        nonlocal y
        c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
        c.drawString(2*cm, y, txt)
        y -= dy

    # Header
    line("Informe DISC (uso interno)", size=16, bold=True, dy=1.0*cm)
    line(f"Nombre: {person_name}", bold=True)
    line(f"Rol/Área: {role}")
    line(f"Resultado: Primario {primary} ({DIM_NAMES[primary]})" +
         (f" | Secundarios: {', '.join(secondary)}" if secondary else ""))
    line(f"Validez (0–30): {validity_score}" + ("  [ALERTA]" if any("Alerta de validez" in n for n in notes) else ""))
    line("Notas:", bold=True)
    for n in notes:
        line(f"• {n}", size=10, dy=0.55*cm)

    y -= 0.3*cm
    line("Puntajes:", bold=True)
    line(f"Crudos: D={raw['D']}  I={raw['I']}  S={raw['S']}  C={raw['C']}", size=10, dy=0.55*cm)
    line(f"% internos: D={pct['D']:.1f}  I={pct['I']:.1f}  S={pct['S']:.1f}  C={pct['C']:.1f}", size=10, dy=0.55*cm)

    # Images
    y -= 0.4*cm
    c.drawImage(img_bar, 2*cm, y-6*cm, width=16*cm, height=5.5*cm, preserveAspectRatio=True, anchor='nw')
    y -= 6.3*cm
    c.drawImage(img_radar, 2*cm, y-6*cm, width=8*cm, height=5.5*cm, preserveAspectRatio=True, anchor='nw')
    c.drawImage(img_quad, 10*cm, y-6*cm, width=8*cm, height=5.5*cm, preserveAspectRatio=True, anchor='nw')
    y -= 6.3*cm

    # Strengths & Development
    line("Virtudes (altas probabilidades):", bold=True)
    for s in STRENGTHS[primary]:
        line(f"• {s}", size=10, dy=0.55*cm)

    y -= 0.2*cm
    line("Puntos a trabajar (sugerencias):", bold=True)
    for d in DEVELOP[primary]:
        line(f"• {d}", size=10, dy=0.55*cm)

    y -= 0.2*cm
    line("Lectura del blend:", bold=True)
    for bi in blend_insights(primary, secondary):
        line(f"• {bi}", size=10, dy=0.55*cm)

    c.showPage()
    c.save()
