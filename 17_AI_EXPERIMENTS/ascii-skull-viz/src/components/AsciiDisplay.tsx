import React, { useEffect, useRef, memo } from 'react'

interface AsciiDisplayProps {
  content: string
  fontSize?: number
  glitch?: boolean
}

export const AsciiDisplay = memo(function AsciiDisplay({ content, fontSize = 8, glitch = false }: AsciiDisplayProps) {
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (containerRef.current && glitch) {
      containerRef.current.classList.add('glitch')
      const timer = setTimeout(() => {
        containerRef.current?.classList.remove('glitch')
      }, 300)
      return () => clearTimeout(timer)
    }
  }, [glitch])

  return (
    <div className="overflow-auto bg-black/50 p-2 rounded border-2 border-primary/40 shadow-[0_0_20px_rgba(0,255,150,0.3)] h-[calc(100vh-12rem)] w-full">
      <div
        ref={containerRef}
        className="ascii-display w-full min-w-full h-full flex items-start justify-start transition-all duration-300 ease-out"
        style={{ 
          fontSize: `${fontSize}px`,
          lineHeight: '1.0',
          whiteSpace: 'pre',
          overflow: 'visible'
        }}
      >
        {content}
      </div>
    </div>
  )
})
