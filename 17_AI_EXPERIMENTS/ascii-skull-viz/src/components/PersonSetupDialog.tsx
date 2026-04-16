import React, { useState } from 'react'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Person } from '@/lib/face-detector'
import { UserCircle, Check } from '@phosphor-icons/react'

interface PersonSetupDialogProps {
  open: boolean
  onClose: () => void
  onSave: (persons: Person[]) => void
  initialPersons?: Person[]
}

const PRESET_COLORS = [
  '#00ff88',
  '#ff00ff',
  '#00ffff',
  '#ffff00',
  '#ff8800',
  '#8800ff',
]

export function PersonSetupDialog({ open, onClose, onSave, initialPersons }: PersonSetupDialogProps) {
  const [person1Name, setPerson1Name] = useState(initialPersons?.[0]?.name || '')
  const [person2Name, setPerson2Name] = useState(initialPersons?.[1]?.name || '')
  const [person1Color, setPerson1Color] = useState(initialPersons?.[0]?.color || PRESET_COLORS[0])
  const [person2Color, setPerson2Color] = useState(initialPersons?.[1]?.color || PRESET_COLORS[1])

  const handleSave = () => {
    const persons: Person[] = []
    
    if (person1Name.trim()) {
      persons.push({
        id: 'person-1',
        name: person1Name.trim(),
        color: person1Color,
        detections: []
      })
    }
    
    if (person2Name.trim()) {
      persons.push({
        id: 'person-2',
        name: person2Name.trim(),
        color: person2Color,
        detections: []
      })
    }
    
    onSave(persons)
    onClose()
  }

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md border-accent shadow-[0_0_30px_rgba(180,100,255,0.4)]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <UserCircle size={24} weight="bold" className="text-accent" />
            CONFIGURAR RECONOCIMIENTO
          </DialogTitle>
          <DialogDescription className="text-muted-foreground">
            Configura los nombres y colores para reconocer a dos personas en el video
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 py-4">
          <div className="space-y-3">
            <Label className="text-xs font-bold tracking-wide text-primary">PERSONA 1</Label>
            <Input
              placeholder="Nombre de la persona 1"
              value={person1Name}
              onChange={(e) => setPerson1Name(e.target.value)}
              className="font-mono border-primary/40"
            />
            <div className="space-y-2">
              <Label className="text-xs font-medium tracking-wide">Color de etiqueta</Label>
              <div className="flex gap-2">
                {PRESET_COLORS.map((color) => (
                  <button
                    key={color}
                    onClick={() => setPerson1Color(color)}
                    className="w-10 h-10 rounded-md border-2 transition-all hover:scale-110"
                    style={{
                      backgroundColor: color,
                      borderColor: person1Color === color ? '#fff' : 'transparent',
                      boxShadow: person1Color === color ? `0 0 15px ${color}` : 'none'
                    }}
                  >
                    {person1Color === color && (
                      <Check size={20} weight="bold" className="mx-auto" style={{ color: '#000' }} />
                    )}
                  </button>
                ))}
              </div>
            </div>
          </div>

          <div className="border-t border-accent/30 pt-4 space-y-3">
            <Label className="text-xs font-bold tracking-wide text-accent">PERSONA 2</Label>
            <Input
              placeholder="Nombre de la persona 2"
              value={person2Name}
              onChange={(e) => setPerson2Name(e.target.value)}
              className="font-mono border-accent/40"
            />
            <div className="space-y-2">
              <Label className="text-xs font-medium tracking-wide">Color de etiqueta</Label>
              <div className="flex gap-2">
                {PRESET_COLORS.map((color) => (
                  <button
                    key={color}
                    onClick={() => setPerson2Color(color)}
                    className="w-10 h-10 rounded-md border-2 transition-all hover:scale-110"
                    style={{
                      backgroundColor: color,
                      borderColor: person2Color === color ? '#fff' : 'transparent',
                      boxShadow: person2Color === color ? `0 0 15px ${color}` : 'none'
                    }}
                  >
                    {person2Color === color && (
                      <Check size={20} weight="bold" className="mx-auto" style={{ color: '#000' }} />
                    )}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

        <div className="flex justify-end gap-2 pt-4 border-t border-accent/30">
          <Button variant="secondary" onClick={onClose}>
            Cancelar
          </Button>
          <Button 
            onClick={handleSave}
            disabled={!person1Name.trim() && !person2Name.trim()}
            className="bg-accent hover:bg-accent/90 text-accent-foreground hover:shadow-[0_0_15px_rgba(180,100,255,0.5)]"
          >
            Guardar
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}
