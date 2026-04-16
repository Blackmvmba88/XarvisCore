import React, { useState, useRef, useEffect } from 'react'
import { useKV } from '@github/spark/hooks'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Slider } from '@/components/ui/slider'
import { Switch } from '@/components/ui/switch'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  Microphone, 
  MicrophoneSlash, 
  VideoCamera, 
  UploadSimple,
  Play,
  Pause,
  Waveform,
  Image as ImageIcon,
  UserCircle
} from '@phosphor-icons/react'
import { toast } from 'sonner'
import { AsciiDisplay } from '@/components/AsciiDisplay'
import { FrequencyVisualizer } from '@/components/FrequencyVisualizer'
import { AudioLevelMeter } from '@/components/AudioLevelMeter'
import { AIMessage } from '@/components/AIMessage'
import { FaceOverlay } from '@/components/FaceOverlay'
import { PersonSetupDialog } from '@/components/PersonSetupDialog'
import { useAudioAnalyzer } from '@/hooks/use-audio-analyzer'
import { videoFrameToAscii, imageToAscii, mutateAscii, generatePatternAscii } from '@/lib/ascii-converter'
import { detectFaces, Person, FaceDetection } from '@/lib/face-detector'

const AI_MESSAGES = [
  "Energy detected.",
  "Frequency quantum active.",
  "Channeling vibration.",
  "Sonic peaks detected.",
  "Amplitude curve stable.",
  "The fire is alive.",
  "The system breathes with you.",
  "Observing resonance.",
  "Pulse aligned.",
  "I am here, with you."
]

