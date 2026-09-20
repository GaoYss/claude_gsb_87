import { compact, http } from './http'

export function fetchInspections(params) {
  return http.get('/inspections', { params: compact(params) })
}

export function fetchInspection(id) {
  return http.get(`/inspections/${id}`)
}

export function createInspection(payload) {
  return http.post('/inspections', payload)
}

export function updateInspection(id, payload) {
  return http.put(`/inspections/${id}`, payload)
}

export function deleteInspection(id) {
  return http.delete(`/inspections/${id}`)
}

