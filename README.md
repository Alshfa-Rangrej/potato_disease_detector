# Potato Leaf Disease Detector

A deep learning app that looks at a photo of a potato leaf and tells you whether it has **early blight**, **late blight**, or is **healthy**. It has three parts: a trained image classifier, a FastAPI backend that serves it, and a Streamlit web page where you upload a photo and see the result.

![App screenshot](screenshot.png)

## What it detects

| Class | What it means |
|---|---|
| Early blight | Fungal disease with dark brown, ring-shaped spots, usually on older leaves |
| Late blight | Fast-spreading disease with dark, water-soaked patches that can destroy a crop quickly |
| Healthy | No disease found |

## Results

| Metric | Value |
|---|---|
| Validation accuracy | **XX.X%** |
| Model | MobileNetV2 (transfer learning) |
| Input size | 128 x 128 RGB |

> Fill in the real numbers from your final training run. Add the confusion matrix image here too if you like.

## How it works

1. **Data:** about 2,150 leaf photos from the PlantVillage potato dataset, split 80% training and 20% validation. The healthy class is much smaller than the other two, so class weights are used during training.
2. **Augmentation:** random flips, rotation and zoom, so the model sees varied versions of each leaf.
3. **Model:** a pretrained MobileNetV2 feature extractor with a small classifier on top (global average pooling, dropout, and a 3-way softmax).
4. **Backend:** `main.py` loads the saved model and exposes a `/predict` endpoint with FastAPI.
5. **Frontend:** `app.py` is a Streamlit page that sends the uploaded photo to the backend and shows the prediction, confidence and basic advice.

## Project structure

```
.
├── updatedaccuracycnn.ipynb      # data loading, training, evaluation
├── potato_cnn_model.keras        # trained model (notebook output)
├── classification_report.txt     # class names saved by the notebook
├── leaf.JPG                      # sample leaf for testing
├── requirements.txt
├── potato-project/
│   ├── main.py                   # FastAPI backend
│   ├── app.py                    # Streamlit frontend
│   └── potato_cnn_model.keras    # model used by the backend
└── Potato___*/                   # dataset folders (one per class)
```

## Getting started

### 1. Clone and install

```bash
git clone https://github.com/Alshfa-Rangrej/potato_disease_detector.git
cd potato_disease_detector

python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux

pip install -r requirements.txt
```

### 2. Run the app

You need two terminals, both with the virtual environment active.

**Terminal 1: backend**

```bash
cd potato-project
uvicorn main:app --reload --port 8000
```

Wait until it prints `CNN Model loaded successfully in FastAPI!`.

**Terminal 2: frontend**

```bash
cd potato-project
streamlit run app.py
```

Open http://localhost:8501, upload a potato leaf photo and select **Check this leaf**.

### 3. Retrain the model (optional)

Open `updatedaccuracycnn.ipynb`, choose **Restart & Run All**, and wait for training to finish. The notebook saves a new `potato_cnn_model.keras`. Copy it into `potato-project/` so the backend uses it.

## API

`POST /predict` with an image sent as form field `file`.

Example response:

```json
{
  "class": "Potato___Early_blight",
  "confidence": 97.5
}
```

`confidence` is a percentage. Interactive docs are available at http://127.0.0.1:8000/docs while the backend is running.

## Tips for good predictions

- Photograph a single leaf in daylight and keep it in focus.
- Fill most of the frame with the leaf and use a plain background.
- Results below 70% confidence are flagged in the app. Try a clearer photo.

## Limitations

- The model only knows three classes. A leaf with another disease, or something that isn't a potato leaf, will still be forced into one of them.
- It was trained on clean PlantVillage photos, so field photos with cluttered backgrounds may be less accurate.
- The prediction is an estimate from one photo. Confirm with a local agriculture officer before making treatment decisions.

## Future work

- Add more disease classes and real field photos.
- Deploy the backend and frontend online.
- Show the probability of every class, not just the top one.

## Tech stack

Python, TensorFlow / Keras, FastAPI, Uvicorn, Streamlit, Pillow, NumPy, scikit-learn, Matplotlib

## Acknowledgements

Dataset: PlantVillage potato leaf images.
