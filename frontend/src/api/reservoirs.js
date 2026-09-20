import { compact, http } from './http'

export function fetchReservoirs(params) {
  return http.get('/reservoirs', { params: compact(params) })
}

export function fetchReservoir(id) {
  return http.get(`/reservoirs/${id}`)
}

export function fetchReservoirStats(id) {
  return http.get(`/reservoirs/${id}/stats`)
}

export function createReservoir(payload) {
  return http.post('/reservoirs', payload)
}

export function updateReservoir(id, payload) {
  return http.put(`/reservoirs/${id}`, payload)
}

export function deleteReservoir(id) {
  return http.delete(`/reservoirs/${id}`)
}

