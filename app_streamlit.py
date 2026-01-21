import io
import math
import time
import random
from dataclasses import dataclass
from typing import Dict, List, Literal, Tuple

import streamlit as st
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader

# -----------------------------
# Config (sin parámetros visibles)
# -----------------------------
st.set_page_config(page_title="DISC (Colores) — Cuestionario + Informe", layout="wide")

LIKERT_MIN, LIKERT_MAX = 1, 5
Dim = Literal["D", "I", "S", "C", "V"]  # V = validez (oculta en UI)

# Defaults internos
BLEND_RATIO_DEFAULT = 0.90
BLEND_ABS_DEFAULT = 2
VALIDITY_THRESHOLD_DEFAULT = 24  # 0–30 con 6 ítems V

# Colores tipo "Rodeado de idiotas"
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

# -----------------------------
# Data
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

        # --- Validez (se incluyen pero NO se etiquetan en la UI) ---
        Item("V01", "Nunca me equivoco en el trabajo.", "V"),
        Item("V02", "Siempre mantengo la calma, sin excepción.", "V"),
        Item("V03", "Jamás me distraigo; mi concentración es perfecta.", "V"),
        Item("V04", "Nunca he tenido un conflicto con nadie.", "V"),
        Item("V05", "Siempre cumplo todo a tiempo, incluso con múltiples urgencias.", "V"),
        Item("V06", "Mis decisiones siempre son objetivamente correctas.", "V"),
    ]

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
        notes.append("Perfil poco diferenciado: puntajes muy cercanos entre dimensiones (posible estilo balanceado o respuestas neutras).")

    validity_flag = validity >= VALIDITY_THRESHOLD_DEFAULT
    if validity_flag:
        notes.append("Alerta de validez: patrón de respuestas 'demasiado perfecto' (posible deseabilidad social).")

    if not secondary:
        notes.append(f"Estilo predominante: {primary} ({COLOR_NAME[primary]}).")
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
# Charts (colores solo en resultados)
# -----------------------------
def fig_to_png_bytes(fig) -> bytes:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=200, bbox_inches="tight")
    plt.close(fig)
    return buf.getvalue()

def bar_chart_bytes(raw: Dict[str, int]) -> bytes:
    dims = ["D", "I", "S", "C"]
    vals = [raw[d] for d in dims]
    colors = [COLOR_HEX[d] for d in dims]
    fig = plt.figure()
    plt.title("DISC — Puntajes crudos")
    plt.bar(dims, vals, color=colors)
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
    ax.set_title("DISC — Diagrama de araña (0–100%)")
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
    plt.scatter([x], [y], color=COLOR_HEX[primary], s=80)
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
    y = A4[1] - 2 * cm

    def line(txt, dy=0.7 * cm, size=11, bold=False):
        nonlocal y
        c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
        c.drawString(2 * cm, y, txt)
        y -= dy

    raw, pct = result["raw"], result["pct"]
    primary, secondary = result["primary"], result["secondary"]

    line("Informe DISC (colores)", size=16, bold=True, dy=1.0 * cm)
    line(f"Nombre: {person_name}", bold=True)
    line(f"Rol/Área: {role}")
    line(
        f"Resultado: {primary} ({DIM_NAMES[primary]} — {COLOR_NAME[primary]})"
        + (f" | Secundarios: {', '.join(secondary)}" if secondary else "")
    )
    line(f"Validez (0–30): {result['validity_score']}" + ("  [ALERTA]" if result["validity_flag"] else ""))

    line("Notas:", bold=True)
    for n in result["notes"]:
        line(f"• {n}", size=10, dy=0.55 * cm)

    y -= 0.3 * cm
    line("Puntajes:", bold=True)
    line(f"Crudos: D={raw['D']}  I={raw['I']}  S={raw['S']}  C={raw['C']}", size=10, dy=0.55 * cm)
    line(f"% internos: D={pct['D']:.1f}  I={pct['I']:.1f}  S={pct['S']:.1f}  C={pct['C']:.1f}", size=10, dy=0.55 * cm)

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
# UI (un solo panel + orden aleatorio)
# -----------------------------
st.title("DISC (colores) — Cuestionario anónimo por dimensión + Informe PDF")
st.caption("Instrucciones: responde honestamente (1–5). El orden de preguntas se mezcla automáticamente para reducir sugestión.")

# Estado para aleatoriedad por evaluación
if "shuffle_seed" not in st.session_state:
    st.session_state.shuffle_seed = int(time.time() * 1000)

if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "result" not in st.session_state:
    st.session_state.result = None

items_all = get_items()

# Botón “Nueva evaluación”: limpia respuestas y remezcla orden
topA, topB, topC = st.columns([1.2, 1, 1])
with topA:
    person_name = st.text_input("Nombre evaluado", value=st.session_state.get("person_name", ""))
with topB:
    role = st.text_input("Rol/Área", value=st.session_state.get("role", ""))
