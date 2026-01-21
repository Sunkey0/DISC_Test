from dataclasses import dataclass
from typing import Dict, List, Tuple
from questionnaire import Item

LIKERT_MIN, LIKERT_MAX = 1, 5

def reverse_score(x: int) -> int:
    # 1<->5, 2<->4, 3->3
    return (LIKERT_MAX + LIKERT_MIN) - x

@dataclass
class DiscResult:
    raw: Dict[str, int]          # D/I/S/C raw sums
    pct: Dict[str, float]        # 0-100 within-person share
    z: Dict[str, float]          # within-person z-scores
    primary: str                 # top dimension
    secondary: List[str]         # blended dims
    validity_flag: bool
    validity_score: int
    notes: List[str]

def score_disc(items: List[Item], answers: Dict[str, int],
               blend_ratio: float = 0.90,
               blend_abs: int = 2,
               validity_threshold: int = 24) -> DiscResult:
    """
    answers: dict {item_id: 1..5}
    validity_threshold: sum of V items above this => possible social desirability.
                        6 items * max 5 = 30. threshold 24 is “muy alto”.
    """
    dims = ["D", "I", "S", "C"]
    raw = {d: 0 for d in dims}
    validity = 0
    notes = []

    for it in items:
        if it.id not in answers:
            raise ValueError(f"Falta respuesta para {it.id}")
        x = answers[it.id]
        if not (LIKERT_MIN <= x <= LIKERT_MAX):
            raise ValueError(f"Respuesta fuera de rango en {it.id}: {x}")
        if it.reverse:
            x = reverse_score(x)

        if it.dim in raw:
            raw[it.dim] += x
        elif it.dim == "V":
            validity += x

    total = sum(raw.values())
    pct = {d: (raw[d] / total * 100.0) if total else 0.0 for d in dims}

    # z-scores intra-sujeto (4 dimensiones)
    mean = sum(raw.values()) / 4.0
    var = sum((raw[d] - mean) ** 2 for d in dims) / 4.0
    sd = var ** 0.5 if var > 0 else 1.0
    z = {d: (raw[d] - mean) / sd for d in dims}

    # Ranking
    ranked: List[Tuple[str, int]] = sorted(raw.items(), key=lambda kv: kv[1], reverse=True)
    primary = ranked[0][0]
    top_score = ranked[0][1]

    secondary = []
    for d, s in ranked[1:]:
        if (s >= top_score * blend_ratio) or ((top_score - s) <= blend_abs):
            secondary.append(d)

    # Si todo queda muy parejo, avisar
    spread = ranked[0][1] - ranked[-1][1]
    if spread <= 3:
        notes.append("Perfil poco diferenciado: puntajes muy cercanos entre dimensiones (posible estilo balanceado o respuestas neutras).")

    validity_flag = validity >= validity_threshold
    if validity_flag:
        notes.append("Alerta de validez: patrón de respuestas 'demasiado perfecto' (posible deseabilidad social).")

    # Etiqueta de estilo
    if not secondary:
        notes.append(f"Estilo predominante: {primary}.")
    else:
        combo = "-".join([primary] + secondary)
        notes.append(f"Estilo combinado (blend): {combo}.")

    return DiscResult(
        raw=raw, pct=pct, z=z,
        primary=primary, secondary=secondary,
        validity_flag=validity_flag, validity_score=validity,
        notes=notes
    )
