from typing import Dict, List

DIM_NAMES = {
    "D": "Dominancia",
    "I": "Influencia",
    "S": "Estabilidad",
    "C": "Conciencia (Consciencia/Conscientiousness)",
}

STRENGTHS: Dict[str, List[str]] = {
    "D": ["Orientación a resultados", "Decisión y rapidez", "Asertividad", "Capacidad para destrabar problemas"],
    "I": ["Comunicación persuasiva", "Energía social", "Motivación del equipo", "Networking y visibilidad"],
    "S": ["Constancia y paciencia", "Trabajo en equipo", "Escucha activa", "Estabilidad bajo presión"],
    "C": ["Precisión y calidad", "Análisis y criterio", "Gestión de riesgos", "Orden y estandarización"],
}

DEVELOP: Dict[str, List[str]] = {
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
    insights = [f"Blend {s}: el comportamiento puede cambiar según presión, rol y contexto."]
    if primary == "D" and "C" in secondary:
        insights.append("D-C: empuje por resultados con exigencia de calidad; riesgo: dureza y criticidad.")
    if primary == "I" and "S" in secondary:
        insights.append("I-S: cercanía y soporte; riesgo: evitar conflictos necesarios.")
    if primary == "C" and "S" in secondary:
        insights.append("C-S: estabilidad + precisión; riesgo: resistencia a cambios rápidos.")
    if primary == "D" and "I" in secondary:
        insights.append("D-I: influencia + acción; riesgo: decisiones impulsivas y baja escucha.")
    return insights
