import face_recognition
import numpy as np
import json

def encode_face(image_np):
    locations = face_recognition.face_locations(image_np)
    if len(locations) != 1:
        return None
    encodings = face_recognition.face_encodings(image_np, locations)
    if not encodings:
        return None
    return encodings[0].tolist()

def decode_face_encoding(enc):
    if enc is None:
        return None
    if isinstance(enc, str):
        try:
            enc = json.loads(enc)
        except Exception:
            return None
    return np.array(enc)

def compare_faces_batch(known_encodings, live_encoding, tolerance=0.5):
    known = [np.array(k) for k in known_encodings]
    live = np.array(live_encoding)
    matches = face_recognition.compare_faces(known, live, tolerance=tolerance)
    distances = face_recognition.face_distance(known, live)
    best_index = int(np.argmin(distances)) if len(distances) else None
    return matches, distances, best_index