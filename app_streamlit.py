import io
import math
from dataclasses import dataclass
from typing import Dict, List, Literal, Tuple

import streamlit as st
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader

# -----------------------------
# Config
# -----------------------------
st.set_page_config(page_title="DISC Interno (Streamlit)", layout="wide")

LIKERT_MIN, LIKERT_MAX = 1, 5
Dim = Literal["D", "I", "S", "C", "V"]  # V = validez (opcional)

@dataclass(frozen=True)
class Item:
    id: str
    text: str
    dim: Dim
    reverse: bool = False

def get_items() -> List[Item]:
    return [
        # --- D ---
        Item("D01", "Tomo decisiones rápidamente incluso con información incompleta.", "D"),
        Item("D02", "Me siento cómodo asumiendo el control cuando hay incertidumbre.", "D"),
        Item("D03", "Me enfoco en resultados, aunque implique conversaciones difíciles.", "D"),
        Item("D04", "Disfruto competir y medir el rendimiento con metas claras.", "D"),
        Item("D05", "Cuando algo se estanca, presiono para avanzar.", "D"),
        Item("D06", "Prefiero actuar primero y ajustar sobre la marcha.", "D"),
        Item("D07", "Me frustra la lentitud en procesos o decisiones.", "D"),
        Item("D08", "Defiendo mi punto de vista con firmeza.", "D"),
        Item("D09", "Asumo riesgos calculados si el beneficio lo justifica.", "D"),
        Item("D10", "Evito confrontaciones aunque afecten el resultado.", "D", reverse=True),

        # --- I ---
        Item("I01", "Me energiza interactuar con personas y crear conexiones.", "I"),
        Item("I02", "Se me facilita influir y persuadir para alinear al equipo.", "I"),
        Item("I03", "Suelo expresar entusiasmo y motivar a otros.", "I"),
        Item("I04", "Prefiero conversaciones abiertas antes que mensajes fríos o formales.", "I"),
        Item("I05", "Me adapto rápido a ambientes nuevos y desconocidos.", "I"),
        Item("I06", "Me gusta contar historias o ejemplos para explicar ideas.", "I"),
        Item("I07", "Busco reconocimiento cuando logro algo importante.", "I"),
        Item("I08", "Me cuesta hablar en público o exponer mis ideas.", "I", reverse=True),
        Item("I09", "Prefiero decisiones que consideren el impacto en el clima del equipo.", "I"),
        Item("I10", "Me impaciento si la conversación es demasiado técnica y sin gente.", "I"),

        # --- S ---
        Item("S01", "Mantengo la calma y la constancia incluso bajo presión.", "S"),
        Item("S02", "Prefiero la estabilidad y la planificación gradual.", "S"),
        Item("S03", "Me esfuerzo por ayudar y apoyar a los demás de forma práctica.", "S"),
        Item("S04", "Valoro relaciones de trabajo armoniosas y colaborativas.", "S"),
        Item("S05", "Me siento cómodo con rutinas y procesos repetibles.", "S"),
        Item("S06", "Escucho con paciencia antes de responder.", "S"),
        Item("S07", "Me cuesta adaptarme cuando hay cambios repentinos.", "S"),
        Item("S08", "Prefiero evitar conflictos para mantener un buen ambiente.", "S"),
        Item("S09", "Me toma tiempo confiar; prefiero construir relaciones paso a paso.", "S"),
        Item("S10", "Me aburro si el trabajo es muy estable y predecible.", "S", reverse=True),

        # --- C ---
        Item("C01", "Reviso detalles y posibles errores antes de entregar.", "C"),
        Item("C02", "Me gusta trabajar con datos, criterios y evidencias.", "C"),
        Item("C03", "Prefiero estándares claros y consistentes para decidir.", "C"),
        Item("C04", "Cuestiono supuestos y busco la causa raíz.", "C"),
        Item("C05", "Me incomoda improvisar sin un plan o sin información suficiente.", "C"),
        Item("C06", "Me tomo en serio cumplir políticas, normas y procedimientos.", "C"),
        Item("C07", "Me cuesta delegar si no confío en la calidad del resultado.", "C"),
        Item("C08", "Antes de decidir, comparo alternativas de forma sistemática.", "C"),
        Item("C09", "Prefiero mensajes estructurados: objetivos, pasos, criterios.", "C"),
        Item("C10", "A menudo entrego sin revisar porque confío en mi primera versión.", "C", reverse=True),

        # --- Validez (opcional) ---
        Item("V01", "Nunca me equivoco en el trabajo.", "V"),
        Item("V02", "Siempre mantengo la calma, sin excepción.", "V"),
        Item("V03", "Jamás me distraigo; mi concentración es perfecta.", "V"),
        Item("V04", "Nunca he tenido un conflicto con nadie.", "V"),
        Item("V05", "Siempre cumplo todo a tiempo, incluso con múltiples urgencias.", "V"),
        Item("V06", "Mis decisiones siempre son objetivamente correctas.", "V"),
    ]

