import io
import math
import time
import random
from dataclasses import dataclass
from typing import Dict, List, Literal, Tuple

import streamlit as st
import matplotlib.pyplot as plt

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
)

# -----------------------------
# Config (sin parámetros visibles)
# -----------------------------
st.set_page_config(page_title="DISC — Cuestionario + Informe", layout="wide")

LIKERT_MIN, LIKERT_MAX = 1, 5
Dim = Literal["D", "I", "S", "C", "V"]

# Defaults internos (no se muestran)
BLEND_RATIO_DEFAULT = 0.90
BLEND_ABS_DEFAULT = 2
VALIDITY_THRESHOLD_DEFAULT = 24  # 6 ítems * max 5 = 30

# Colores internos (solo para resultados/informe)
COLOR_HEX = {
    "D": "#E53935",  # Rojo
    "I": "#FBC02D",  # Amarillo
    "S": "#43A047",  # Verde
    "C": "#1E88E5",  # Azul
    "V": "#6D6D6D",
}
COLOR_NAME = {"D": "Rojo", "I": "Amarillo", "S": "Verde", "C": "Azul"}

DIM_NAMES = {
    "D": "Dominancia",
    "I": "Influencia",
    "S": "Estabilidad",
    "C": "Cumplimiento / Conciencia",
}

LIKERT_LABELS = {
    1: "1 — Totalmente en desacuerdo",
    2: "2 — En desacuerdo",
    3: "3 — Neutral",
    4: "4 — De acuerdo",
    5: "5 — Totalmente de acuerdo",
}
LIKERT_EMOJI = {1: "😟", 2: "🙁", 3: "😐", 4: "🙂", 5: "😄"}

# -----------------------------
# Cuestionario
# -----------------------------
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

        # --- Validez (mezcladas, no visibles como tal) ---
        Item("V01", "Nunca me equivoco en el trabajo.", "V"),
        Item("V02", "Siempre mantengo la calma, sin excepción.", "V"),
        Item("V03", "Jamás me distraigo; mi concentración es perfecta.", "V"),
        Item("V04", "Nunca he tenido un conflicto con nadie.", "V"),
        Item("V05", "Siempre cumplo todo a tiempo, incluso con múltiples urgencias.", "V"),
        Item("V06", "Mis decisiones siempre son objetivamente correctas.", "V"),
    ]

# -----------------------------
# Interpretación (resumen)
# -----------------------------
STRENGTHS = {
    "D": ["Orientación a resultados", "Decisión y rapidez", "Asertividad", "Capacidad para destrabar problemas"],
    "I": ["Comunicación persuasiva", "Energía social", "Motivación del equipo", "Networking y visibilidad"],
    "S": ["Constancia y paciencia", "Trabajo en equipo", "Escucha activa", "Estabilidad bajo presión"],
    "C": ["Precisión y calidad", "Análisis y criterio", "Gestión de riesgos", "Orden y estandarización"],
}
RISKS = {
    "D": ["Puede sonar duro o impaciente", "Riesgo de decidir sin suficiente alineación", "Subestimar impactos emocionales"],
    "I": ["Riesgo de dispersión", "Sobre-optimismo sin plan", "Puede evitar detalles o seguimiento"],
    "S": ["Resistencia a cambios bruscos", "Evita conflicto aunque sea necesario", "Dificultad para decir 'no'"],
    "C": ["Perfeccionismo / parálisis por análisis", "Rigidez con reglas", "Dificultad para delegar"],
}
UNDER_PRESSURE = {
    "D": ["Acelera y controla", "Exige respuestas rápidas", "Tolera menos la ambigüedad social"],
    "I": ["Habla más y busca apoyo social", "Puede saltar entre temas", "Se frustra con lo muy técnico"],
    "S": ["Se retrae y busca estabilidad", "Puede postergar decisiones", "Prioriza armonía sobre fricción útil"],
    "C": ["Aumenta la revisión y control", "Pide evidencia/criterios", "Puede frenar velocidad del equipo"],
}
MANAGER_TIPS = {
    "D": ["Acordar metas y autoridad claras", "Ir a lo concreto: impacto/ROI/tiempos", "Dar opciones (A/B) y pedir decisión"],
    "I": ["Reconocer logros cuando aplique", "Aterrizar con fechas/propietarios", "Usar ejemplos e impacto en personas"],
    "S": ["Dar contexto y tiempo de transición", "Asegurar estabilidad en prioridades", "Cerrar acuerdos por escrito"],
    "C": ["Entregar datos, criterios y definición de 'hecho'", "Acordar umbrales para decidir", "Evitar improvisación sin plan"],
}

def blend_label(primary: str, secondary: List[str]) -> str:
    return primary if not secondary else "-".join([primary] + secondary)

