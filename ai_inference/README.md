# Member 3 – AI Skin Disease Classification

**Role:** Skin lesion classifier (7 classes). Default backbone: **EfficientNetB0** for best accuracy. Can use multiple datasets from Kaggle (and similar) for a stronger model.

**Classes:** Actinic keratosis, Basal cell carcinoma, Benign keratosis, Dermatofibroma, Melanoma, Melanocytic nevus, Vascular lesion.

## Setup

```bash
cd ai_inference
pip install -r requirements.txt
```

## Run prediction API

```bash
set SKIN_MODEL_WEIGHTS=C:\path\to\skin_model.weights.h5
python -m uvicorn api.main:app --host 0.0.0.0 --port 8002
```

- `GET /health` — health check  
- `POST /predict` — multipart `file` or JSON `{ "processed_image_b64": "..." }`

---

## Train a really good model (recommended)

Use **multiple datasets** from Kaggle and **EfficientNetB0** with strong augmentation and class weights.

### 1. Install Kaggle CLI and add API key

```bash
pip install kaggle
```

- Go to [Kaggle → Account → Create New Token](https://www.kaggle.com/settings).
- Save `kaggle.json` to:
  - **Windows:** `%USERPROFILE%\.kaggle\`
  - **Mac/Linux:** `~/.kaggle/`

### 2. Download several datasets

```bash
cd ai_inference
python scripts/download_all_datasets.py --out_dir "C:/data/skin_combined" --datasets all
```

This pulls:

- **ham10000** — [Skin Cancer MNIST HAM10000](https://www.kaggle.com/datasets/kmader/skin-cancer-mnist-ham10000) (~10k images, 7 classes)
- **ham10000_isic** — [Skin Disease Detection HAM10000+ISIC](https://www.kaggle.com/datasets/nour12347653/skin-disease-detection-dataset-ham10000-isic)
- **melanoma10k** — [Melanoma Skin Cancer Dataset of 10000 Images](https://www.kaggle.com/datasets/hasnainjaved/melanoma-skin-cancer-dataset-of-10000-images)

To download only HAM10000:

```bash
python scripts/download_all_datasets.py --out_dir "C:/data/skin_combined" --datasets ham10000
```

### 3. Merge (if you downloaded more than one)

```bash
python scripts/merge_datasets.py --data_dir "C:/data/skin_combined" --out merged
```

This creates `C:/data/skin_combined/merged/train/` with one folder per class.

### 4. Train with EfficientNet (high accuracy)

**From merged folders:**

```bash
python scripts/train_advanced.py --data_dir "C:/data/skin_combined/merged/train" --use_folders --epochs 40 --batch_size 32
```

**From a single HAM10000 (CSV + images):**

```bash
python scripts/train_advanced.py --data_dir "C:/data/ham10000" --csv HAM10000_metadata.csv --images_dir images --epochs 40
```

Training uses:

- **EfficientNetB0** (default)
- Strong augmentation (rotation, zoom, flip, contrast, brightness)
- **Class weights** for imbalanced classes
- **ReduceLROnPlateau** and **EarlyStopping**
- Saves `weights/skin_model.weights.h5` and `weights/skin_model.weights_config.json` (backbone name for the API)

### 5. Use the trained model

Weights path:

- Either copy `weights/skin_model.weights.h5` (and `*_config.json`) into `ai_inference/weights/`,
- Or set: `set SKIN_MODEL_WEIGHTS=C:\path\to\skin_model.weights.h5`

Then start the API; it will load the backbone from the config file.

---

## Single-dataset training (HAM10000 only)

If you only use HAM10000:

```bash
python scripts/download_ham10000.py --out_dir "C:/data/ham10000"
python scripts/train_ham10000.py --data_dir "C:/data/ham10000" --csv HAM10000_metadata.csv --images_dir images --epochs 25
```

Or use **EfficientNet** and more epochs:

```bash
python scripts/train_advanced.py --data_dir "C:/data/ham10000" --csv HAM10000_metadata.csv --images_dir images --epochs 40
```

---

## Backbone and env

- **EfficientNetB0** (default): better accuracy, more compute. Set `SKIN_BACKBONE=efficientnetb0` (or rely on saved config).
- **MobileNetV2**: faster and lighter. Set `SKIN_BACKBONE=mobilenetv2` before starting the API if your weights were trained with it.

---

## Disclaimer

Not for clinical or diagnostic use. For demo and education only.