DIM_NAMES = {
    "D": "Dominancia",
    "I": "Influencia",
    "S": "Estabilidad",
    "C": "Conciencia (Consciencia)",
}

STRENGTHS = {
    "D": ["Orientación a resultados", "Decisión y rapidez", "Asertividad", "Capacidad para destrabar problemas"],
    "I": ["Comunicación persuasiva", "Energía social", "Motivación del equipo", "Networking y visibilidad"],
    "S": ["Constancia y paciencia", "Trabajo en equipo", "Escucha activa", "Estabilidad bajo presión"],
    "C": ["Precisión y calidad", "Análisis y criterio", "Gestión de riesgos", "Orden y estandarización"],
}
DEVELOP = {
    "D": ["Practicar escucha antes de decidir", "Bajar intensidad en confrontación", "Validar impactos en personas/proceso"],
    "I": ["Aterrizar ideas en planes medibles", "Gestionar dispersión", "Dar espacio a perfiles más reservados"],
    "S": ["Aumentar tolerancia al cambio", "Poner límites (evitar sobrecarga)", "Expresar desacuerdo a tiempo"],
    "C": ["Evitar perfeccionismo/parálisis por análisis", "Delegar con criterios claros", "Simplificar comunicación cuando se requiere velocidad"],
}

def blend_insights(primary: str, secondary: List[str]) -> List[str]:
    if not secondary:
        return [f"Perfil focalizado en {DIM_NAMES[primary]}: alto impacto si se ubica en roles alineados a esa prioridad."]
    combo = [primary] + secondary
    s = "-".join(combo)
    insights = [f"Blend {s}: el comportamiento puede variar según presión, rol y contexto."]
    if primary == "D" and "C" in secondary:
        insights.append("D-C: empuje por resultados con exigencia de calidad; riesgo: dureza y criticidad.")
    if primary == "I" and "S" in secondary:
        insights.append("I-S: cercanía y soporte; riesgo: evitar conflictos necesarios.")
    if primary == "C" and "S" in secondary:
        insights.append("C-S: estabilidad + precisión; riesgo: resistencia a cambios rápidos.")
    if primary == "D" and "I" in secondary:
        insights.append("D-I: influencia + acción; riesgo: decisiones impulsivas y baja escucha.")
    return insights

def reverse_score(x: int) -> int:
    return (LIKERT_MAX + LIKERT_MIN) - x

def score_disc(items: List[Item], answers: Dict[str, int],
               blend_ratio: float = 0.90,
               blend_abs: int = 2,
               validity_threshold: int = 24) -> Dict:
    dims = ["D", "I", "S", "C"]
    raw = {d: 0 for d in dims}
    validity = 0
    notes = []

    for it in items:
        x = answers[it.id]
        if it.reverse:
            x = reverse_score(x)
        if it.dim in raw:
            raw[it.dim] += x
        elif it.dim == "V":
            validity += x

    total = sum(raw.values())
    pct = {d: (raw[d] / total * 100.0) if total else 0.0 for d in dims}

    mean = sum(raw.values()) / 4.0
    var = sum((raw[d] - mean) ** 2 for d in dims) / 4.0
    sd = var ** 0.5 if var > 0 else 1.0
    z = {d: (raw[d] - mean) / sd for d in dims}

    ranked: List[Tuple[str, int]] = sorted(raw.items(), key=lambda kv: kv[1], reverse=True)
    primary = ranked[0][0]
    top_score = ranked[0][1]

    secondary = []
    for d, s in ranked[1:]:
        if (s >= top_score * blend_ratio) or ((top_score - s) <= blend_abs):
            secondary.append(d)

    spread = ranked[0][1] - ranked[-1][1]
    if spread <= 3:
        notes.append("Perfil poco diferenciado: puntajes muy cercanos entre dimensiones (posible estilo balanceado o respuestas neutras).")

    validity_flag = validity >= validity_threshold
    if validity_flag:
        notes.append("Alerta de validez: patrón de respuestas 'demasiado perfecto' (posible deseabilidad social).")

    if not secondary:
        notes.append(f"Estilo predominante: {primary}.")
    else:
        combo = "-".join([primary] + secondary)
        notes.append(f"Estilo combinado (blend): {combo}.")

    return {
        "raw": raw,
        "pct": pct,
        "z": z,
        "primary": primary,
        "secondary": secondary,
        "validity_score": validity,
        "validity_flag": validity_flag,
        "notes": notes,
    }

# -----------------------------
# Charts (in-memory PNG bytes)
# -----------------------------
def fig_to_png_bytes(fig) -> bytes:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=200, bbox_inches="tight")
    plt.close(fig)
    return buf.getvalue()