def blend_insights(primary: str, secondary: List[str]) -> List[str]:
    if not secondary:
        return [f"Predomina {DIM_NAMES[primary]} ({COLOR_NAME[primary]})."]
    out = [f"Blend {blend_label(primary, secondary)}: el estilo puede variar por rol, presión y tarea."]
    if primary == "D" and "C" in secondary:
        out.append("D-C: resultados + calidad; riesgo: criticidad y baja paciencia.")
    if primary == "I" and "S" in secondary:
        out.append("I-S: conexión + soporte; riesgo: evitar conversaciones difíciles.")
    if primary == "C" and "S" in secondary:
        out.append("C-S: estabilidad + precisión; riesgo: resistencia a cambios rápidos.")
    if primary == "D" and "I" in secondary:
        out.append("D-I: acción + influencia; riesgo: impulsividad y menor escucha.")
    return out

# -----------------------------
# Scoring
# -----------------------------
def reverse_score(x: int) -> int:
    return (LIKERT_MAX + LIKERT_MIN) - x

def score_disc(items: List[Item], answers: Dict[str, int]) -> Dict:
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
    sd = (var ** 0.5) if var > 0 else 1.0
    z = {d: (raw[d] - mean) / sd for d in dims}

    ranked: List[Tuple[str, int]] = sorted(raw.items(), key=lambda kv: kv[1], reverse=True)
    primary = ranked[0][0]
    top_score = ranked[0][1]

    secondary = []
    for d, s in ranked[1:]:
        if (s >= top_score * BLEND_RATIO_DEFAULT) or ((top_score - s) <= BLEND_ABS_DEFAULT):
            secondary.append(d)

    spread = ranked[0][1] - ranked[-1][1]
    if spread <= 3:
        notes.append("Perfil poco diferenciado: puntajes cercanos (posible estilo balanceado o respuestas muy neutras).")

    validity_flag = validity >= VALIDITY_THRESHOLD_DEFAULT
    if validity_flag:
        notes.append("Alerta de validez: respuestas 'demasiado perfectas' (posible deseabilidad social).")

    notes.append(f"Estilo: {blend_label(primary, secondary)}.")
    return {
        "raw": raw, "pct": pct, "z": z,
        "primary": primary, "secondary": secondary,
        "validity_score": validity, "validity_flag": validity_flag,
        "notes": notes, "ranked": ranked,
    }

# -----------------------------
# Charts (bytes)
# -----------------------------
def fig_to_png_bytes(fig) -> bytes:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=200, bbox_inches="tight")
    plt.close(fig)
    return buf.getvalue()

def bar_chart_bytes(raw: Dict[str, int]) -> bytes:
    dims = ["D", "I", "S", "C"]
    vals = [raw[d] for d in dims]
    colors_ = [COLOR_HEX[d] for d in dims]
    fig = plt.figure()
    plt.title("DISC — Puntajes crudos")
    plt.bar(dims, vals, color=colors_)
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
    ax.set_title("DISC — Araña (0–100% internos)")
    ax.plot(angles, vals, color="#333333", linewidth=2)
    ax.fill(angles, vals, alpha=0.12)
    ax.set_thetagrids([a * 180 / math.pi for a in angles[:-1]], dims)
    ax.set_ylim(0, 100)
    return fig_to_png_bytes(fig)

def quadrant_chart_bytes(z: Dict[str, float], primary: str) -> bytes:
    x = (z["D"] + z["I"]) - (z["S"] + z["C"])
    y = (z["D"] + z["C"]) - (z["I"] + z["S"])
    fig = plt.figure()
    plt.title("Mapa conductual (esquema)")
    plt.axhline(0)
    plt.axvline(0)
    plt.scatter([x], [y], color=COLOR_HEX[primary], s=90)
    plt.xlim(-4, 4)
    plt.ylim(-4, 4)
    plt.xlabel("Activo/Rápido  ←→  Estable/Metódico")
    plt.ylabel("Tarea  ←→  Personas")
    return fig_to_png_bytes(fig)

def donut_chart_bytes(pct: Dict[str, float]) -> bytes:
    dims = ["D", "I", "S", "C"]
    vals = [pct[d] for d in dims]
    colors_ = [COLOR_HEX[d] for d in dims]
    fig = plt.figure()
    plt.title("DISC — Composición (%)")
    wedges, _ = plt.pie(vals, colors=colors_, startangle=90)
    centre_circle = plt.Circle((0, 0), 0.65, fc="white")
    plt.gca().add_artist(centre_circle)
    plt.legend(wedges, dims, loc="center left", bbox_to_anchor=(1.0, 0.5))
    plt.axis("equal")
    return fig_to_png_bytes(fig)

