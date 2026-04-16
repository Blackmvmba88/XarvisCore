export interface FaceDetection {
  x: number
  y: number
  width: number
  height: number
  confidence: number
}

export interface Person {
  id: string
  name: string
  color: string
  detections: FaceDetection[]
}

export async function detectFaces(
  video: HTMLVideoElement,
  canvas: HTMLCanvasElement
): Promise<FaceDetection[]> {
  const ctx = canvas.getContext('2d')
  if (!ctx || !video.videoWidth) return []

  canvas.width = video.videoWidth
  canvas.height = video.videoHeight
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height)

  const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height)
  const faces = await detectFacesFromImageData(imageData, canvas.width, canvas.height)
  
  return faces
}

async function detectFacesFromImageData(
  imageData: ImageData,
  width: number,
  height: number
): Promise<FaceDetection[]> {
  const data = imageData.data
  const faces: FaceDetection[] = []

  const scanSize = 32
  const step = 16
  
  for (let y = 0; y < height - scanSize; y += step) {
    for (let x = 0; x < width - scanSize; x += step) {
      const score = checkFacePattern(data, x, y, scanSize, width)
      
      if (score > 0.5) {
        const faceWidth = Math.min(scanSize * 3, width - x)
        const faceHeight = Math.min(scanSize * 4, height - y)
        
        faces.push({
          x,
          y,
          width: faceWidth,
          height: faceHeight,
          confidence: score
        })
      }
    }
  }

  return mergeFaces(faces)
}

function checkFacePattern(
  data: Uint8ClampedArray,
  x: number,
  y: number,
  size: number,
  width: number
): number {
  const centerY = y + size / 2
  const centerX = x + size / 2
  
  let skinPixels = 0
  let totalPixels = 0
  let brightPixels = 0
  
  for (let dy = 0; dy < size; dy++) {
    for (let dx = 0; dx < size; dx++) {
      const px = x + dx
      const py = y + dy
      const idx = (py * width + px) * 4
      
      const r = data[idx]
      const g = data[idx + 1]
      const b = data[idx + 2]
      
      const isSkin = r > 95 && g > 40 && b > 20 &&
                    r > g && r > b &&
                    Math.abs(r - g) > 15
      
      const brightness = (r + g + b) / 3
      
      if (isSkin) skinPixels++
      if (brightness > 120) brightPixels++
      totalPixels++
    }
  }
  
  const skinRatio = skinPixels / totalPixels
  const brightRatio = brightPixels / totalPixels
  
  const eyeRegionBrightness = checkEyeRegion(data, x, y, size, width)
  
  let score = 0
  if (skinRatio > 0.3 && skinRatio < 0.8) score += 0.4
  if (brightRatio > 0.2 && brightRatio < 0.7) score += 0.3
  if (eyeRegionBrightness > 0.5) score += 0.3
  
  return score
}

function checkEyeRegion(
  data: Uint8ClampedArray,
  x: number,
  y: number,
  size: number,
  width: number
): number {
  const eyeY = y + size * 0.4
  const eyeSize = size * 0.3
  
  let darkPixels = 0
  let totalPixels = 0
  
  for (let dy = 0; dy < eyeSize; dy++) {
    for (let dx = 0; dx < size; dx++) {
      const px = x + dx
      const py = Math.floor(eyeY + dy)
      const idx = (py * width + px) * 4
      
      const r = data[idx] || 0
      const g = data[idx + 1] || 0
      const b = data[idx + 2] || 0
      
      const brightness = (r + g + b) / 3
      if (brightness < 80) darkPixels++
      totalPixels++
    }
  }
  
  return darkPixels / totalPixels
}

function mergeFaces(faces: FaceDetection[]): FaceDetection[] {
  if (faces.length === 0) return []
  
  const merged: FaceDetection[] = []
  const used = new Set<number>()
  
  for (let i = 0; i < faces.length; i++) {
    if (used.has(i)) continue
    
    const face1 = faces[i]
    const group = [face1]
    
    for (let j = i + 1; j < faces.length; j++) {
      if (used.has(j)) continue
      
      const face2 = faces[j]
      if (facesOverlap(face1, face2)) {
        group.push(face2)
        used.add(j)
      }
    }
    
    const avgFace = averageFaces(group)
    merged.push(avgFace)
    used.add(i)
  }
  
  merged.sort((a, b) => b.confidence - a.confidence)
  return merged.slice(0, 2)
}

function facesOverlap(face1: FaceDetection, face2: FaceDetection): boolean {
  const x1 = face1.x
  const y1 = face1.y
  const x2 = face1.x + face1.width
  const y2 = face1.y + face1.height
  
  const x3 = face2.x
  const y3 = face2.y
  const x4 = face2.x + face2.width
  const y4 = face2.y + face2.height
  
  return !(x2 < x3 || x4 < x1 || y2 < y3 || y4 < y1)
}

function averageFaces(faces: FaceDetection[]): FaceDetection {
  const avgX = faces.reduce((sum, f) => sum + f.x, 0) / faces.length
  const avgY = faces.reduce((sum, f) => sum + f.y, 0) / faces.length
  const avgWidth = faces.reduce((sum, f) => sum + f.width, 0) / faces.length
  const avgHeight = faces.reduce((sum, f) => sum + f.height, 0) / faces.length
  const avgConfidence = faces.reduce((sum, f) => sum + f.confidence, 0) / faces.length
  
  return {
    x: avgX,
    y: avgY,
    width: avgWidth,
    height: avgHeight,
    confidence: avgConfidence
  }
}
