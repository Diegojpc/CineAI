"""
CineAI LLM Service - Prompt Builder
Construye los prompts para el modelo Gemini con el contexto del catálogo.
"""
import logging

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Eres CineAI, un asistente experto en cine apasionado y conocedor. Tu trabajo es recomendar películas del catálogo disponible basándote en lo que el usuario describe.

REGLAS ESTRICTAS:
1. SOLO puedes recomendar películas que están en el CATÁLOGO proporcionado. No inventes películas.
2. Responde SIEMPRE en español.
3. Sé conversacional, cálido y entusiasta. Usa un tono de amigo cinéfilo.
4. Cuando recomiendes películas, explica BREVEMENTE por qué cada una encaja con lo que el usuario busca.
5. Si el usuario describe un estado de ánimo, género, o temática, busca las mejores coincidencias en el catálogo.
6. Si no encuentras películas que coincidan bien, sé honesto y sugiere las más cercanas.
7. Limita tus recomendaciones a un máximo de 5 películas por respuesta.
8. Al final de tu respuesta, incluye SIEMPRE una línea con el formato exacto:
   RECOMMENDED_IDS: [id1, id2, id3]
   donde los IDs son los IDs del catálogo de las películas recomendadas.
   Si no recomiendas ninguna película, escribe: RECOMMENDED_IDS: []

FORMATO DE RESPUESTA:
- Texto conversacional con las recomendaciones
- Última línea SIEMPRE: RECOMMENDED_IDS: [lista de ids]"""


def build_catalog_context(movies: list[dict]) -> str:
    """
    Construye el bloque de texto del catálogo para inyectar en el prompt.

    Args:
        movies: Lista de diccionarios con datos de películas.

    Returns:
        String formateado con el catálogo.
    """
    logger.info("build_catalog_context: building context for %d movies", len(movies))

    lines = ["CATÁLOGO DE PELÍCULAS DISPONIBLES:"]
    lines.append("=" * 50)

    for m in movies:
        genres_str = ", ".join(m.get("genres", []))
        year = m.get("year", "N/A")
        rating = m.get("vote_average", 0.0)
        overview = m.get("overview", "Sin sinopsis")

        lines.append(
            f"- ID: {m['id']} | \"{m['title']}\" ({year}) | "
            f"Géneros: {genres_str} | Rating: {rating}/10 | "
            f"Sinopsis: {overview}"
        )

    lines.append("=" * 50)
    catalog_text = "\n".join(lines)
    logger.debug("build_catalog_context: catalog text length=%d chars", len(catalog_text))
    return catalog_text


def build_messages(
    user_message: str,
    conversation_history: list[dict],
    catalog_context: str,
) -> list[dict]:
    """
    Construye la lista de mensajes para enviar a Gemini.

    Args:
        user_message: Mensaje actual del usuario.
        conversation_history: Historial de mensajes previos.
        catalog_context: Texto del catálogo generado por build_catalog_context.

    Returns:
        Lista de dicts con role/content para el modelo.
    """
    logger.info(
        "build_messages: user_message='%s', history_length=%d",
        user_message[:80],
        len(conversation_history),
    )

    messages = []

    # Historial previo (últimos 10 mensajes para no exceder tokens)
    recent_history = conversation_history[-10:]
    for msg in recent_history:
        messages.append({
            "role": msg["role"],
            "content": msg["content"],
        })

    # Mensaje actual del usuario con el catálogo como contexto
    full_user_message = f"""{catalog_context}

CONSULTA DEL USUARIO:
{user_message}

Recuerda: solo recomienda películas del catálogo anterior y termina SIEMPRE con RECOMMENDED_IDS: [ids]"""

    messages.append({
        "role": "user",
        "content": full_user_message,
    })

    logger.info("build_messages: built %d messages for Gemini", len(messages))
    return messages
