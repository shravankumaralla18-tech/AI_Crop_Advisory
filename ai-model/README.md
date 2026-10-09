# AI model

Leaf-image classifier for crop diseases (MobileNetV2 transfer learning, Keras).

## 1. Install

```bash
cd ai-model
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

On Windows PowerShell, use `py -3.11 -m venv .venv` and `\.venv\Scripts\Activate.ps1` instead of the Unix activation command.

## 2. Prepare data

Put one folder per class in `dataset/raw/`, named like the PlantVillage dataset, for example `Tomato___Early_blight` (crop, three underscores, disease). Healthy classes end in `___healthy`.
The backend reads these names to look up treatment text in `data/diseases/`, so add an entry there for every new class.

```bash
python preprocessing/data_split.py      # 70% train, 15% val, 15% test
```

## 3. Train and evaluate

```bash
python training/train.py --epochs 10 --fine-tune-epochs 5
python training/evaluate.py
```

Training writes `models/crop_disease_model.keras` and `models/class_names.json`. The `class_names.json` in the repo is only a placeholder and is overwritten by training.

## 4. Predict

```bash
python prediction/predict.py path/to/leaf.jpg
```

The FastAPI backend imports `prediction.predict.predict_image_bytes` directly.
