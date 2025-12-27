# Quantum Audio Player

Quantum Audio Player is an experimental high‑fidelity music player designed by **BlackMamba**.  
It marries a minimalistic design with cutting‑edge quantum‑inspired audio processing to deliver an unmatched listening experience.  
This repository contains a Python implementation of the Quantum Audio Player prototype, including a PyQt6 graphical interface, a simulated quantum DAC and DSP engine, scripts for macOS and Raspberry Pi, and a development roadmap.

## Features

- **Quantum‑inspired DAC** – A simulated digital‑to‑analog converter that applies a band‑pass filter and dynamic range optimisation to emulate noise‑free quantum quantisation.
- **AI‑powered DSP** – Real‑time analysis and optimisation of audio signals using algorithms from NumPy and SciPy.
- **Auto‑calibration** – The engine normalises output levels based on the characteristics of the loaded audio file.
- **Cross‑platform GUI** – A PyQt6 interface that allows you to load and control playback of `.wav` files.
- **Extensible architecture** – The codebase is structured for modular expansion (e.g., integration with actual quantum hardware, Bluetooth connectivity, etc.).

## Structure

```
quantum_audio_player/
├── README.md          – This document.
├── ROADMAP.md         – Development roadmap and philosophy.
├── LICENSE            – MIT license for the project.
├── requirements.txt    – Python dependencies.
├── run_mac.sh         – Convenience script for macOS.
├── run_rpi.sh         – Convenience script for Raspberry Pi.
└── src/
    ├── main.py        – Entry point for the PyQt6 application.
    └── player/
        ├── __init__.py
        ├── ui.py      – PyQt6 user interface.
        ├── quantum_engine.py – Simulated Quantum DAC and DSP.
        └── assets/
            └── concept.png   – Conceptual artwork (optional).
```

## Installation

Quantum Audio Player requires **Python 3.10** or later.

### macOS

1. Clone or download this repository.
2. Ensure Homebrew is installed: `brew update`.
3. Run the setup and launch script:

```bash
chmod +x run_mac.sh
./run_mac.sh
```

### Raspberry Pi (Raspberry Pi OS Bullseye or later)

1. Clone or download this repository.
2. Update your package list and install required system packages:

```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip libportaudio2
```

3. Run the setup and launch script:

```bash
chmod +x run_rpi.sh
./run_rpi.sh
```

### Manual installation

You can also set up a virtual environment and install dependencies manually:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python src/main.py
```

## Usage

Upon launching the application, you can load a `.wav` file via the **Load** button.  
The Quantum Audio Player processes the audio through its quantum‑inspired engine and plays it back through your default audio output.  
Use the **Play** and **Stop** buttons to control playback, and adjust the volume slider as desired.

## Philosophy – The Núcleo Mamba

The heart of this project, dubbed the **Núcleo Mamba**, embodies a design philosophy that strives for purity, precision and poetry:

- **Purity of sound** – Our algorithms aim to remove measurable distortion, preserving the natural dynamics of every note.
- **Precision engineering** – Each component, from the GUI to the DSP, is built with attention to detail, ensuring stability and reliability.
- **Poetry in technology** – The interface and code are crafted to be as elegant as the music they deliver, emphasising minimalism and user experience.

For a deeper look at future milestones and enhancements, see [ROADMAP.md](ROADMAP.md).

## License

This project is provided under the MIT License.  
See [LICENSE](LICENSE) for details.