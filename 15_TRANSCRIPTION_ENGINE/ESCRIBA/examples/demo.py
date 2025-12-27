"""
Example usage of ESCRIBA for multi-language transcription and classification.

This demonstrates:
1. Language detection from text
2. Audio transcription with automatic language recognition
3. Intelligent content classification
4. Data storage and retrieval
"""

import asyncio
from escriba import create_escriba


async def main():
    """Main example function."""
    
    print("🚀 ESCRIBA - Multi-Language Speech-to-Text Platform")
    print("=" * 60)
    print()
    
    # Create ESCRIBA instance
    # This will use the 'small' Whisper model by default
    escriba = create_escriba(model_size="small")
    
    print("✅ ESCRIBA initialized")
    print(f"   Model: small")
    print(f"   Auto-detect: enabled")
    print()
    
    # Example 1: Test language detection
    print("📝 Example 1: Language Detection")
    print("-" * 60)
    
    test_texts = [
        "Hello, this is a test in English.",
        "Hola, esto es una prueba en español.",
        "Bonjour, ceci est un test en français.",
        "Hallo, dies ist ein Test auf Deutsch.",
        "こんにちは、これは日本語のテストです。",
    ]
    
    detector = escriba.language_detector
    
    for text in test_texts:
        detection = detector.detect(text)
        lang_name = detector.get_language_name(detection.language)
        print(f"   Text: {text[:40]}...")
        print(f"   → Language: {lang_name} ({detection.language})")
        print(f"   → Confidence: {detection.confidence:.2%}")
        print()
    
    # Example 2: Text classification
    print("📊 Example 2: Text Classification")
    print("-" * 60)
    
    classifier = escriba.classifier
    
    test_cases = [
        ("Let's discuss the API design for our new microservice architecture", "en"),
        ("The quarterly revenue exceeded expectations by 15 percent", "en"),
        ("La clase de hoy trata sobre algoritmos de búsqueda", "es"),
    ]
    
    for text, lang in test_cases:
        classification = classifier.classify(text, language=lang)
        print(f"   Text: {text[:50]}...")
        print(f"   → Category: {classification.category.value}")
        print(f"   → Confidence: {classification.confidence:.2%}")
        print(f"   → Tags: {', '.join(classification.tags)}")
        print(f"   → Keywords: {', '.join(classification.keywords[:3])}")
        print()
    
    # Example 3: Show statistics (if any data exists)
    print("📈 Example 3: System Statistics")
    print("-" * 60)
    
    lang_stats = escriba.get_language_statistics()
    if lang_stats:
        print("   Language Usage:")
        for lang_code, stats in lang_stats.items():
            print(f"   - {stats['name']}: {stats['segments']} segments, "
                  f"{stats['duration']:.1f}s total")
    else:
        print("   No transcription data yet.")
    print()
    
    category_stats = escriba.get_category_statistics()
    if category_stats:
        print("   Category Distribution:")
        for category, stats in category_stats.items():
            print(f"   - {category}: {stats['count']} transcripts")
    else:
        print("   No classification data yet.")
    print()
    
    print("=" * 60)
    print("✨ ESCRIBA is ready to process audio in ANY language!")
    print()
    print("To transcribe an audio file:")
    print("   result = await escriba.process_audio_file('path/to/audio.wav')")
    print()
    print("The system will:")
    print("   ✓ Automatically detect the language")
    print("   ✓ Transcribe with high accuracy")
    print("   ✓ Classify and tag the content")
    print("   ✓ Store everything in the database")
    print()


if __name__ == "__main__":
    asyncio.run(main())
