from dataclasses import dataclass
from typing import List, Literal

Dim = Literal["D", "I", "S", "C", "V"]  # V = validez (opcional)

@dataclass(frozen=True)
class Item:
    id: str
    text: str
    dim: Dim
    reverse: bool = False

def get_items() -> List[Item]:
    items = [
        # --- D (Dominancia): reto, decisión, velocidad ---
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

        # --- I (Influencia): persuasión, energía social, optimismo ---
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

        # --- S (Estabilidad): calma, consistencia, cooperación ---
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

        # --- C (Conciencia/Consciencia): precisión, reglas, análisis ---
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

        # --- Validez (opcional): señales de “respuesta perfecta” ---
        Item("V01", "Nunca me equivoco en el trabajo.", "V"),
        Item("V02", "Siempre mantengo la calma, sin excepción.", "V"),
        Item("V03", "Jamás me distraigo; mi concentración es perfecta.", "V"),
        Item("V04", "Nunca he tenido un conflicto con nadie.", "V"),
        Item("V05", "Siempre cumplo todo a tiempo, incluso con múltiples urgencias.", "V"),
        Item("V06", "Mis decisiones siempre son objetivamente correctas.", "V"),
    ]
    return items
