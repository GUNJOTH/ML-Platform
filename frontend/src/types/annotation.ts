export interface Annotation {
  id: string
  image_id: string
  label_id: string
  annotation_type: string
  data: Record<string, number>
  label_name?: string
  color?: string
  created_at: string
  updated_at: string
}
