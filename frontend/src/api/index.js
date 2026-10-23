import api, { getCSRF } from './client'

export const getCurrentUser = async () => {
  try {
    const { data } = await api.get('/users/me/')
    return data
  } catch (e) {
    if (e.response?.status === 401 || e.response?.status === 403) return null
    throw e
  }
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

export const openCase = async (caseId) => {
  const res = await fetch(`/api/open-case/${caseId}/`, {
    method: 'POST',
    credentials: 'include',
    headers: {
      'X-CSRFToken': getCSRF() || '',
      'Content-Type': 'application/json',
    },
  })
  return res.json()
}


export const getCaseHistory = async (caseId) => {
  const res = await fetch(`/api/case-history/${caseId}/`, { credentials: 'include' })
  return res.json()
}


export const getInventory = async () => {
  const { data } = await api.get('/inventory/')
  return data.results || data
}

export const sellItem = async (inventoryId) => {
  const res = await fetch(`/api/sell-item/${inventoryId}/`, {
    method: 'POST',
    credentials: 'include',
    headers: {
      'X-CSRFToken': getCSRF() || '',
      'Content-Type': 'application/json',
    },
  })
  return res.json()
}

export const sellAllItems = async () => {
  const res = await fetch('/api/sell-all-items/', {
    method: 'POST',
    credentials: 'include',
    headers: {
      'X-CSRFToken': getCSRF() || '',
      'Content-Type': 'application/json',
    },
  })
  return res.json()
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

export const getAllItems = async () => {
  const res = await fetch('/api/all-items/', { credentials: 'include' })
  return res.json()
}

export const doUpgrade = async (inventoryId, targetItemId) => {
  const res = await fetch('/api/do-upgrade/', {
    method: 'POST',
    credentials: 'include',
    headers: {
      'X-CSRFToken': getCSRF() || '',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ inventory_id: inventoryId, target_item_id: targetItemId })
  })
  return res.json()
}