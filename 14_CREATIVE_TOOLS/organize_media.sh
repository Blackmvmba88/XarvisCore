#!/bin/bash

echo "🎬 ORGANIZADOR MULTIMEDIA BLACKMAMBA"
echo "===================================================="
echo ""
echo "¿Qué deseas organizar?"
echo ""
echo "1. 🎵 Música (ya organizada → 10_CULTURAL_RENAISSANCE)"
echo "2. 🎬 Películas (Downloads → ~/Movies/BlackMamba_Cinema)"
echo "3. 📸 Ambos"
echo "4. 📊 Ver estadísticas"
echo ""
read -p "Selecciona una opción (1-4): " option

VENV_PYTHON="/Users/blackmamba/Desktop/XarvisCore/venv/bin/python3"

case $option in
    1)
        echo ""
        echo "🎵 Organizando música..."
        cd /Users/blackmamba/Desktop/XarvisCore/10_CULTURAL_RENAISSANCE
        $VENV_PYTHON organize_music.py
        ;;
    2)
        echo ""
        echo "🎬 Modo de ejecución para películas:"
        echo "1. 🔍 Simulación (ver qué se haría)"
        echo "2. ✅ Ejecutar (mover archivos realmente)"
        read -p "Selecciona modo (1-2): " mode
        
        cd /Users/blackmamba/Desktop/XarvisCore/14_CREATIVE_TOOLS
        
        if [ "$mode" = "1" ]; then
            echo ""
            echo "🔍 MODO SIMULACIÓN..."
            $VENV_PYTHON movie_organizer.py
        else
            echo ""
            echo "⚠️  ¿Estás seguro? Esto moverá 64 archivos de Downloads"
            read -p "Confirmar (s/n): " confirm
            if [ "$confirm" = "s" ]; then
                # Cambiar DRY_RUN a False en el script
                sed -i.bak 's/DRY_RUN = True/DRY_RUN = False/' movie_organizer.py
                $VENV_PYTHON movie_organizer.py
                # Restaurar DRY_RUN a True
                sed -i.bak 's/DRY_RUN = False/DRY_RUN = True/' movie_organizer.py
                rm movie_organizer.py.bak
                echo ""
                echo "✅ Organización completada"
            else
                echo "❌ Cancelado"
            fi
        fi
        ;;
    3)
        echo ""
        echo "📸 Organizando ambos..."
        echo ""
        echo "🎵 [1/2] Organizando música..."
        cd /Users/blackmamba/Desktop/XarvisCore/10_CULTURAL_RENAISSANCE
        $VENV_PYTHON organize_music.py
        
        echo ""
        echo "🎬 [2/2] Organizando películas..."
        cd /Users/blackmamba/Desktop/XarvisCore/14_CREATIVE_TOOLS
        
        echo "⚠️  ¿Mover 64 archivos de Downloads?"
        read -p "Confirmar (s/n): " confirm
        if [ "$confirm" = "s" ]; then
            sed -i.bak 's/DRY_RUN = True/DRY_RUN = False/' movie_organizer.py
            $VENV_PYTHON movie_organizer.py
            sed -i.bak 's/DRY_RUN = False/DRY_RUN = True/' movie_organizer.py
            rm movie_organizer.py.bak
        fi
        ;;
    4)
        echo ""
        echo "📊 ESTADÍSTICAS"
        echo "===================================================="
        echo ""
        echo "🎵 MÚSICA:"
        cd /Users/blackmamba/Desktop/XarvisCore/10_CULTURAL_RENAISSANCE
        if [ -f "music_library.json" ]; then
            total_songs=$(cat music_library.json | grep -o '"song_name"' | wc -l)
            echo "   Total de canciones: $total_songs"
            echo "   📁 Ubicación: 10_CULTURAL_RENAISSANCE/BlackMamba_Music_Collection"
        fi
        
        echo ""
        echo "🎬 PELÍCULAS:"
        cd /Users/blackmamba/Desktop/XarvisCore/14_CREATIVE_TOOLS
        $VENV_PYTHON movie_organizer.py --stats 2>/dev/null || echo "   (Ejecuta organización primero)"
        ;;
    *)
        echo "❌ Opción inválida"
        exit 1
        ;;
esac

echo ""
echo "✅ Listo, hermano!"