def bar_chart_bytes(raw: Dict[str, int]) -> bytes:
    dims = ["D", "I", "S", "C"]
    vals = [raw[d] for d in dims]
    fig = plt.figure()
    plt.title("DISC - Puntajes crudos")
    plt.bar(dims, vals)
    plt.xlabel("Dimensión")
    plt.ylabel("Puntaje")
    return fig_to_png_bytes(fig)

def radar_chart_bytes(pct: Dict[str, float]) -> bytes:
    dims = ["D", "I", "S", "C"]
    vals = [pct[d] for d in dims]
    vals += vals[:1]
    angles = [i * 2 * math.pi / 4 for i in range(4)]
    angles += angles[:1]

    fig = plt.figure()
    ax = plt.subplot(111, polar=True)
    ax.set_title("DISC - Diagrama de araña (0–100%)")
    ax.plot(angles, vals)
    ax.fill(angles, vals, alpha=0.15)
    ax.set_thetagrids([a * 180 / math.pi for a in angles[:-1]], dims)
    ax.set_ylim(0, 100)
    return fig_to_png_bytes(fig)

def quadrant_chart_bytes(z: Dict[str, float]) -> bytes:
    x = (z["D"] + z["I"]) - (z["S"] + z["C"])
    y = (z["D"] + z["C"]) - (z["I"] + z["S"])

    fig = plt.figure()
    plt.title("Mapa conductual (esquema)")
    plt.axhline(0)
    plt.axvline(0)
    plt.scatter([x], [y])
    plt.xlim(-4, 4)
    plt.ylim(-4, 4)
    plt.xlabel("Activo/Rápido  ←→  Estable/Metódico")
    plt.ylabel("Orientado a tarea  ←→  Orientado a personas")
    return fig_to_png_bytes(fig)

# -----------------------------
# PDF (in-memory)
# -----------------------------
def build_pdf_bytes(person_name: str, role: str, result: Dict,
                    img_bar: bytes, img_radar: bytes, img_quad: bytes) -> bytes:
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4
    y = height - 2 * cm

    def line(txt, dy=0.7 * cm, size=11, bold=False):
        nonlocal y
        c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
        c.drawString(2 * cm, y, txt)
        y -= dy

    raw, pct, z = result["raw"], result["pct"], result["z"]
    primary, secondary = result["primary"], result["secondary"]
    validity_score, notes = result["validity_score"], result["notes"]

    line("Informe DISC (uso interno)", size=16, bold=True, dy=1.0 * cm)
    line(f"Nombre: {person_name}", bold=True)
    line(f"Rol/Área: {role}")
    line(f"Resultado: Primario {primary} ({DIM_NAMES[primary]})" +
         (f" | Secundarios: {', '.join(secondary)}" if secondary else ""))
    line(f"Validez (0–30): {validity_score}" + ("  [ALERTA]" if result["validity_flag"] else ""))
    line("Notas:", bold=True)
    for n in notes:
        line(f"• {n}", size=10, dy=0.55 * cm)

    y -= 0.3 * cm
    line("Puntajes:", bold=True)
    line(f"Crudos: D={raw['D']}  I={raw['I']}  S={raw['S']}  C={raw['C']}", size=10, dy=0.55 * cm)
    line(f"% internos: D={pct['D']:.1f}  I={pct['I']:.1f}  S={pct['S']:.1f}  C={pct['C']:.1f}", size=10, dy=0.55 * cm)

    # Images
    y -= 0.4 * cm
    c.drawImage(ImageReader(io.BytesIO(img_bar)), 2 * cm, y - 6 * cm, width=16 * cm, height=5.5 * cm,
                preserveAspectRatio=True, anchor="nw")
    y -= 6.3 * cm
    c.drawImage(ImageReader(io.BytesIO(img_radar)), 2 * cm, y - 6 * cm, width=8 * cm, height=5.5 * cm,
                preserveAspectRatio=True, anchor="nw")
    c.drawImage(ImageReader(io.BytesIO(img_quad)), 10 * cm, y - 6 * cm, width=8 * cm, height=5.5 * cm,
                preserveAspectRatio=True, anchor="nw")
    y -= 6.3 * cm

    line("Virtudes (altas probabilidades):", bold=True)
    for s in STRENGTHS[primary]:
        line(f"• {s}", size=10, dy=0.55 * cm)

    y -= 0.2 * cm
    line("Puntos a trabajar (sugerencias):", bold=True)
    for d in DEVELOP[primary]:
        line(f"• {d}", size=10, dy=0.55 * cm)

    y -= 0.2 * cm
    line("Lectura del blend:", bold=True)
    for bi in blend_insights(primary, secondary):
        line(f"• {bi}", size=10, dy=0.55 * cm)

    c.showPage()
    c.save()
    return buf.getvalue()

