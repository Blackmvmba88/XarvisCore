const ASCII_CHARS = ' .:;-=+*#%@'

export function videoFrameToAscii(
  video: HTMLVideoElement,
  canvas: HTMLCanvasElement,
  width: number = 120
): string {
  const ctx = canvas.getContext('2d', { willReadFrequently: true })
  if (!ctx) return ''

  if (!video.videoWidth || !video.videoHeight || video.videoWidth === 0 || video.videoHeight === 0) {
    return ''
  }

  const aspectRatio = video.videoHeight / video.videoWidth
  const height = Math.floor(width * aspectRatio * 0.5)

  if (!isFinite(height) || height <= 0 || !isFinite(width) || width <= 0) {
    return ''
  }

  canvas.width = Math.floor(width)
  canvas.height = Math.floor(height)

  ctx.drawImage(video, 0, 0, Math.floor(width), Math.floor(height))
  const imageData = ctx.getImageData(0, 0, Math.floor(width), Math.floor(height))
  const pixels = imageData.data

  let ascii = ''
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      const i = (y * width + x) * 4
      const r = pixels[i]
      const g = pixels[i + 1]
      const b = pixels[i + 2]
      const brightness = (r + g + b) / 3
      const charIndex = Math.floor((brightness / 255) * (ASCII_CHARS.length - 1))
      ascii += ASCII_CHARS[charIndex]
    }
    ascii += '\n'
  }

  return ascii
}

export function mutateAscii(ascii: string, mutationRate: number = 0.03): string {
  const chars = ascii.split('')
  for (let i = 0; i < chars.length; i++) {
    if (chars[i] !== '\n' && chars[i] !== ' ' && Math.random() < mutationRate) {
      const randomCharCode = Math.floor(Math.random() * 94) + 33
      chars[i] = String.fromCharCode(randomCharCode)
    }
  }
  return chars.join('')
}

export function imageToAscii(
  image: HTMLImageElement,
  canvas: HTMLCanvasElement,
  width: number = 120
): string {
  const ctx = canvas.getContext('2d', { willReadFrequently: true })
  if (!ctx) return ''

  if (!image.width || !image.height || image.width === 0 || image.height === 0) {
    return ''
  }

  const aspectRatio = image.height / image.width
  const height = Math.floor(width * aspectRatio * 0.5)

  if (!isFinite(height) || height <= 0 || !isFinite(width) || width <= 0) {
    return ''
  }

  canvas.width = Math.floor(width)
  canvas.height = Math.floor(height)

  ctx.drawImage(image, 0, 0, Math.floor(width), Math.floor(height))
  const imageData = ctx.getImageData(0, 0, Math.floor(width), Math.floor(height))
  const pixels = imageData.data

  let ascii = ''
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      const i = (y * width + x) * 4
      const r = pixels[i]
      const g = pixels[i + 1]
      const b = pixels[i + 2]
      const brightness = (r + g + b) / 3
      const charIndex = Math.floor((brightness / 255) * (ASCII_CHARS.length - 1))
      ascii += ASCII_CHARS[charIndex]
    }
    ascii += '\n'
  }

  return ascii
}

export function generatePatternAscii(
  width: number = 120, 
  height: number = 40, 
  frame: number = 0,
  audioLevel: number = 0,
  waveform: number[] = []
): string {
  let ascii = ''
  const centerX = width / 2
  const centerY = height / 2
  
  const amplitude = 0.5 + audioLevel * 2
  const frequency = 1 + audioLevel * 3
  const speed = frame / (10 - audioLevel * 5)
  
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      const dist = Math.sqrt(Math.pow(x - centerX, 2) + Math.pow(y - centerY, 2))
      
      let wave = Math.sin(dist / (5 / frequency) - speed) * amplitude + 0.5
      
      if (waveform.length > 0) {
        const waveformIndex = Math.floor((x / width) * waveform.length)
        const waveformValue = waveform[waveformIndex] || 0
        wave += waveformValue * audioLevel * 0.3
      }
      
      const horizontalWave = Math.sin(x / 8 - speed * 2) * audioLevel * 0.2
      wave += horizontalWave
      
      const verticalWave = Math.sin(y / 6 - speed * 1.5) * audioLevel * 0.2
      wave += verticalWave
      
      wave = Math.max(0, Math.min(1, wave))
      
      const charIndex = Math.floor(wave * (ASCII_CHARS.length - 1))
      ascii += ASCII_CHARS[charIndex]
    }
    ascii += '\n'
  }
  return ascii
}
