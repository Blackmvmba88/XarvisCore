import React, { useEffect, useRef, memo } from 'react'

interface FrequencyVisualizerProps {
  spectrum: number[]
  waveform: number[]
  height?: number
}

export const FrequencyVisualizer = memo(function FrequencyVisualizer({ spectrum, waveform, height = 150 }: FrequencyVisualizerProps) {
  const spectrumCanvasRef = useRef<HTMLCanvasElement>(null)
  const waveformCanvasRef = useRef<HTMLCanvasElement>(null)
  const spectrumContainerRef = useRef<HTMLDivElement>(null)
  const waveformContainerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const canvas = spectrumCanvasRef.current
    const container = spectrumContainerRef.current
    if (!canvas || !container || spectrum.length === 0) return

    const resizeCanvas = () => {
      const rect = container.getBoundingClientRect()
      canvas.width = rect.width
      canvas.height = height
    }

    resizeCanvas()
    window.addEventListener('resize', resizeCanvas)

    const ctx = canvas.getContext('2d', { alpha: false })
    if (!ctx) return

    const width = canvas.width
    const h = canvas.height
    const barWidth = width / spectrum.length

    ctx.fillStyle = 'rgb(12, 12, 12)'
    ctx.fillRect(0, 0, width, h)

    spectrum.forEach((value, index) => {
      const barHeight = value * h * 0.98
      const x = index * barWidth

      const gradient = ctx.createLinearGradient(0, h - barHeight, 0, h)
      
      if (value > 0.7) {
        gradient.addColorStop(0, 'rgb(180, 100, 255)')
        gradient.addColorStop(0.5, 'rgb(120, 60, 200)')
      } else {
        gradient.addColorStop(0, 'rgb(180, 100, 255)')
        gradient.addColorStop(0.4, 'rgb(0, 255, 255)')
      }
      gradient.addColorStop(0.7, 'rgb(0, 200, 100)')
      gradient.addColorStop(1, 'rgb(0, 150, 50)')

      ctx.fillStyle = gradient
      ctx.fillRect(x, h - barHeight, barWidth - 0.5, barHeight)
      
      if (value > 0.5) {
        ctx.shadowColor = value > 0.7 ? 'rgb(180, 100, 255)' : 'rgb(0, 255, 150)'
        ctx.shadowBlur = value * 15
        ctx.fillRect(x, h - barHeight, barWidth - 0.5, barHeight)
        ctx.shadowBlur = 0
      }
    })

    return () => window.removeEventListener('resize', resizeCanvas)
  }, [spectrum, height])

  useEffect(() => {
    const canvas = waveformCanvasRef.current
    const container = waveformContainerRef.current
    if (!canvas || !container || waveform.length === 0) return

    const resizeCanvas = () => {
      const rect = container.getBoundingClientRect()
      canvas.width = rect.width
      canvas.height = height / 2
    }

    resizeCanvas()
    window.addEventListener('resize', resizeCanvas)

    const ctx = canvas.getContext('2d', { alpha: false })
    if (!ctx) return

    const width = canvas.width
    const h = canvas.height
    const midY = h / 2

    ctx.fillStyle = 'rgb(12, 12, 12)'
    ctx.fillRect(0, 0, width, h)

    const amplitude = waveform.reduce((sum, val) => sum + Math.abs(val), 0) / waveform.length
    const maxAmplitude = Math.max(...waveform.map(v => Math.abs(v)))

    const isHighEnergy = amplitude > 0.2 || maxAmplitude > 0.5
    ctx.strokeStyle = isHighEnergy ? 'rgb(180, 100, 255)' : 'rgb(0, 255, 150)'
    ctx.lineWidth = 2 + (amplitude * 3)
    ctx.shadowColor = isHighEnergy ? 'rgb(180, 100, 255)' : 'rgb(0, 255, 150)'
    ctx.shadowBlur = 10 + (amplitude * 30)
    ctx.lineCap = 'round'
    ctx.lineJoin = 'round'

    ctx.beginPath()
    
    const pointsPerPixel = waveform.length / width
    
    for (let pixelX = 0; pixelX <= width; pixelX++) {
      const waveformIndex = Math.floor(pixelX * pointsPerPixel)
      const value = waveform[Math.min(waveformIndex, waveform.length - 1)] || 0
      
      const amplificationFactor = 1.2 + (amplitude * 0.5)
      const y = midY + (value * midY * 0.95 * amplificationFactor)

      if (pixelX === 0) {
        ctx.moveTo(pixelX, y)
      } else {
        ctx.lineTo(pixelX, y)
      }
    }
    
    ctx.stroke()

    if (isHighEnergy) {
      ctx.globalAlpha = 0.3
      ctx.lineWidth = 1
      ctx.shadowBlur = 5
      ctx.beginPath()
      for (let pixelX = 0; pixelX <= width; pixelX++) {
        const waveformIndex = Math.floor(pixelX * pointsPerPixel)
        const value = waveform[Math.min(waveformIndex, waveform.length - 1)] || 0
        const y = midY + (value * midY * 1.3)
        if (pixelX === 0) {
          ctx.moveTo(pixelX, y)
        } else {
          ctx.lineTo(pixelX, y)
        }
      }
      ctx.stroke()
      ctx.globalAlpha = 1
    }

    ctx.shadowBlur = 0

    return () => window.removeEventListener('resize', resizeCanvas)
  }, [waveform, height])

  return (
    <div className="grid gap-2">
      <div ref={spectrumContainerRef}>
        <div className="text-xs text-muted-foreground mb-1 font-medium tracking-wide">FREQUENCY SPECTRUM</div>
        <canvas
          ref={spectrumCanvasRef}
          className="w-full border border-accent/40 rounded"
          style={{ height: `${height}px`, display: 'block' }}
        />
      </div>
      <div ref={waveformContainerRef}>
        <div className="text-xs text-muted-foreground mb-1 font-medium tracking-wide">AUDIO WAVEFORM</div>
        <canvas
          ref={waveformCanvasRef}
          className="w-full border border-accent/40 rounded"
          style={{ height: `${height / 2}px`, display: 'block' }}
        />
      </div>
    </div>
  )
})
