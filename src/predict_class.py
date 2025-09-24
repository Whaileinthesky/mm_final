# medicine_classifier.py
import json
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image

class predict_func:
    def __init__(self, model_path, class_indices_path, input_size=(512, 512)):
        # 모델 로드
        self.model = tf.keras.models.load_model(model_path)
        # class_indices 불러오기
        with open(class_indices_path, "r", encoding="utf-8") as f:
            class_indices = json.load(f)
        # index → label 변환
        self.idx_to_label = {v: k for k, v in class_indices.items()}
        self.input_size = input_size

    def predict(self, img_path):
        # 이미지 로드 및 전처리
        img = image.load_img(img_path, target_size=self.input_size)
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0) 
        x /= 255.0

        # 예측
        preds = self.model.predict(x)
        idx = np.argmax(preds)
        label = self.idx_to_label.get(idx, str(idx))
        return label
    

