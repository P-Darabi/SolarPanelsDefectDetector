# api.py
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse, StreamingResponse
from predictor import run_inference
from PIL import Image
from io import BytesIO

app = FastAPI(title="Solar Panel Anomaly Detector API")

@app.get("/")
def root():
    return {"message": "Welcome to the Solar Panel Anomaly Detection API!"}

@app.post("/predict/", response_class=StreamingResponse)
async def predict_image(file: UploadFile = File(...)):
    try:
        img = Image.open(file.file)
        detections, msg, output_image = run_inference(img)

        if output_image is None:
            return JSONResponse(content={"status": msg, "detections": detections}, status_code=200)

        img_io = BytesIO()
        output_image.save(img_io, format='JPEG')
        img_io.seek(0)

        return StreamingResponse(
            img_io,
            media_type="image/jpeg",
            headers={
                "X-Anomaly-Count": str(len(detections)),
                "X-Detection-Result": msg
            }
        )

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
