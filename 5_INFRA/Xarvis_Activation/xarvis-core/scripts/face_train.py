import face_recognition
import os
import pickle

known_faces = {}
for folder in ['Fotos/Mac', 'Fotos/Celular', 'Fotos/Raspberry']:
    if not os.path.exists(folder): continue
    for file in os.listdir(folder):
        path = os.path.join(folder, file)
        image = face_recognition.load_image_file(path)
        encodings = face_recognition.face_encodings(image)
        if encodings:
            known_faces[file] = encodings[0]

with open("face_data.pickle", "wb") as f:
    pickle.dump(known_faces, f)

print("✔️ Caras entrenadas y guardadas.")