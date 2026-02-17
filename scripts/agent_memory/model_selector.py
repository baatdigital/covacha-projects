"""
Selección de modelo Claude basada en labels de la tarea.
Optimiza costo eligiendo haiku/sonnet/opus según complejidad.
"""

from config import MODEL_MAP, MODEL_DEFAULT, MODEL_HAIKU, MODEL_SONNET, MODEL_OPUS


# Justificaciones por modelo para incluir en CONTEXT.md
MODEL_JUSTIFICATION: dict[str, str] = {
    MODEL_HAIKU: "tarea de lectura/sync/docs (read-only, bajo costo)",
    MODEL_SONNET: "implementación de feature/bugfix (balance costo/capacidad)",
    MODEL_OPUS: "decisión arquitectónica o tarea cross-repo (máxima capacidad)",
}

# Prioridad de labels: opus > sonnet > haiku
PRIORITY_ORDER: list[str] = [MODEL_OPUS, MODEL_SONNET, MODEL_HAIKU]


def select_model(labels: list[str]) -> tuple[str, str]:
    """
    Selecciona el modelo Claude más apropiado según los labels de la tarea.

    Regla: si hay conflicto, el modelo más poderoso tiene prioridad.
    Ejemplo: ['backend', 'architecture'] → opus (architecture gana a backend)

    Args:
        labels: Lista de labels del issue de GitHub

    Returns:
        Tupla (model_name, justification)
    """
    if not labels:
        return MODEL_DEFAULT, MODEL_JUSTIFICATION[MODEL_DEFAULT]

    labels_lower = [label.lower().strip() for label in labels]
    selected_model = MODEL_DEFAULT

    # Iterar en orden de prioridad descendente (opus primero)
    for model in PRIORITY_ORDER:
        for label in labels_lower:
            if MODEL_MAP.get(label) == model:
                selected_model = model
                break
        if selected_model == model and model != MODEL_DEFAULT:
            break

    justification = MODEL_JUSTIFICATION.get(selected_model, "")
    return selected_model, justification


def get_model_for_operation(operation: str) -> str:
    """
    Retorna el modelo para operaciones internas del sistema.

    Args:
        operation: Nombre de la operación (bootstrap, sync, claim, release, status)

    Returns:
        Nombre del modelo recomendado
    """
    # Operaciones del sistema siempre usan haiku (simples, sin lógica de negocio)
    system_operations = {"bootstrap", "sync", "claim", "release", "status", "team_status"}
    if operation.lower() in system_operations:
        return MODEL_HAIKU
    return MODEL_DEFAULT
