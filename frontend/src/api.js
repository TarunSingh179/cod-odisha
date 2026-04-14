import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// API endpoints
export const detectImage = async (file, ecosystem = 'default') => {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('ecosystem', ecosystem)
  
  const response = await api.post('/api/detect', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
  return response.data
}

export const describeSpecies = async (data) => {
  const response = await api.post('/api/describe', data)
  return response.data
}

export const getEcosystems = async () => {
  const response = await api.get('/api/ecosystems')
  return response.data
}

export const getHealth = async () => {
  const response = await api.get('/api/health')
  return response.data
}

export default api
