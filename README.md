# SmartSort – Streamlit Prototype

AI-powered household recycling classification app.

## Setup

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Pages

| Page | Description |
|------|-------------|
| 📷 Camera | Upload a photo and classify the item |
| ← Result | See the classification verdict, bin, and tip |
| Profile → | View recycling stats, scan history, sign in/out |

## Connecting your YOLO model

In `app.py`, find this block inside `page_camera()`:

```python
# ── Simulated classification (swap this for your YOLO model) ──────────
item_name = random.choice(list(RECYCLABLE_MAP.keys()))
result = {"item": item_name, **RECYCLABLE_MAP[item_name]}
```

Replace it with your actual YOLOv8 inference, for example:

```python
from ultralytics import YOLO
from PIL import Image
import numpy as np

model = YOLO("models/waste_classifier_fast/weights/best.pt")

img = Image.open(st.session_state.uploaded_img)
results = model(np.array(img), conf=0.25, verbose=False)
boxes = results[0].boxes

if boxes:
    cls_id    = int(boxes[0].cls[0])
    item_name = model.names[cls_id]
    # map item_name to your RECYCLABLE_MAP entries
```
