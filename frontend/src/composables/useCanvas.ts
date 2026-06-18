import { ref, type Ref } from 'vue'

export interface BBox {
  id: string
  x: number
  y: number
  width: number
  height: number
  labelId: string
  labelName: string
  color: string
}

type DrawMode = 'draw' | 'select'

const HANDLE_SIZE = 6

export function useCanvas(canvasRef: Ref<HTMLCanvasElement | null>) {
  const boxes = ref<BBox[]>([])
  const selectedId = ref<string | null>(null)
  const mode = ref<DrawMode>('draw')
  const currentLabelId = ref('')
  const currentLabelName = ref('')
  const currentColor = ref('#FF0000')

  let image: HTMLImageElement | null = null
  let scale = 1
  let offsetX = 0
  let offsetY = 0
  let drawing = false
  let startX = 0
  let startY = 0
  let tempBox: { x: number; y: number; w: number; h: number } | null = null
  let dragging = false
  let dragOffsetX = 0
  let dragOffsetY = 0

  function loadImage(src: string): Promise<void> {
    return new Promise((resolve) => {
      const img = new Image()
      img.onload = () => {
        image = img
        fitToCanvas()
        render()
        resolve()
      }
      img.src = src
    })
  }

  function fitToCanvas() {
    const canvas = canvasRef.value
    if (!canvas || !image) return
    const scaleX = canvas.width / image.width
    const scaleY = canvas.height / image.height
    scale = Math.min(scaleX, scaleY)
    offsetX = (canvas.width - image.width * scale) / 2
    offsetY = (canvas.height - image.height * scale) / 2
  }

  function render() {
    const canvas = canvasRef.value
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    ctx.clearRect(0, 0, canvas.width, canvas.height)

    if (image) {
      ctx.drawImage(image, offsetX, offsetY, image.width * scale, image.height * scale)
    }

    for (const box of boxes.value) {
      drawBox(ctx, box, box.id === selectedId.value)
    }

    if (tempBox) {
      ctx.strokeStyle = currentColor.value
      ctx.lineWidth = 2
      ctx.setLineDash([4, 4])
      ctx.strokeRect(
        tempBox.x * scale + offsetX,
        tempBox.y * scale + offsetY,
        tempBox.w * scale,
        tempBox.h * scale
      )
      ctx.setLineDash([])
    }
  }

  function drawBox(ctx: CanvasRenderingContext2D, box: BBox, selected: boolean) {
    const x = box.x * scale + offsetX
    const y = box.y * scale + offsetY
    const w = box.width * scale
    const h = box.height * scale

    ctx.strokeStyle = box.color
    ctx.lineWidth = selected ? 3 : 2
    ctx.strokeRect(x, y, w, h)

    ctx.fillStyle = box.color
    ctx.globalAlpha = 0.15
    ctx.fillRect(x, y, w, h)
    ctx.globalAlpha = 1

    ctx.font = '12px sans-serif'
    ctx.fillStyle = box.color
    ctx.fillText(box.labelName, x + 2, y - 4)

    if (selected) {
      const handles = getHandles(x, y, w, h)
      ctx.fillStyle = '#fff'
      ctx.strokeStyle = box.color
      ctx.lineWidth = 1
      for (const handle of handles) {
        ctx.fillRect(handle.x - HANDLE_SIZE / 2, handle.y - HANDLE_SIZE / 2, HANDLE_SIZE, HANDLE_SIZE)
        ctx.strokeRect(handle.x - HANDLE_SIZE / 2, handle.y - HANDLE_SIZE / 2, HANDLE_SIZE, HANDLE_SIZE)
      }
    }
  }

  function getHandles(x: number, y: number, w: number, h: number) {
    return [
      { x, y },
      { x: x + w, y },
      { x, y: y + h },
      { x: x + w, y: y + h },
    ]
  }

  function canvasToImage(cx: number, cy: number): { x: number; y: number } {
    return { x: (cx - offsetX) / scale, y: (cy - offsetY) / scale }
  }

  function findBoxAt(cx: number, cy: number): BBox | null {
    const { x: ix, y: iy } = canvasToImage(cx, cy)
    for (let i = boxes.value.length - 1; i >= 0; i--) {
      const b = boxes.value[i]
      if (ix >= b.x && ix <= b.x + b.width && iy >= b.y && iy <= b.y + b.height) {
        return b
      }
    }
    return null
  }

  function onMouseDown(e: MouseEvent) {
    const rect = canvasRef.value?.getBoundingClientRect()
    if (!rect) return
    const cx = e.clientX - rect.left
    const cy = e.clientY - rect.top

    if (mode.value === 'select') {
      const box = findBoxAt(cx, cy)
      if (box) {
        selectedId.value = box.id
        dragging = true
        const imgPos = canvasToImage(cx, cy)
        dragOffsetX = imgPos.x - box.x
        dragOffsetY = imgPos.y - box.y
      } else {
        selectedId.value = null
      }
      render()
      return
    }

    drawing = true
    const imgPos = canvasToImage(cx, cy)
    startX = imgPos.x
    startY = imgPos.y
    tempBox = { x: startX, y: startY, w: 0, h: 0 }
  }

  function onMouseMove(e: MouseEvent) {
    const rect = canvasRef.value?.getBoundingClientRect()
    if (!rect) return
    const cx = e.clientX - rect.left
    const cy = e.clientY - rect.top
    const imgPos = canvasToImage(cx, cy)

    if (dragging && selectedId.value) {
      const box = boxes.value.find((b) => b.id === selectedId.value)
      if (box) {
        box.x = imgPos.x - dragOffsetX
        box.y = imgPos.y - dragOffsetY
        render()
      }
      return
    }

    if (drawing && tempBox) {
      tempBox.w = imgPos.x - startX
      tempBox.h = imgPos.y - startY
      render()
    }
  }

  function onMouseUp() {
    if (dragging) {
      dragging = false
      return
    }

    if (drawing && tempBox) {
      drawing = false
      const w = Math.abs(tempBox.w)
      const h = Math.abs(tempBox.h)

      if (w > 5 && h > 5) {
        const newBox: BBox = {
          id: crypto.randomUUID(),
          x: tempBox.w < 0 ? startX + tempBox.w : startX,
          y: tempBox.h < 0 ? startY + tempBox.h : startY,
          width: w,
          height: h,
          labelId: currentLabelId.value,
          labelName: currentLabelName.value,
          color: currentColor.value,
        }
        boxes.value.push(newBox)
        selectedId.value = newBox.id
      }
      tempBox = null
      render()
    }
  }

  function deleteSelected() {
    if (!selectedId.value) return
    boxes.value = boxes.value.filter((b) => b.id !== selectedId.value)
    selectedId.value = null
    render()
  }

  function updateSelectedLabel(labelId: string, labelName: string, color: string) {
    if (!selectedId.value) return
    const box = boxes.value.find((b) => b.id === selectedId.value)
    if (box) {
      box.labelId = labelId
      box.labelName = labelName
      box.color = color
      render()
    }
  }

  function setBoxes(newBoxes: BBox[]) {
    boxes.value = newBoxes
    render()
  }

  function setLabel(labelId: string, labelName: string, color: string) {
    currentLabelId.value = labelId
    currentLabelName.value = labelName
    currentColor.value = color
  }

  return {
    boxes,
    selectedId,
    mode,
    loadImage,
    render,
    onMouseDown,
    onMouseMove,
    onMouseUp,
    deleteSelected,
    updateSelectedLabel,
    setBoxes,
    setLabel,
  }
}
