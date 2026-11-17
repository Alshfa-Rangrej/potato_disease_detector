from fastapi import FastAPI, File, UploadFile
import tensorflow as tf
import numpy as np
from io import BytesIO
from PIL import Image

app = FastAPI()

# Load the trained CNN model
try:
    MODEL = tf.keras.models.load_model("potato_cnn_model.keras")
    print("CNN Model loaded successfully in FastAPI!")
except Exception as e:
    print(f"Error loading model: {e}")

# Class names matching your dataset categories
CLASS_NAMES = ["Potato___Early_blight", "Potato___Late_blight", "Potato___healthy"]

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    # Read image bytes uploaded from Streamlit
    image_bytes = await file.read()
    
    # Preprocess the image to match your model's input size (e.g., 128x128)
    image_pil = Image.open(BytesIO(image_bytes)).convert("RGB").resize((128, 128))
    img_array = tf.keras.utils.img_to_array(image_pil)
    img_array = np.expand_dims(img_array, axis=0) # Add batch dimension
    
    # Run prediction
    predictions = MODEL.predict(img_array)
    predicted_class = CLASS_NAMES[np.argmax(predictions[0])]
    confidence = float(np.max(predictions[0])) * 100
    
    return {
        "class": predicted_class,
        "confidence": round(confidence, 2)
    }