# -----------------------------
# UI
# -----------------------------
st.title("DISC interno (Streamlit) — Cuestionario + Informe PDF")

with st.sidebar:
    st.subheader("Parámetros")
    blend_ratio = st.slider("Blend ratio (cercanía al top)", 0.70, 0.98, 0.90, 0.01)
    blend_abs = st.slider("Blend diferencia absoluta (puntos)", 0, 8, 2, 1)
    validity_threshold = st.slider("Umbral alerta validez (0–30)", 10, 30, 24, 1)

    st.caption("Likert: 1=Totalmente en desacuerdo … 5=Totalmente de acuerdo")

items = get_items()
by_dim = {"D": [], "I": [], "S": [], "C": [], "V": []}
for it in items:
    by_dim[it.dim].append(it)

colA, colB = st.columns([1, 1])
with colA:
    person_name = st.text_input("Nombre evaluado", value="")
with colB:
    role = st.text_input("Rol/Área", value="")

st.divider()

likert_labels = {
    1: "1 — Totalmente en desacuerdo",
    2: "2 — En desacuerdo",
    3: "3 — Neutral",
    4: "4 — De acuerdo",
    5: "5 — Totalmente de acuerdo",
}

def render_dim_block(title: str, dim: str):
    st.subheader(title)
    for it in by_dim[dim]:
        st.selectbox(
            f"[{it.id}] {it.text}" + (" (invertida)" if it.reverse else ""),
            options=[1, 2, 3, 4, 5],
            format_func=lambda x: likert_labels[x],
            key=f"ans_{it.id}",
            index=2  # default 3 neutral
        )

with st.form("disc_form"):
    c1, c2 = st.columns(2)
    with c1:
        with st.expander("D — Dominancia", expanded=True):
            render_dim_block("Dominancia (D)", "D")
        with st.expander("S — Estabilidad", expanded=False):
            render_dim_block("Estabilidad (S)", "S")

    with c2:
        with st.expander("I — Influencia", expanded=True):
            render_dim_block("Influencia (I)", "I")
        with st.expander("C — Conciencia", expanded=False):
            render_dim_block("Conciencia (C)", "C")

    with st.expander("Validez (opcional)", expanded=False):
        render_dim_block("Validez (V)", "V")

    submitted = st.form_submit_button("Calcular resultados y generar informe")

if submitted:
    if not person_name.strip():
        person_name = "N/A"
    if not role.strip():
        role = "N/A"

    answers = {it.id: int(st.session_state[f"ans_{it.id}"]) for it in items}

    result = score_disc(
        items, answers,
        blend_ratio=float(blend_ratio),
        blend_abs=int(blend_abs),
        validity_threshold=int(validity_threshold)
    )

    st.success("Resultados calculados.")

    # Charts
    img_bar = bar_chart_bytes(result["raw"])
    img_radar = radar_chart_bytes(result["pct"])
    img_quad = quadrant_chart_bytes(result["z"])

    # Display
    left, right = st.columns([1.2, 1])
    with left:
        st.subheader("Resumen")
        st.write(
            f"**Primario:** {result['primary']} ({DIM_NAMES[result['primary']]})  \n"
            + (f"**Secundarios:** {', '.join(result['secondary'])}" if result["secondary"] else "**Secundarios:** —")
        )
        st.write(f"**Validez (0–30):** {result['validity_score']}" + (" ⚠️" if result["validity_flag"] else ""))

        st.markdown("**Notas:**")
        for n in result["notes"]:
            st.write(f"- {n}")

        st.markdown("**Puntajes crudos (suma):**")
        st.json(result["raw"])
        st.markdown("**% internos (0–100):**")
        st.json({k: round(v, 1) for k, v in result["pct"].items()})

    with right:
        st.subheader("Gráficas")
        st.image(img_bar, caption="Barras — Puntajes crudos")
        st.image(img_radar, caption="Araña — % internos")
        st.image(img_quad, caption="Mapa conductual (esquema)")

    st.divider()
    st.subheader("Virtudes y puntos a trabajar (según primario)")
    p = result["primary"]
    c3, c4 = st.columns(2)
    with c3:
        st.markdown("**Virtudes**")
        for s in STRENGTHS[p]:
            st.write(f"- {s}")
    with c4:
        st.markdown("**Puntos a trabajar**")
        for d in DEVELOP[p]:
            st.write(f"- {d}")

    st.markdown("**Lectura del blend**")
    for bi in blend_insights(result["primary"], result["secondary"]):
        st.write(f"- {bi}")

    # PDF
    pdf_bytes = build_pdf_bytes(person_name, role, result, img_bar, img_radar, img_quad)

    st.download_button(
        label="Descargar informe PDF",
        data=pdf_bytes,
        file_name=f"informe_DISC_{person_name.replace(' ', '_')}.pdf",
        mime="application/pdf",
    )
