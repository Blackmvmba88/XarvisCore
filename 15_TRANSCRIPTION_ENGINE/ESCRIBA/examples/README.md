# ESCRIBA Examples

This directory contains examples demonstrating the multi-language recognition and intelligent classification capabilities of ESCRIBA.

## Running the Demo

```bash
# Install ESCRIBA
pip install -e .

# Run the demo
python examples/demo.py
```

## What the Demo Shows

The demo demonstrates:

1. **Multi-Language Detection**: Automatic detection of text in various languages (English, Spanish, French, German, Japanese, etc.)

2. **Intelligent Classification**: Categorization of content into types like:
   - Technical
   - Business
   - Educational
   - Conversation
   - And more...

3. **Statistics Tracking**: View usage statistics by language and category

## Processing Audio Files

To process an actual audio file:

```python
import asyncio
from escriba import create_escriba

async def process_audio():
    escriba = create_escriba()
    
    # Process audio file - automatically detects language
    result = await escriba.process_audio_file('path/to/audio.wav')
    
    print(f"Language: {result['language']}")
    print(f"Category: {result['category']}")
    print(f"Transcription: {result['full_text']}")
    
    # Export to Markdown
    escriba.export_session()

asyncio.run(process_audio())
```

## Supported Languages

ESCRIBA supports 99+ languages through Whisper, including:
- Spanish (es)
- English (en)
- French (fr)
- German (de)
- Italian (it)
- Portuguese (pt)
- Russian (ru)
- Chinese (zh)
- Japanese (ja)
- Korean (ko)
- Arabic (ar)
- And many more...

The system automatically detects and adapts to ANY language!

## Features

### ✅ Multi-Language Recognition
- Automatic language detection from audio
- Support for 99+ languages via Whisper
- Dual-detector validation for higher accuracy

### ✅ Intelligent Classification
- Automatic content categorization
- Keyword extraction
- Tag generation
- Sentiment analysis
- Language-aware processing

### ✅ System Adaptation
- Works on any system with Python 3.11+
- Adapts to different audio formats
- Configurable model sizes (tiny to large)
- Local processing (no cloud required)
