/**
 * CineAI Frontend - API Service
 * Wrapper para todas las llamadas HTTP al backend.
 */

const API_BASE = '/api';

/**
 * Fetch wrapper con manejo de errores estandarizado.
 */
async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  console.info(`[API] ${options.method || 'GET'} ${url}`);

  try {
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      console.error(`[API] Error ${response.status}:`, errorData);
      throw new Error(errorData.detail || `Error ${response.status}`);
    }

    const data = await response.json();
    console.info(`[API] Response from ${url}:`, { status: response.status });
    return data;
  } catch (error) {
    console.error(`[API] Request failed for ${url}:`, error);
    throw error;
  }
}

/**
 * Obtener películas paginadas.
 */
export async function getMovies(page = 1, limit = 20, genreId = null, sortBy = 'popularity') {
  let endpoint = `/movies?page=${page}&limit=${limit}&sort_by=${sortBy}`;
  if (genreId) endpoint += `&genre_id=${genreId}`;
  return request(endpoint);
}

/**
 * Obtener detalle de una película.
 */
export async function getMovie(id) {
  return request(`/movies/${id}`);
}

/**
 * Buscar películas.
 */
export async function searchMovies(query, limit = 20) {
  return request(`/movies/search?q=${encodeURIComponent(query)}&limit=${limit}`);
}

/**
 * Obtener géneros.
 */
export async function getGenres() {
  return request('/genres');
}

/**
 * Enviar mensaje al chat LLM.
 */
export async function sendChatMessage(message, conversationHistory = []) {
  return request('/chat', {
    method: 'POST',
    body: JSON.stringify({
      message,
      conversation_history: conversationHistory,
    }),
  });
}

/**
 * Health check.
 */
export async function healthCheck() {
  return request('/health');
}

/**
 * Construir URL completa del poster de TMDB.
 */
export function getPosterUrl(posterPath, size = 'w500') {
  if (!posterPath) return null;
  return `https://image.tmdb.org/t/p/${size}${posterPath}`;
}

/**
 * Construir URL del backdrop de TMDB.
 */
export function getBackdropUrl(backdropPath, size = 'w1280') {
  if (!backdropPath) return null;
  return `https://image.tmdb.org/t/p/${size}${backdropPath}`;
}