# -----------------------------
# PDF (Platypus)
# -----------------------------
def _img_from_bytes(png_bytes: bytes, width_cm: float) -> Image:
    bio = io.BytesIO(png_bytes)
    img = Image(bio)
    img.drawWidth = width_cm * cm
    img.drawHeight = img.drawWidth * 0.62
    return img

def build_pdf_bytes(person_name: str, role: str, result: Dict,
                    img_bar: bytes, img_radar: bytes, img_quad: bytes, img_donut: bytes) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=1.6*cm, rightMargin=1.6*cm, topMargin=1.6*cm, bottomMargin=1.6*cm)

    styles = getSampleStyleSheet()
    H1 = ParagraphStyle("H1", parent=styles["Heading1"], fontSize=16, spaceAfter=10)
    H2 = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=12, spaceBefore=10, spaceAfter=6)
    P = ParagraphStyle("P", parent=styles["BodyText"], fontSize=10, leading=13)
    Small = ParagraphStyle("Small", parent=styles["BodyText"], fontSize=9, leading=12, textColor=colors.grey)

    story = []

    primary = result["primary"]
    secondary = result["secondary"]
    raw = result["raw"]
    pct = result["pct"]
    z = result["z"]
    ranked = result["ranked"]

    story.append(Paragraph("Informe DISC — Uso interno", H1))
    story.append(Paragraph(f"<b>Evaluado:</b> {person_name} &nbsp;&nbsp; <b>Rol/Área:</b> {role}", P))
    story.append(Paragraph(f"<b>Resultado:</b> {blend_label(primary, secondary)}  "
                           f"(<b>Primario:</b> {primary} — {COLOR_NAME[primary]} / {DIM_NAMES[primary]})", P))
    story.append(Paragraph(f"<b>Validez:</b> {result['validity_score']} / 30"
                           f"{' &nbsp;&nbsp; <b>ALERTA</b>' if result['validity_flag'] else ''}", P))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Qué significa (modelo por colores)", H2))
    story.append(Paragraph(
        "Este instrumento clasifica estilos conductuales en cuatro colores: "
        "<b>Rojo (D)</b> resultados/decisión; <b>Amarillo (I)</b> influencia/comunicación; "
        "<b>Verde (S)</b> estabilidad/cooperación; <b>Azul (C)</b> precisión/estándares. "
        "La mayoría de personas presenta mezcla (1–2 colores dominantes).", P
    ))
    story.append(Paragraph(
        f"Regla interna para blend: ≥{int(BLEND_RATIO_DEFAULT*100)}% del top o diferencia ≤{BLEND_ABS_DEFAULT} puntos.", Small
    ))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Resumen ejecutivo", H2))
    for n in result["notes"]:
        story.append(Paragraph(f"• {n}", P))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Tabla de puntajes", H2))
    table_data = [["Color", "Dim", "Nombre", "Raw", "% interno", "Z (intra)"]]
    for d, _ in ranked:
        if d not in ["D", "I", "S", "C"]:
            continue
        table_data.append([COLOR_NAME[d], d, DIM_NAMES[d], str(raw[d]), f"{pct[d]:.1f}", f"{z[d]:.2f}"])

    t = Table(table_data, colWidths=[2.0*cm, 1.0*cm, 5.3*cm, 1.4*cm, 2.2*cm, 2.1*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.whitesmoke),
        ("GRID", (0,0), (-1,-1), 0.25, colors.lightgrey),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("ALIGN", (3,1), (-1,-1), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ]))
    story.append(t)
    story.append(Spacer(1, 10))

    story.append(Paragraph("Gráficos", H2))
    story.append(_img_from_bytes(img_bar, width_cm=17.0))
    story.append(Spacer(1, 6))
    row = Table([[_img_from_bytes(img_radar, 8.2), _img_from_bytes(img_donut, 8.2)]], colWidths=[8.2*cm, 8.2*cm])
    story.append(row)
    story.append(Spacer(1, 6))
    story.append(_img_from_bytes(img_quad, width_cm=17.0))

    doc.build(story)
    return buf.getvalue()

# -----------------------------
# Estado evaluación (1 pregunta)
# -----------------------------
items_all = get_items()

def init_eval():
    st.session_state.shuffle_seed = int(time.time() * 1000)
    rng = random.Random(st.session_state.shuffle_seed)
    st.session_state.items_shuffled = items_all.copy()
    rng.shuffle(st.session_state.items_shuffled)
    st.session_state.idx = 0
    st.session_state.answers = {}
    st.session_state.finished = False
    st.session_state.result = None

if "items_shuffled" not in st.session_state:
    init_eval()

