from fastapi import FastAPI, File, UploadFile, Request, Depends
import tensorflow as tf
import numpy as np
from PIL import Image
import io
import cv2
import matplotlib.cm as cm
import base64
import tensorflow_addons as tfa
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from starlette.responses import JSONResponse
from utils import preprocess_image , generate_gradcam , overlay_heatmap,encode_image_to_base64
app = FastAPI()

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(429, _rate_limit_exceeded_handler)

MODEL_PATH = r'H:\article\modelstrainedv2test1-701515\efficientnetv2b0best.h5'
model = tf.keras.models.load_model(MODEL_PATH)

@app.post("/predict/")
@limiter.limit("3/minute")
async def predict(request: Request, file: UploadFile = File(...)):
    try:
        
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        processed_image = preprocess_image(image)
        predictions = model.predict(processed_image)
        predicted_class = int(np.argmax(predictions, axis=1)[0])
        confidence_scores = predictions.tolist()

        print(confidence_scores)
        heatmap = generate_gradcam(processed_image, model, predicted_class)
        gradcam_image = overlay_heatmap(image, heatmap)
        gradcam_base64 = encode_image_to_base64(gradcam_image)

        return {
            "predicted_class": predicted_class,
            "confidence_scores": confidence_scores,
            "gradcam_image": gradcam_base64
        }

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
