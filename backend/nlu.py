import os
import pickle


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, "models")

with open(os.path.join(MODEL_DIR, "intent_model.pkl"), "rb") as f:
    model = pickle.load(f)

with open(os.path.join(MODEL_DIR, "vectorizer.pkl"), "rb") as f:
    vectorizer = pickle.load(f)

with open(os.path.join(MODEL_DIR, "label_encoder.pkl"), "rb") as f:
    label_encoder = pickle.load(f)


def predict_intent(text: str):
    text_vector = vectorizer.transform([text])
    pred_idx = model.predict(text_vector)[0]
    pred_label = label_encoder.inverse_transform([pred_idx])[0]

    probabilities = model.predict_proba(text_vector)[0]
    confidence = max(probabilities)

    return pred_label, float(confidence)