# -----------------------------
# UI / CSS (más grande + centrado)
# -----------------------------
st.markdown(
    """
<style>
.big-card {
  padding: 26px 26px;
  border-radius: 18px;
  border: 1px solid rgba(0,0,0,0.10);
  background: rgba(255,255,255,0.75);
  text-align: center;
}
.q-title {
  font-size: 30px;
  font-weight: 800;
  line-height: 1.25;
  margin-top: 8px;
  margin-bottom: 10px;
}
.q-sub {
  font-size: 14px;
  opacity: 0.85;
}
div[role="radiogroup"] label {
  font-size: 18px !important;
}
</style>
""",
    unsafe_allow_html=True,
)

st.title("DISC — Cuestionario + Informe PDF")
st.caption("Las preguntas están mezcladas al azar y no muestran a qué dimensión pertenecen.")

top1, top2, top3 = st.columns([1.2, 1, 1])
with top1:
    person_name = st.text_input("Nombre evaluado", value=st.session_state.get("person_name", ""))
with top2:
    role = st.text_input("Rol/Área", value=st.session_state.get("role", ""))
with top3:
    if st.button("🔄 Nueva evaluación", use_container_width=True):
        init_eval()
        st.rerun()

st.session_state["person_name"] = person_name
st.session_state["role"] = role

items_shuffled: List[Item] = st.session_state.items_shuffled
n_items = len(items_shuffled)
idx = st.session_state.idx

st.progress((idx) / n_items if n_items else 0)

if not st.session_state.finished:
    it = items_shuffled[idx]
    st.markdown('<div class="big-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="q-sub">Pregunta {idx+1} de {n_items}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="q-title">{it.text}</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.write("")

    current_value = st.session_state.answers.get(it.id, 3)

    choice = st.radio(
        "Selecciona una opción:",
        options=[1, 2, 3, 4, 5],
        index=[1, 2, 3, 4, 5].index(current_value),
        horizontal=True,
        format_func=lambda x: f"{LIKERT_EMOJI[x]}  {LIKERT_LABELS[x]}",
        key=f"radio_{it.id}",
        label_visibility="collapsed",
    )
    st.session_state.answers[it.id] = int(choice)

    navL, navR, navC = st.columns([1, 1, 2])
    with navL:
        back = st.button("⬅️ Atrás", use_container_width=True, disabled=(idx == 0))
    with navR:
        if idx < n_items - 1:
            nxt = st.button("Siguiente ➡️", use_container_width=True)
        else:
            nxt = st.button("✅ Finalizar", use_container_width=True)

    if back:
        st.session_state.idx = max(0, idx - 1)
        st.rerun()

    if nxt:
        if idx < n_items - 1:
            st.session_state.idx = idx + 1
            st.rerun()
        else:
            answers = {it0.id: st.session_state.answers.get(it0.id, 3) for it0 in items_all}
            st.session_state.result = score_disc(items_all, answers)
            st.session_state.finished = True
            st.rerun()

# -----------------------------
# Resultados + PDF
# -----------------------------
if st.session_state.finished and st.session_state.result:
    result = st.session_state.result
    person = (st.session_state.get("person_name") or "").strip() or "N/A"
    role_ = (st.session_state.get("role") or "").strip() or "N/A"

    primary = result["primary"]
    secondary = result["secondary"]

    st.divider()
    st.subheader("Resultados")

    r1, r2, r3 = st.columns([1.6, 1, 1])
    with r1:
        st.markdown(
            f"**Primario:** {primary} — {COLOR_NAME[primary]} ({DIM_NAMES[primary]})  \n"
            f"**Secundarios:** {(', '.join(secondary)) if secondary else '—'}  \n"
            f"**Blend:** {blend_label(primary, secondary)}"
        )
        for n in result["notes"]:
            st.write(f"- {n}")

    with r2:
        st.metric("Validez (0–30)", str(result["validity_score"]),
                  delta="⚠️" if result["validity_flag"] else "")

    with r3:
        st.metric("% interno del primario", f"{result['pct'][primary]:.1f}%")

    img_bar = bar_chart_bytes(result["raw"])
    img_radar = radar_chart_bytes(result["pct"])
    img_quad = quadrant_chart_bytes(result["z"], primary=primary)
    img_donut = donut_chart_bytes(result["pct"])

    cL, cR = st.columns([1, 1])
    with cL:
        st.image(img_bar, caption="Barras — Puntajes crudos")
        st.image(img_radar, caption="Araña — % internos")
    with cR:
        st.image(img_donut, caption="Composición (%)")
        st.image(img_quad, caption="Mapa conductual (esquema)")

    pdf_bytes = build_pdf_bytes(person, role_, result, img_bar, img_radar, img_quad, img_donut)
    st.download_button(
        label="⬇️ Descargar informe PDF",
        data=pdf_bytes,
        file_name=f"informe_DISC_{person.replace(' ', '_')}.pdf",
        mime="application/pdf",
        use_container_width=True,
    )
