import { useState, useEffect, useRef } from 'react'

interface AudioData {
  bass: number
  mid: number
  treble: number
  total: number
  waveform: number[]
  spectrum: number[]
}

export function useAudioAnalyzer(enabled: boolean) {
  const [audioData, setAudioData] = useState<AudioData>({
    bass: 0,
    mid: 0,
    treble: 0,
    total: 0,
    waveform: [],
    spectrum: []
  })
  const [hasPermission, setHasPermission] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  const audioContextRef = useRef<AudioContext | null>(null)
  const analyserRef = useRef<AnalyserNode | null>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const animationRef = useRef<number | null>(null)
  const sourceRef = useRef<MediaStreamAudioSourceNode | null>(null)
  const isCleaningUpRef = useRef(false)

  useEffect(() => {
    if (!enabled) {
      cleanup()
      return
    }

    let mounted = true

    const setupAudio = async () => {
      if (isCleaningUpRef.current) return

      try {
        const stream = await navigator.mediaDevices.getUserMedia({ 
          audio: {
            echoCancellation: true,
            noiseSuppression: true,
            autoGainControl: true
          }
        })
        
        if (!mounted || isCleaningUpRef.current) {
          stream.getTracks().forEach(track => track.stop())
          return
        }

        streamRef.current = stream

        const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)()
        const analyser = audioContext.createAnalyser()
        analyser.fftSize = 2048
        analyser.smoothingTimeConstant = 0.75
        analyser.minDecibels = -90
        analyser.maxDecibels = -10

        const source = audioContext.createMediaStreamSource(stream)
        source.connect(analyser)

        audioContextRef.current = audioContext
        analyserRef.current = analyser
        sourceRef.current = source

        if (!mounted || isCleaningUpRef.current) {
          cleanup()
          return
        }

        setHasPermission(true)
        setError(null)

        const bufferLength = analyser.frequencyBinCount
        const dataArray = new Uint8Array(bufferLength)
        const waveformArray = new Uint8Array(bufferLength)

        const analyze = () => {
          if (!analyserRef.current || isCleaningUpRef.current || !mounted) return

          analyserRef.current.getByteFrequencyData(dataArray)
          analyserRef.current.getByteTimeDomainData(waveformArray)

          const bass = Array.from(dataArray.slice(0, 50)).reduce((a, b) => a + b, 0) / 50
          const mid = Array.from(dataArray.slice(50, 500)).reduce((a, b) => a + b, 0) / 450
          const treble = Array.from(dataArray.slice(500, 1024)).reduce((a, b) => a + b, 0) / 524
          const total = (bass + mid + treble) / 3

          const spectrum = Array.from(dataArray.slice(0, 128)).map(v => v / 255)
          const waveform = Array.from(waveformArray.slice(0, 128)).map(v => (v - 128) / 128)

          if (mounted && !isCleaningUpRef.current) {
            setAudioData({ bass, mid, treble, total, spectrum, waveform })
            animationRef.current = requestAnimationFrame(analyze)
          }
        }

        analyze()
      } catch (err) {
        if (mounted) {
          setError('Acceso al micrófono denegado')
          setHasPermission(false)
        }
      }
    }

    setupAudio()

    return () => {
      mounted = false
      cleanup()
    }
  }, [enabled])

  const cleanup = () => {
    isCleaningUpRef.current = true

    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current)
      animationRef.current = null
    }

    if (sourceRef.current) {
      try {
        sourceRef.current.disconnect()
      } catch (e) {}
      sourceRef.current = null
    }

    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => {
        track.stop()
      })
      streamRef.current = null
    }

    if (audioContextRef.current) {
      if (audioContextRef.current.state !== 'closed') {
        audioContextRef.current.close().catch(() => {})
      }
      audioContextRef.current = null
    }

    analyserRef.current = null
    
    setAudioData({ bass: 0, mid: 0, treble: 0, total: 0, waveform: [], spectrum: [] })
    setHasPermission(false)
    
    setTimeout(() => {
      isCleaningUpRef.current = false
    }, 100)
  }

  return { audioData, hasPermission, error }
}
