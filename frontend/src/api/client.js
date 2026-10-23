import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  withCredentials: true,
  headers: { 'Content-Type': 'application/json' },
})


export function getCSRF() {
  const m = document.cookie.match(/csrftoken=([^;]+)/)
  return m ? m[1] : null
}

api.interceptors.request.use((config) => {
  const csrf = getCSRF()
  if (csrf && ['post', 'put', 'patch', 'delete'].includes(config.method?.toLowerCase())) {
    config.headers['X-CSRFToken'] = csrf
  }
  return config
})

export default api