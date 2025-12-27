import React, { memo } from 'react'
import { motion } from 'framer-motion'
import { Person, FaceDetection } from '@/lib/face-detector'

interface FaceOverlayProps {
  persons: Person[]
  videoWidth: number
  videoHeight: number
  asciiWidth: number
}

export const FaceOverlay = memo(function FaceOverlay({ persons, videoWidth, videoHeight, asciiWidth }: FaceOverlayProps) {
  if (!videoWidth || !videoHeight) return null

  const scaleX = asciiWidth / videoWidth
  const scaleY = scaleX / 2

  return (
    <div className="absolute inset-0 pointer-events-none overflow-hidden">
      {persons.map((person) =>
        person.detections.map((detection, idx) => {
          const x = detection.x * scaleX
          const y = detection.y * scaleY
          const width = detection.width * scaleX
          const height = detection.height * scaleY

          return (
            <motion.div
              key={`${person.id}-${idx}`}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              className="absolute"
              style={{
                left: `${x}px`,
                top: `${y}px`,
                width: `${width}px`,
                height: `${height}px`,
                border: `2px solid ${person.color}`,
                boxShadow: `0 0 20px ${person.color}`,
              }}
            >
              <motion.div
                className="absolute -top-8 left-0 px-3 py-1 rounded-md text-xs font-bold tracking-wide"
                style={{
                  backgroundColor: person.color,
                  color: '#000',
                }}
                initial={{ y: -10, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ delay: 0.1 }}
              >
                {person.name}
              </motion.div>

              <div
                className="absolute inset-0"
                style={{
                  background: `linear-gradient(to bottom, ${person.color}22, transparent)`,
                }}
              />

              <motion.div
                className="absolute top-0 left-0 right-0 h-0.5"
                style={{ backgroundColor: person.color }}
                animate={{ scaleX: [0, 1, 0] }}
                transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
              />
            </motion.div>
          )
        })
      )}
    </div>
  )
})
