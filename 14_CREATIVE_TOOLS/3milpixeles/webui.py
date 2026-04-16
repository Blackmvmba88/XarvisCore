from flask import Flask, request, send_file, render_template_string
from PIL import Image
import io

app = Flask(__name__)

# I will embed the HTML in the python file to make it a single file solution
INDEX_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Image Resizer 3000</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: #1a0033;
            color: white;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .container {
            background-color: #2D0052;
            padding: 2rem;
            border-radius: 1rem;
            box-shadow: 0 0 20px rgba(0, 255, 136, 0.5);
            text-align: center;
        }
        h1 {
            color: #00FF88;
        }
        input[type="file"] {
            margin-bottom: 1rem;
        }
        .modes {
            margin-bottom: 1rem;
        }
        .modes label {
            margin-right: 1rem;
        }
        button {
            background-color: #00FF88;
            color: #1a0033;
            border: none;
            padding: 0.8rem 1.5rem;
            font-size: 1rem;
            font-weight: bold;
            border-radius: 0.5rem;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>✨ Image Resizer 3000 ✨</h1>
        <p>Upload an image to resize it to 3000x3000 pixels.</p>
        <form action="/upload" method="post" enctype="multipart/form-data">
            <div>
                <input type="file" name="file" accept="image/*" required>
            </div>
            <div class="modes">
                <label>
                    <input type="radio" name="mode" value="fit" checked> Fit
                </label>
                <label>
                    <input type="radio" name="mode" value="fill"> Fill
                </label>
                <label>
                    <input type="radio" name="mode" value="stretch"> Stretch
                </label>
            </div>
            <button type="submit">🚀 Resize and Download</button>
        </form>
    </div>
</body>
</html>
"""

def resize_fit(img):
    """Redimensiona ajustando dentro del cuadrado con márgenes"""
    result = Image.new('RGB', (3000, 3000), (255, 255, 255))
    img.thumbnail((3000, 3000))
    x = (3000 - img.width) // 2
    y = (3000 - img.height) // 2
    result.paste(img, (x, y))
    return result

def resize_fill(img):
    """Redimensiona rellenando el cuadrado (recorta excedente)"""
    from PIL import ImageOps
    return ImageOps.fit(img, (3000, 3000))

def resize_stretch(img):
    """Estira la imagen a 3000x3000"""
    return img.resize((3000, 3000))

@app.route('/')
def index():
    return render_template_string(INDEX_HTML)

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return "No file part", 400
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400
    
    mode = request.form.get('mode', 'fit')

    if file:
        try:
            img = Image.open(file.stream)
            if img.mode != 'RGB':
                img = img.convert('RGB')

            if mode == 'fit':
                result_img = resize_fit(img)
            elif mode == 'fill':
                result_img = resize_fill(img)
            else: # stretch
                result_img = resize_stretch(img)
            
            output = io.BytesIO()
            result_img.save(output, 'PNG')
            output.seek(0)
            
            return send_file(output, mimetype='image/png', as_attachment=True, download_name='resized_image.png')
        except Exception as e:
            return f"Error processing image: {e}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)