with topC:
    if st.button("🔄 Nueva evaluación (remezclar preguntas)", use_container_width=True):
        # Reset
        st.session_state.shuffle_seed = int(time.time() * 1000)
        st.session_state.submitted = False
        st.session_state.result = None
        # borrar respuestas
        for it in items_all:
            k = f"ans_{it.id}"
            if k in st.session_state:
                del st.session_state[k]
        st.rerun()

st.session_state["person_name"] = person_name
st.session_state["role"] = role

# Mezcla determinística por seed de sesión/evaluación
items_shuffled = items_all.copy()
rng = random.Random(st.session_state.shuffle_seed)
rng.shuffle(items_shuffled)

# CSS mínimo para hacerlo más limpio
st.markdown(
    """
<style>
.qcard {
  padding: 14px 16px;
  border-radius: 14px;
  border: 1px solid rgba(0,0,0,0.08);
  background: rgba(255,255,255,0.65);
  margin-bottom: 10px;
}
.small { font-size: 12px; opacity: 0.85; }
</style>
""",
    unsafe_allow_html=True,
)

with st.form("disc_form", clear_on_submit=False):
    st.markdown('<div class="qcard">', unsafe_allow_html=True)
    st.markdown("**Escala:** 1=Totalmente en desacuerdo … 5=Totalmente de acuerdo")
    st.markdown('<div class="small">Tip: evita responder todo “3”; usa los extremos cuando aplique.</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    for idx, it in enumerate(items_shuffled, start=1):
        # NO mostramos dim, color ni si está invertida.
        # (La inversión se aplica internamente en el scoring)
        st.markdown('<div class="qcard">', unsafe_allow_html=True)
        st.markdown(f"**{idx}.** {it.text}")
        st.radio(
            label="",
            options=[1, 2, 3, 4, 5],
            index=2,
            horizontal=True,
            format_func=lambda x: LIKERT_LABELS[x],
            key=f"ans_{it.id}",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    submit = st.form_submit_button("✅ Calcular resultados y generar informe")

if submit:
    st.session_state.submitted = True
    answers = {it.id: int(st.session_state.get(f"ans_{it.id}", 3)) for it in items_all}
    st.session_state.result = score_disc(items_all, answers)

# -----------------------------
# Resultados (en la misma pantalla)
# -----------------------------
if st.session_state.submitted and st.session_state.result:
    result = st.session_state.result
    person = (st.session_state.get("person_name") or "").strip() or "N/A"
    role = (st.session_state.get("role") or "").strip() or "N/A"

    primary = result["primary"]
    secondary = result["secondary"]

    st.divider()
    st.subheader("Resultados (colores)")

    r1, r2, r3 = st.columns([1.6, 1, 1])
    with r1:
        sec_txt = (", ".join(secondary)) if secondary else "—"
        st.markdown(
            f"**Primario:** {primary} — {COLOR_NAME[primary]} ({DIM_NAMES[primary]})  \n"
            f"**Secundarios:** {sec_txt}"
        )
        for n in result["notes"]:
            st.write(f"- {n}")

    with r2:
        st.metric("Validez (0–30)", str(result["validity_score"]),
                  delta="⚠️" if result["validity_flag"] else "")
        st.caption("Si hay alerta, interpreta con cautela (posible deseabilidad social).")

    with r3:
        st.metric("% interno del primario", f"{result['pct'][primary]:.1f}%")
        st.caption("Distribución relativa dentro de la persona.")

    # Gráficas
    img_bar = bar_chart_bytes(result["raw"])
    img_radar = radar_chart_bytes(result["pct"])
    img_quad = quadrant_chart_bytes(result["z"], primary=primary)

    cL, cR = st.columns([1, 1])
    with cL:
        st.image(img_bar, caption="Barras — Puntajes crudos (colores)")
        st.image(img_radar, caption="Araña — % internos")
    with cR:
        st.image(img_quad, caption="Mapa conductual (esquema)")
        st.markdown("**Puntajes crudos**")
        st.json(result["raw"])
        st.markdown("**% internos**")
        st.json({k: round(v, 1) for k, v in result["pct"].items()})

    st.subheader("Virtudes y puntos a trabajar (según primario)")
    c3, c4 = st.columns(2)
    with c3:
        st.markdown(f"**Virtudes ({COLOR_NAME[primary]})**")
        for s in STRENGTHS[primary]:
            st.write(f"- {s}")
    with c4:
        st.markdown("**Puntos a trabajar**")
        for d in DEVELOP[primary]:
            st.write(f"- {d}")

    st.markdown("**Lectura del blend**")
    for bi in blend_insights(primary, secondary):
        st.write(f"- {bi}")

    # PDF
    pdf_bytes = build_pdf_bytes(person, role, result, img_bar, img_radar, img_quad)
    st.download_button(
        label="⬇️ Descargar informe PDF",
        data=pdf_bytes,
        file_name=f"informe_DISC_{person.replace(' ', '_')}.pdf",
        mime="application/pdf",
        use_container_width=True,
    )
