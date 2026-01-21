# app_cli.py
import os
from questionnaire import get_items
from scoring import score_disc
from charts import bar_chart, radar_chart, quadrant_chart
from report_pdf import build_pdf

def ask_likert(prompt: str) -> int:
    while True:
        try:
            x = int(input(prompt))
            if 1 <= x <= 5:
                return x
        except:
            pass
        print("Ingresa un número 1–5.")

def main():
    items = get_items()
    print("DISC (1–5): 1=Totalmente en desacuerdo ... 5=Totalmente de acuerdo\n")

    person = input("Nombre evaluado: ").strip() or "N/A"
    role = input("Rol/Área: ").strip() or "N/A"

    answers = {}
    for it in items:
        if it.dim == "V":
            # opcional: puedes preguntar también validez; aquí sí la preguntamos.
            pass
        q = f"[{it.id}] {it.text}\n  1 2 3 4 5 -> "
        answers[it.id] = ask_likert(q)

    res = score_disc(items, answers)

    os.makedirs("out", exist_ok=True)
    img_bar = "out/disc_bar.png"
    img_radar = "out/disc_radar.png"
    img_quad = "out/disc_quadrant.png"
    out_pdf = "out/informe_disc.pdf"

    bar_chart(res.raw, img_bar)
    radar_chart(res.pct, img_radar)
    quadrant_chart(res.z, img_quad)

    build_pdf(
        out_pdf=out_pdf,
        person_name=person,
        role=role,
        raw=res.raw, pct=res.pct, z=res.z,
        primary=res.primary, secondary=res.secondary,
        validity_score=res.validity_score,
        notes=res.notes,
        img_bar=img_bar, img_radar=img_radar, img_quad=img_quad
    )

    print("\nRESULTADOS")
    print("Raw:", res.raw)
    print("Pct:", {k: round(v, 1) for k, v in res.pct.items()})
    print("Primary:", res.primary, "Secondary:", res.secondary)
    print("Validez:", res.validity_score, "Flag:", res.validity_flag)
    print("\nPDF generado:", out_pdf)

if __name__ == "__main__":
    main()
