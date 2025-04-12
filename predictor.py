# predictor.py
import numpy as np
from PIL import Image, ExifTags
import cv2
from io import BytesIO
from model_loader import model

def preprocess_image(img: Image.Image) -> np.ndarray:
    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break
        exif = img._getexif()
        if exif is not None:
            orientation = exif.get(orientation)
            if orientation == 3:
                img = img.rotate(180, expand=True)
            elif orientation == 6:
                img = img.rotate(270, expand=True)
            elif orientation == 8:
                img = img.rotate(90, expand=True)
    except:
        pass

    img = np.array(img)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    img = cv2.resize(img, (640, 640))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = img / 255.0
    return img.astype(np.float32)

def run_inference(img: Image.Image):
    pre_img = preprocess_image(img)
    uint_img = (pre_img * 255).astype(np.uint8)
    pil_img = Image.fromarray(uint_img)

    results = model(pil_img)

    if not results or len(results) == 0:
        return [], "No anomalies", None

    detections = []
    for r in results:
        if r.boxes is None:
            continue
        for idx in range(len(r.boxes.xyxy)):
            if r.boxes.conf[idx] > 0.5:
                detections.append({
                    "class_id": int(r.boxes.cls[idx]),
                    "confidence": float(r.boxes.conf[idx]),
                    "xyxyn": r.boxes.xyxyn[idx].cpu().numpy().tolist()
                })

    output_image_np = results[0].plot()
    output_image_rgb = cv2.cvtColor(output_image_np, cv2.COLOR_BGR2RGB)
    output_image_pil = Image.fromarray(output_image_rgb)

    return detections, "Success", output_image_pil
