import React, { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

interface AIMessageProps {
  message: string
  onComplete?: () => void
}

export function AIMessage({ message, onComplete }: AIMessageProps) {
  const [isVisible, setIsVisible] = useState(true)

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsVisible(false)
      onComplete?.()
    }, 4000)

    return () => clearTimeout(timer)
  }, [message, onComplete])

  return (
    <AnimatePresence>
      {isVisible && message && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          className="fixed bottom-8 left-1/2 -translate-x-1/2 z-50"
        >
          <div className="bg-accent/90 text-accent-foreground px-6 py-3 rounded border-2 border-accent shadow-lg shadow-accent/50">
            <div className="text-xs font-bold tracking-widest mb-1">SYSTEM RESPONSE</div>
            <div className="text-sm font-medium">{message}</div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
