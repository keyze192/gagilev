import api from './client'

export const apiRegister = async (username, password, email) => {
  const { data } = await api.post('/auth/register/', { username, password, email })
  return data
}
export const apiLogin = async (username, password) => {
  const { data } = await api.post('/auth/login/', { username, password })
  return data
}
export const apiLogout = async () => {
  await api.post('/auth/logout/')
}

export const getCurrentUser = async () => {
  try {
    const { data } = await api.get('/users/me/')
    return data
  } catch (e) {
    if (e.response?.status === 401 || e.response?.status === 403) return null
    throw e
  }
}


export const getUsers = async () => {
  const { data } = await api.get('/users/')
  return data.results || data
}

export const deleteUser = async (id) => {
  await api.delete(`/users/${id}/`)
}


export const getCases = async (params = {}) => {
  const { data } = await api.get('/cases/', { params })
  return data.results || data
}

export const getCase = async (id) => {
  const { data } = await api.get(`/cases/${id}/`)
  return data
}

export const getCaseChances = async (id) => {
  const { data } = await api.get(`/cases/${id}/chances/`)
  return data.results || data
}

export const getCaseHistory = async (id) => {
  const { data } = await api.get(`/cases/${id}/history/`)
  return { success: true, history: data }
}

export const openCase = async (caseId, count = 1) => {
  const { data } = await api.post(`/cases/${caseId}/open/`, { count })
  return data
}


export const getInventory = async () => {
  const { data } = await api.get('/inventory/')
  return data.results || data
}

export const sellItem = async (inventoryId) => {
  const { data } = await api.post(`/inventory/${inventoryId}/sell/`)
  return data
}

export const sellAllItems = async () => {
  const { data } = await api.post('/inventory/sell-all/')
  return data
}

export const getAllItems = async () => {
  const { data } = await api.get('/items/', { params: { page_size: 1000 } })
  return { success: true, items: data.results || data }
}

export const doUpgrade = async (inventoryId, targetItemId) => {
  const { data } = await api.post('/inventory/upgrade/', {
    inventory_id: inventoryId,
    target_item_id: targetItemId,
  })
  return data
}


export const getItemIcon = (name = '') => {
  const n = name.toLowerCase()
  if (n.includes('нож') || n.includes('knife')) return 'fa-crosshairs'
  if (n.includes('перчатк') || n.includes('glove')) return 'fa-hand-paper'
  if (/ak|awp|m4|deagle|usp|glock|famas/.test(n)) return 'fa-gun'
  return 'fa-cube'
}

export const rarityClass = (rarity = 'common') => (rarity || 'common').toLowerCase()

export const rarityName = (rarity = 'common') => {
  const map = {
    common: 'Обычный', rare: 'Редкий', epic: 'Эпический',
    legendary: 'Легендарный', ancient: 'Древний',
  }
  return map[(rarity || 'common').toLowerCase()] || 'Обычный'
}