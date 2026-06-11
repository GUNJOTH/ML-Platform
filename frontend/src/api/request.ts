import axios from 'axios'
import type { AxiosInstance, AxiosResponse } from 'axios'

const baseURL = import.meta.env.VITE_API_BASE_URL
  ? `${import.meta.env.VITE_API_BASE_URL}/api/v1`
  : '/api/v1'

const request: AxiosInstance = axios.create({
  baseURL,
  timeout: 30000,
})

request.interceptors.response.use(
  (response: AxiosResponse) => response.data,
  (error) => {
    const message = error.response?.data?.detail || '请求失败'
    console.error('[API Error]', message)
    return Promise.reject(error)
  }
)

export default request
