import { http } from './http'

export function fetchOptions() {
  return http.get('/meta/options')
}

export function fetchHealth() {
  return http.get('/meta/health')
}

