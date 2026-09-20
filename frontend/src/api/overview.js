import { http } from './http'

export function fetchSummary() {
  return http.get('/overview/summary')
}

