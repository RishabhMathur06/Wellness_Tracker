export const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export function authHeaders(token) {
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function apiFetch(path, { token, ...options } = {}) {
  const headers = {
    ...options.headers,
    ...authHeaders(token),
  };

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  return res;
}