function App() {
  const [audioEnabled, setAudioEnabled] = useState(false)
  const [showVisualizer, setShowVisualizer] = useState(true)
  const [videoPlaying, setVideoPlaying] = useState(false)
  const [usingCamera, setUsingCamera] = useState(false)
  const [usingImage, setUsingImage] = useState(false)
  const [asciiContent, setAsciiContent] = useState('')
  const [currentMessage, setCurrentMessage] = useState('')
  const [glitchEffect, setGlitchEffect] = useState(false)
  const [faceDetectionEnabled, setFaceDetectionEnabled] = useState(false)
  const [persons, setPersons] = useState<Person[]>([])
  const [showPersonDialog, setShowPersonDialog] = useState(false)
  const [videoSize, setVideoSize] = useState({ width: 0, height: 0 })
  
  const [asciiWidth, setAsciiWidth] = useKV<number>('ascii-width', 240)
  const [fontSize, setFontSize] = useKV<number>('font-size', 8)
  const [baseMutationRate, setBaseMutationRate] = useKV<number>('mutation-rate', 3)
  const [savedPersons, setSavedPersons] = useKV<Person[]>('saved-persons', [])
  
  const videoRef = useRef<HTMLVideoElement>(null)
  const imageRef = useRef<HTMLImageElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const imageInputRef = useRef<HTMLInputElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const faceCanvasRef = useRef<HTMLCanvasElement>(null)
  const animationRef = useRef<number | null>(null)
  const frameCountRef = useRef(0)
  const lastMessageTimeRef = useRef(0)
  const faceDetectionIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const { audioData, hasPermission, error } = useAudioAnalyzer(audioEnabled)

  useEffect(() => {
    if (savedPersons && savedPersons.length > 0) {
      setPersons(savedPersons)
    }
  }, [savedPersons])

  useEffect(() => {
    if (faceDetectionEnabled && faceCanvasRef.current && videoRef.current && (usingCamera || videoPlaying)) {
      if (faceDetectionIntervalRef.current) {
        clearInterval(faceDetectionIntervalRef.current)
      }

      const detectInterval = setInterval(async () => {
        if (!videoRef.current || !faceCanvasRef.current) return
        
        try {
          const faces = await detectFaces(videoRef.current, faceCanvasRef.current)
          
          setPersons((currentPersons) => {
            return currentPersons.map((person, index) => ({
              ...person,
              detections: faces[index] ? [faces[index]] : []
            }))
          })

          if (videoRef.current.videoWidth && videoRef.current.videoHeight) {
            setVideoSize({
              width: videoRef.current.videoWidth,
              height: videoRef.current.videoHeight
            })
          }
        } catch (error) {
          console.error('Face detection error:', error)
        }
      }, 1000)

      faceDetectionIntervalRef.current = detectInterval

      return () => {
        if (faceDetectionIntervalRef.current) {
          clearInterval(faceDetectionIntervalRef.current)
        }
      }
    } else {
      if (faceDetectionIntervalRef.current) {
        clearInterval(faceDetectionIntervalRef.current)
        faceDetectionIntervalRef.current = null
      }
      setPersons((currentPersons) => 
        currentPersons.map(p => ({ ...p, detections: [] }))
      )
    }
  }, [faceDetectionEnabled, usingCamera, videoPlaying])

  useEffect(() => {
    if (!canvasRef.current) return
    
    let lastFrameTime = 0
    const targetFPS = 30
    const frameInterval = 1000 / targetFPS
    let isRunning = true

    const renderFrame = (currentTime: number) => {
      if (!isRunning) return

      const elapsed = currentTime - lastFrameTime
      
      if (elapsed < frameInterval) {
        animationRef.current = requestAnimationFrame(renderFrame)
        return
      }
      
      lastFrameTime = currentTime - (elapsed % frameInterval)

      try {
        if (usingImage && imageRef.current && canvasRef.current) {
          const ascii = imageToAscii(imageRef.current, canvasRef.current, asciiWidth ?? 240)
          
          const audioLevel = (audioEnabled && hasPermission) ? audioData.total / 255 : 0
          const dynamicMutationRate = ((baseMutationRate ?? 3) / 100) + (audioLevel * 0.1)
          const mutated = mutateAscii(ascii, dynamicMutationRate)
          
          setAsciiContent(mutated)

          if (audioLevel > 0.7 && Date.now() - lastMessageTimeRef.current > 5000) {
            triggerAIMessage()
            lastMessageTimeRef.current = Date.now()
          }
        } else if (videoRef.current && canvasRef.current && (videoPlaying || usingCamera)) {
          const ascii = videoFrameToAscii(videoRef.current, canvasRef.current, asciiWidth ?? 240)
          
          const audioLevel = (audioEnabled && hasPermission) ? audioData.total / 255 : 0
          const dynamicMutationRate = ((baseMutationRate ?? 3) / 100) + (audioLevel * 0.1)
          const mutated = mutateAscii(ascii, dynamicMutationRate)
          
          setAsciiContent(mutated)

          if (audioLevel > 0.7 && Date.now() - lastMessageTimeRef.current > 5000) {
            triggerAIMessage()
            lastMessageTimeRef.current = Date.now()
          }
        } else if (!videoPlaying && !usingCamera && !usingImage) {
          const audioLevel = (audioEnabled && hasPermission) ? audioData.total / 255 : 0
          const calculatedHeight = Math.floor((asciiWidth ?? 240) * 0.35)
          const pattern = generatePatternAscii(
            asciiWidth ?? 240, 
            calculatedHeight, 
            frameCountRef.current,
            audioLevel,
            audioData.waveform
          )
          setAsciiContent(pattern)
          frameCountRef.current++
        }
      } catch (error) {
        console.error('Render error:', error)
      }

      animationRef.current = requestAnimationFrame(renderFrame)
    }

    animationRef.current = requestAnimationFrame(renderFrame)

    return () => {
      isRunning = false
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current)
      }
    }
  }, [videoPlaying, usingCamera, usingImage, asciiWidth, baseMutationRate, audioData, audioEnabled, hasPermission])

  const triggerAIMessage = async () => {
    setGlitchEffect(true)
    setTimeout(() => setGlitchEffect(false), 300)
    
    try {
      const prompt = 'Generate a short, mysterious, technical message (5-8 words) about detecting energy, frequencies, or quantum vibrations. Make it sound like an AI system observing reality. Return only the message text, nothing else.'
      const response = await window.spark.llm(prompt, 'gpt-4o-mini')
      setCurrentMessage(response.trim())
    } catch {
      const fallback = AI_MESSAGES[Math.floor(Math.random() * AI_MESSAGES.length)]
      setCurrentMessage(fallback)
    }
  }

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    if (!file.type.startsWith('video/')) {
      toast.error('Please upload a video file')
      return
    }

    const url = URL.createObjectURL(file)
    if (videoRef.current) {
      videoRef.current.src = url
      videoRef.current.loop = true
      videoRef.current.play()
      setVideoPlaying(true)
      setUsingCamera(false)
      setUsingImage(false)
      toast.success('Video loaded')
    }
  }

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    if (!file.type.startsWith('image/')) {
      toast.error('Please upload an image file')
      return
    }

    const url = URL.createObjectURL(file)
    const img = new Image()
    img.onload = () => {
      if (imageRef.current) {
        imageRef.current.src = url
        setUsingImage(true)
        setVideoPlaying(false)
        setUsingCamera(false)
        toast.success('Photo loaded')
      }
    }
    img.onerror = () => {
      toast.error('Failed to load image')
    }
    img.src = url
    if (imageRef.current) {
      imageRef.current.src = url
    }
  }

  const toggleCamera = async () => {
    if (usingCamera) {
      if (videoRef.current?.srcObject) {
        const stream = videoRef.current.srcObject as MediaStream
        stream.getTracks().forEach(track => track.stop())
        videoRef.current.srcObject = null
      }
      setUsingCamera(false)
      setVideoPlaying(false)
      toast.success('Camera disabled')
    } else {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true })
        if (videoRef.current) {
          videoRef.current.srcObject = stream
          videoRef.current.play()
          setUsingCamera(true)
          setVideoPlaying(false)
          setUsingImage(false)
          toast.success('Camera enabled')
        }
      } catch {
        toast.error('Camera access denied')
      }
    }
  }

  const togglePlayPause = () => {
    if (!videoRef.current || usingCamera) return

    if (videoPlaying) {
      videoRef.current.pause()
      setVideoPlaying(false)
    } else {
      videoRef.current.play()
      setVideoPlaying(true)
    }
  }

  const toggleAudio = () => {
    if (audioEnabled) {
      setAudioEnabled(false)
      toast.success('Audio reactivity disabled')
    } else {
      setAudioEnabled(true)
    }
  }

  const handleSavePersons = (newPersons: Person[]) => {
    setPersons(newPersons)
    setSavedPersons(newPersons)
    if (newPersons.length > 0) {
      setFaceDetectionEnabled(true)
      toast.success('Reconocimiento configurado')
    }
  }

  return (
    <div className="min-h-screen bg-background text-foreground p-2">
      <div className="mx-auto space-y-2">
        <header className="text-center py-3 border-b-2 border-primary shadow-[0_0_20px_rgba(0,255,150,0.3)]">
          <h1 className="text-2xl font-bold tracking-tight mb-1 bg-gradient-to-r from-primary via-accent to-primary bg-clip-text text-transparent animate-pulse">
            ASCII VISION ENGINE v5.0
          </h1>
          <p className="text-xs text-muted-foreground tracking-wide">
            REAL-TIME VIDEO/PHOTO TO ASCII CONVERTER WITH AUDIO REACTIVITY + FACE RECOGNITION
          </p>
        </header>

        <div className="grid lg:grid-cols-4 gap-2">
          <div className="lg:col-span-3 space-y-2">
            <div className="relative">
              <AsciiDisplay 
                content={asciiContent || 'NO SOURCE DETECTED\n\nUPLOAD VIDEO/PHOTO OR ENABLE CAMERA'} 
                fontSize={fontSize ?? 6}
                glitch={glitchEffect}
              />
              
              {faceDetectionEnabled && (usingCamera || videoPlaying) && (
                <FaceOverlay
                  persons={persons}
                  videoWidth={videoSize.width}
                  videoHeight={videoSize.height}
                  asciiWidth={asciiWidth ?? 240}
                />
              )}
            </div>

            <Card className="p-3 border-accent/30 shadow-[0_0_15px_rgba(180,100,255,0.2)]">
              <div className="flex flex-wrap gap-2">
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="video/*"
                  onChange={handleFileUpload}
                  className="hidden"
                />
                <input
                  ref={imageInputRef}
                  type="file"
                  accept="image/*"
                  onChange={handleImageUpload}
                  className="hidden"
                />
                <Button
                  onClick={() => fileInputRef.current?.click()}
                  variant="default"
                  className="gap-2 hover:shadow-[0_0_15px_rgba(0,255,150,0.5)] transition-all"
                >
                  <UploadSimple size={20} weight="bold" />
                  Upload Video
                </Button>
                <Button
                  onClick={() => imageInputRef.current?.click()}
                  variant="default"
                  className="gap-2 hover:shadow-[0_0_15px_rgba(0,255,150,0.5)] transition-all"
                >
                  <ImageIcon size={20} weight="bold" />
                  Upload Photo
                </Button>
                <Button
                  onClick={toggleCamera}
                  variant={usingCamera ? 'default' : 'secondary'}
                  className="gap-2 hover:shadow-[0_0_15px_rgba(0,255,150,0.5)] transition-all"
                >
                  <VideoCamera size={20} weight="bold" />
                  {usingCamera ? 'Stop Camera' : 'Use Camera'}
                </Button>
                {!usingCamera && !usingImage && (
                  <Button
                    onClick={togglePlayPause}
                    variant="secondary"
                    className="gap-2 hover:shadow-[0_0_15px_rgba(180,100,255,0.5)] transition-all"
                    disabled={!videoRef.current?.src}
                  >
                    {videoPlaying ? <Pause size={20} weight="fill" /> : <Play size={20} weight="fill" />}
                    {videoPlaying ? 'Pause' : 'Play'}
                  </Button>
                )}
                <Button
                  onClick={toggleAudio}
                  variant={audioEnabled ? 'default' : 'secondary'}
                  className="gap-2 hover:shadow-[0_0_15px_rgba(0,255,150,0.5)] transition-all"
                >
                  {audioEnabled ? <Microphone size={20} weight="fill" /> : <MicrophoneSlash size={20} weight="bold" />}
                  Audio Reactive
                </Button>
                <Button
                  onClick={() => setShowPersonDialog(true)}
                  variant={faceDetectionEnabled ? 'default' : 'secondary'}
                  className="gap-2 ml-auto hover:shadow-[0_0_15px_rgba(180,100,255,0.5)] transition-all"
                  style={faceDetectionEnabled ? { 
                    background: 'linear-gradient(135deg, rgb(180, 100, 255) 0%, rgb(120, 60, 200) 100%)',
                    boxShadow: '0 0 20px rgba(180,100,255,0.6)'
                  } : {}}
                >
                  <UserCircle size={20} weight={faceDetectionEnabled ? 'fill' : 'bold'} />
                  Reconocer Personas
                </Button>
              </div>
            </Card>

            {showVisualizer && audioEnabled && hasPermission && (
              <Card className="p-3">
                <FrequencyVisualizer 
                  spectrum={audioData.spectrum}
                  waveform={audioData.waveform}
                />
              </Card>
            )}
          </div>

          <div className="space-y-2">
            <Card className="p-3 border-accent/30 shadow-[0_0_15px_rgba(180,100,255,0.2)]">
              <div className="space-y-3">
                <div>
                  <Label className="text-xs font-medium tracking-wide text-accent">
                    ASCII WIDTH: {asciiWidth ?? 240}
                  </Label>
                  <Slider
                    value={[asciiWidth ?? 240]}
                    onValueChange={(val) => setAsciiWidth(val[0])}
                    min={60}
                    max={320}
                    step={10}
                    className="mt-2"
                  />
                </div>
                <div>
                  <Label className="text-xs font-medium tracking-wide text-accent">
                    FONT SIZE: {fontSize ?? 8}px
                  </Label>
                  <Slider
                    value={[fontSize ?? 8]}
                    onValueChange={(val) => setFontSize(val[0])}
                    min={4}
                    max={16}
                    step={1}
                    className="mt-2"
                  />
                </div>
                <div>
                  <Label className="text-xs font-medium tracking-wide text-accent">
                    MUTATION RATE: {baseMutationRate ?? 3}%
                  </Label>
                  <Slider
                    value={[baseMutationRate ?? 3]}
                    onValueChange={(val) => setBaseMutationRate(val[0])}
                    min={0}
                    max={15}
                    step={1}
                    className="mt-2"
                  />
                </div>
                <div className="flex items-center justify-between pt-1">
                  <Label className="text-xs font-medium tracking-wide text-accent">
                    <Waveform size={16} className="inline mr-2" />
                    SHOW VISUALIZER
                  </Label>
                  <Switch
                    checked={showVisualizer}
                    onCheckedChange={setShowVisualizer}
                  />
                </div>
              </div>
            </Card>

            {audioEnabled && (
              <Card className="p-3 border-accent/30 shadow-[0_0_15px_rgba(180,100,255,0.2)]">
                {hasPermission ? (
                  <AudioLevelMeter
                    bass={audioData.bass}
                    mid={audioData.mid}
                    treble={audioData.treble}
                    total={audioData.total}
                  />
                ) : (
                  <Alert className="border-accent/30">
                    <AlertDescription>
                      {error || 'Requesting microphone access...'}
                    </AlertDescription>
                  </Alert>
                )}
              </Card>
            )}

            <Card className="p-3 bg-card/50 border-accent/30 shadow-[0_0_15px_rgba(180,100,255,0.2)]">
              <div className="text-xs space-y-2">
                <div className="font-bold text-accent tracking-wide mb-2">SYSTEM INFO</div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Status:</span>
                  <span className="text-accent">
                    {usingCamera ? 'CAMERA' : usingImage ? 'PHOTO' : videoPlaying ? 'VIDEO' : 'IDLE'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Audio:</span>
                  <span className="text-accent">
                    {audioEnabled && hasPermission ? 'ACTIVE' : 'INACTIVE'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">FPS Target:</span>
                  <span className="text-accent">30</span>
                </div>
                {faceDetectionEnabled && (
                  <>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Face Detection:</span>
                      <span className="text-accent">ACTIVE</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Personas:</span>
                      <span className="text-accent">{persons.filter(p => p.detections.length > 0).length}/{persons.length}</span>
                    </div>
                  </>
                )}
              </div>
            </Card>
          </div>
        </div>
      </div>

      <video ref={videoRef} className="hidden" />
      <img ref={imageRef} className="hidden" alt="" />
      <canvas ref={canvasRef} className="hidden" />
      <canvas ref={faceCanvasRef} className="hidden" />

      {currentMessage && (
        <AIMessage 
          message={currentMessage} 
          onComplete={() => setCurrentMessage('')}
        />
      )}

      <PersonSetupDialog
        open={showPersonDialog}
        onClose={() => setShowPersonDialog(false)}
        onSave={handleSavePersons}
        initialPersons={persons}
      />
    </div>
  )
}

export default App
