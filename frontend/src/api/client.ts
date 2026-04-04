import axios, { AxiosError } from 'axios'

export const apiBaseUrl = import.meta.env.VITE_API_BASE_URL?.trim() || 'http://localhost:8000'

export class ApiError extends Error {
  status?: number
  validationErrors: string[]

  constructor(message: string, options: { status?: number; validationErrors?: string[] } = {}) {
    super(message)
    this.name = 'ApiError'
    this.status = options.status
    this.validationErrors = options.validationErrors ?? []
  }
}

export const apiClient = axios.create({
  baseURL: apiBaseUrl,
  headers: {
    'Content-Type': 'application/json',
  },
})

apiClient.interceptors.response.use(
  response => response,
  (error: AxiosError<unknown>) => Promise.reject(normalizeApiError(error)),
)

export function isApiError(error: unknown): error is ApiError {
  return error instanceof ApiError
}

export function getApiErrorMessage(error: unknown): string {
  if (isApiError(error)) {
    return error.validationErrors.length > 0 ? error.validationErrors.join('\n') : error.message
  }

  if (error instanceof Error) {
    return error.message
  }

  return '연결 실패'
}

function normalizeApiError(error: AxiosError<unknown>): ApiError {
  if (!error.response) {
    return new ApiError('연결 실패')
  }

  const { status, data } = error.response

  if (status === 500) {
    return new ApiError('서버 오류', { status })
  }

  if (status === 422) {
    return new ApiError('입력값을 확인해 주세요.', {
      status,
      validationErrors: extractValidationErrors(data),
    })
  }

  return new ApiError(extractDetailMessage(data) || error.message || '요청에 실패했습니다.', {
    status,
  })
}

function extractDetailMessage(data: unknown): string {
  if (!data || typeof data !== 'object') {
    return ''
  }

  const detail = (data as { detail?: unknown }).detail
  if (typeof detail === 'string') {
    return detail
  }

  if (!Array.isArray(detail)) {
    return ''
  }

  return detail
    .map(item => {
      if (!item || typeof item !== 'object') {
        return ''
      }

      const error = item as { loc?: unknown; msg?: unknown }
      const location = Array.isArray(error.loc) ? error.loc.join('.') : ''
      const message = typeof error.msg === 'string' ? error.msg : ''

      return [location, message].filter(Boolean).join(': ')
    })
    .filter(Boolean)
    .join('\n')
}

function extractValidationErrors(data: unknown): string[] {
  if (!data || typeof data !== 'object') {
    return []
  }

  const detail = (data as { detail?: unknown }).detail
  if (typeof detail === 'string') {
    return [detail]
  }

  if (!Array.isArray(detail)) {
    return []
  }

  return detail
    .map(item => {
      if (!item || typeof item !== 'object') {
        return ''
      }

      const error = item as { loc?: unknown; msg?: unknown }
      const location = Array.isArray(error.loc) ? error.loc.join('.') : ''
      const message = typeof error.msg === 'string' ? error.msg : ''

      return [location, message].filter(Boolean).join(': ')
    })
    .filter(Boolean)
}
