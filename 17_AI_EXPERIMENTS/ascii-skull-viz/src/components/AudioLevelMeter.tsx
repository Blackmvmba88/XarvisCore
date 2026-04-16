import React, { memo } from 'react'
import { Progress } from '@/components/ui/progress'

interface AudioLevelMeterProps {
  bass: number
  mid: number
  treble: number
  total: number
}

export const AudioLevelMeter = memo(function AudioLevelMeter({ bass, mid, treble, total }: AudioLevelMeterProps) {
  const normalize = (value: number) => Math.min((value / 255) * 100, 100)

  return (
    <div className="space-y-3">
      <div className="text-xs font-medium tracking-wide text-accent">AUDIO LEVELS</div>
      <div className="space-y-2">
        <div>
          <div className="flex justify-between text-xs mb-1">
            <span className="text-foreground">BASS</span>
            <span className="text-primary">{Math.round(normalize(bass))}%</span>
          </div>
          <Progress value={normalize(bass)} className="h-2" />
        </div>
        <div>
          <div className="flex justify-between text-xs mb-1">
            <span className="text-foreground">MID</span>
            <span className="text-primary">{Math.round(normalize(mid))}%</span>
          </div>
          <Progress value={normalize(mid)} className="h-2" />
        </div>
        <div>
          <div className="flex justify-between text-xs mb-1">
            <span className="text-foreground">TREBLE</span>
            <span className="text-primary">{Math.round(normalize(treble))}%</span>
          </div>
          <Progress value={normalize(treble)} className="h-2" />
        </div>
        <div className="pt-2 border-t border-accent/30">
          <div className="flex justify-between text-xs mb-1">
            <span className="text-accent font-bold">TOTAL</span>
            <span className="text-accent font-bold">{Math.round(normalize(total))}%</span>
          </div>
          <Progress value={normalize(total)} className="h-3" />
        </div>
      </div>
    </div>
  )
})
