import os
import json
from PIL import Image
import numpy as np
DATASET_PATH = "dataset"
OUTPUT_DB = "output/quantization_db.json"
def extract_qtables(img_path):
    img = Image.open(img_path)
    qtables = img.quantization
    data = {}
    if 0 in qtables:
        data["Y"] = np.array(qtables[0]).reshape((8, 8)).tolist()
    if 1 in qtables:
        chroma = np.array(qtables[1]).reshape((8, 8)).tolist()
        data["Cb"] = chroma
        data["Cr"] = chroma
    return data
def build_database(dataset_path):
    database = {}
    for software in os.listdir(dataset_path):
        software_path = os.path.join(dataset_path, software)
        if not os.path.isdir(software_path):
            continue
        print(f"[+] Processando: {software}")
        database[software] = {}
        for file in os.listdir(software_path):
            if not file.lower().endswith(".jpg"):
                continue
            quality = os.path.splitext(file)[0]  # "1.jpg" -> "1"
            img_path = os.path.join(software_path, file)
            try:
                qdata = extract_qtables(img_path)
                database[software][int(quality)] = qdata
                print(f"  └─ Qualidade {quality}% OK")
            except Exception as e:
                print(f"  [ERRO] {software}/{file}: {e}")
    return database
if __name__ == "__main__":
    db = build_database(DATASET_PATH)
    with open(OUTPUT_DB, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=4)
    print(f"\nBanco de dados salvo em: {OUTPUT_DB}")
