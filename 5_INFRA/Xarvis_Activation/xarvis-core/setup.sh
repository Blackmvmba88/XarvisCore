#!/bin/bash
echo "🔧 Instalando dependencias..."
pip install pyttsx3 sounddevice numpy scipy face_recognition opencv-python

echo "📁 Creando carpetas necesarias..."
mkdir -p Fotos/Mac Fotos/Celular Fotos/Raspberry

echo "✅ Listo. Puedes correr scripts desde la carpeta 'scripts'"
echo "🎤 Prueba el vumetro con: python3 scripts/vumeter_microphone.py"
echo "🧠 Entrena caras con: python3 scripts/face_train.py"
echo "🗣️ Prueba voz con: python3 scripts/speak.py"