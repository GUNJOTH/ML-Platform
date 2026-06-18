import request from './request'

export function uploadDatasetZip(datasetId: string, file: File) {
  const formData = new FormData()
  formData.append('file', file)
  return request.post(`/datasets/${datasetId}/upload-zip`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export function detectDatasetStructure(datasetId: string) {
  return request.get(`/datasets/${datasetId}/detect`)
}

export function confirmDatasetImport(datasetId: string, payload: Record<string, unknown>) {
  return request.post(`/datasets/${datasetId}/confirm-import`, payload)
}

export function uploadImage(file: File) {
  const formData = new FormData()
  formData.append('file', file)
  return request.post('/upload/image', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}
