# Planning Guide

A web-based ASCII art video and photo player with real-time audio visualization that converts video frames and photos to ASCII characters and responds to microphone input with dynamic effects.

**Experience Qualities**:
1. **Hypnotic** - The continuously transforming ASCII art should draw users into a mesmerizing visual experience
2. **Reactive** - The system responds immediately to audio input, creating a living, breathing digital organism
3. **Technical** - Exposed waveforms and frequency data celebrate the computational nature of the art

**Complexity Level**: Light Application (multiple features with basic state)
  - Features video-to-ASCII conversion, audio visualization, and real-time effects but maintains focused functionality

## Essential Features

### Video/Photo to ASCII Conversion
- **Functionality**: Converts uploaded video frames, photos, or webcam feed into ASCII art using character density mapping
- **Purpose**: Creates the core visual experience of seeing visual media rendered as text characters
- **Trigger**: User uploads a video/photo file or enables webcam
- **Progression**: File upload/camera enable → Frame/image capture → Grayscale conversion → Character mapping → Display render
- **Success criteria**: Smooth 30fps ASCII rendering for videos that clearly represents the source content, static high-quality ASCII for photos

### Audio Reactivity
- **Functionality**: Captures microphone input, performs FFT analysis, and modulates ASCII mutation rate based on audio levels
- **Purpose**: Creates interactive feedback between user's environment and the visual display
- **Trigger**: User grants microphone permission
- **Progression**: Mic permission → Audio capture → FFT analysis → Frequency band separation → Mutation rate calculation → Visual response
- **Success criteria**: Visible character mutations and effects that correlate with audio amplitude, sub-100ms latency

### Frequency Visualization
- **Functionality**: Displays real-time waveform and frequency spectrum graphs
- **Purpose**: Provides technical insight into the audio analysis driving the visual effects
- **Trigger**: Audio capture is active
- **Progression**: Audio data → FFT transformation → Graph data preparation → Canvas rendering
- **Success criteria**: Smooth 60fps graph updates with distinct bass, mid, and treble frequency bands

### AI Voice Responses
- **Functionality**: Triggers AI-generated contextual messages when audio exceeds thresholds
- **Purpose**: Creates personality and conversational interaction with the system
- **Trigger**: Audio level surpasses 70% of dynamic range
- **Progression**: Threshold detection → LLM prompt generation → Response display → Fade out
- **Success criteria**: Contextually relevant messages that appear naturally during high-energy moments

## Edge Case Handling

- **No media source** - Display animated pattern or example ASCII art with clear upload prompt
- **Microphone denied** - Continue with video/photo playback, disable audio-reactive features with notification
- **Unsupported video format** - Show error message with supported formats list (MP4, WebM)
- **Unsupported image format** - Show error message with supported formats list (JPG, PNG, WebP)
- **Video/image loading failure** - Fallback to webcam option with clear error message
- **Audio processing overload** - Throttle FFT calculations to maintain performance
- **No webcam available** - Disable camera option, require video/photo upload

## Design Direction

The design should feel technical and futuristic with a command-line aesthetic - like looking at a living terminal from a sci-fi film. The interface should be minimal and dark, letting the ASCII art dominate while technical readouts provide ambient context. Think Blade Runner meets The Matrix terminal sessions.

## Color Selection

Analogous color scheme using green-cyan spectrum to evoke classic terminal displays with modern vibrancy

- **Primary Color**: Terminal Green (oklch(0.72 0.19 145)) - Represents the main ASCII art display, communicating retro computing and digital life
- **Secondary Colors**: Deep Black (oklch(0.12 0 0)) for backgrounds, Dark Charcoal (oklch(0.18 0 0)) for panels
- **Accent Color**: Cyan Glow (oklch(0.75 0.15 195)) - Highlights active audio reactivity and threshold events
- **Foreground/Background Pairings**:
  - Background (Deep Black oklch(0.12 0 0)): Terminal Green text (oklch(0.72 0.19 145)) - Ratio 8.2:1 ✓
  - Card (Dark Charcoal oklch(0.18 0 0)): Muted Green text (oklch(0.65 0.15 145)) - Ratio 5.4:1 ✓
  - Primary (Terminal Green oklch(0.72 0.19 145)): Black text (oklch(0.12 0 0)) - Ratio 8.2:1 ✓
  - Accent (Cyan Glow oklch(0.75 0.15 195)): Black text (oklch(0.12 0 0)) - Ratio 8.9:1 ✓

## Font Selection

Monospace typefaces that reinforce the computational nature and maintain the ASCII art grid alignment - using JetBrains Mono for its excellent readability and technical aesthetic.

- **Typographic Hierarchy**:
  - H1 (App Title): JetBrains Mono Bold/32px/tight tracking (-0.02em)
  - H2 (Section Headers): JetBrains Mono Medium/18px/normal tracking
  - ASCII Display: JetBrains Mono Regular/8px/tight line-height (1.0)
  - Body Text: JetBrains Mono Regular/14px/relaxed line-height (1.5)
  - Labels: JetBrains Mono Medium/12px/wide tracking (0.05em)

## Animations

Animations should be subtle and functional, reinforcing the technical nature without distraction - primarily used for data visualization and state transitions.

- **Purposeful Meaning**: Smooth waveform animations and frequency bar movements communicate real-time data flow; glitch effects during high audio levels reinforce the reactive nature
- **Hierarchy of Movement**: ASCII mutations are primary, waveforms secondary, UI controls tertiary - focus follows the audio energy

## Component Selection

- **Components**: 
  - Card for control panels and info displays with dark semi-transparent backgrounds
  - Button for primary actions (upload video/photo, toggle camera) with terminal-style borders
  - Slider for mutation rate and character density controls
  - Switch for toggling audio reactivity and visualization modes
  - Progress bar for audio level meters
  - Alert for permission requests and error states with green/cyan styling
  
- **Customizations**: 
  - Custom ASCII canvas renderer component (not in shadcn)
  - Custom frequency spectrum visualizer using canvas
  - Custom waveform display component
  - Glitch text effect component for AI messages
  
- **States**: 
  - Buttons use green hover glow with slight scale (1.02x)
  - Inputs show cyan focus rings
  - Sliders have green fills that pulse during audio peaks
  - Switches illuminate cyan when active
  
- **Icon Selection**: 
  - Microphone/MicrophoneSlash for audio toggle
  - VideoCamera for webcam controls
  - UploadSimple for file uploads
  - Image for photo uploads
  - Waveform for audio visualization
  - Play/Pause for video controls
  - Sliders for parameter controls
  
- **Spacing**: 
  - Consistent 4-unit (1rem) grid for major sections
  - 2-unit (0.5rem) gaps within control groups
  - 1-unit (0.25rem) tight spacing for data displays
  
- **Mobile**: 
  - Stack control panels vertically below ASCII display
  - Reduce ASCII character width for portrait orientation
  - Collapse frequency visualizer to simplified bar chart
  - Touch-friendly 44px minimum button sizes
  - Full-screen ASCII option that hides controls
