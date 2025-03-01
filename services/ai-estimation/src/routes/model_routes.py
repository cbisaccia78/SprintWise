import json
import requests
import tensorflow as tf
from transformers import AutoTokenizer, TFAutoModel

from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from confluent_kafka import Producer

from src.schemas.model_schemas import TaskEstimateRequest
from src.settings import config

# Here, we use the service name "tf-serving" (as defined in docker-compose)
    # and port 5003 as mapped in your docker-compose.
TF_SERVING_URL = "http://tf-serving:8501/v1/models/codebert_regression_model:predict"

if not config.testing:
    producer = Producer(config.kafka_producer_config)

model_bp = Blueprint('model_bp', __name__)

# Load CodeBERT components once (this can be cached globally)
MODEL_NAME = "microsoft/codebert-base"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
codebert = TFAutoModel.from_pretrained(MODEL_NAME)

def extract_embedding(text):
    """Extracts the [CLS] embedding from a text using CodeBERT."""
    # Tokenize input text
    tokens = tokenizer(
        text,
        padding='max_length',
        truncation=True,
        max_length=512,
        return_tensors="tf"
    )
    # Run CodeBERT to get outputs
    outputs = codebert(
        input_ids=tokens["input_ids"],
        attention_mask=tokens["attention_mask"],
        training=False
    )
    # Return the [CLS] embedding (as list so it's JSON serializable)
    cls_embedding = outputs.last_hidden_state[:, 0, :].numpy().tolist()[0]
    return cls_embedding

@model_bp.route('/task', methods=['POST'])
def estimate_task():
    try:
        data = request.get_json()
        task = TaskEstimateRequest(**data)
    except ValidationError as e:
        print(e.errors())
        return jsonify({'error': e.errors()}), 422

    # Precompute embeddings for input fields
    # (Assuming task has attributes: title, description, and code)
    title_emb = extract_embedding(task.title)
    desc_emb  = extract_embedding(task.description)
    code_emb  = extract_embedding(task.code)

    # Build payload for TensorFlow Serving.
    # Adjust input names according to how your model was exported.
    payload = {
        "instances": [
            {
                "title_input": title_emb,
                "desc_input": desc_emb,
                "code_input": code_emb
            }
        ]
    }
    
    # Call TensorFlow Serving to get prediction.
    
    try:
        resp = requests.post(TF_SERVING_URL, json=payload)
        resp.raise_for_status()
        prediction = resp.json()
    except Exception as e:
        return jsonify({'error': f"TF Serving request failed: {str(e)}"}), 500

    # Build response estimate, including additional info if needed.
    ret = task.model_dump()
    # Parse the prediction output.
    # (Assuming the prediction comes as {"predictions": [[pred_value]]})
    try:
        estimated_time = prediction["predictions"][0][0]
    except (KeyError, IndexError):
        return jsonify({'error': "Unexpected response structure from TF Serving"}), 500

    ret["estimated_time"] = estimated_time
    ret["confidence"] = 0.9  # Optionally add other details

    if not config.testing:
        # Produce an event on Kafka
        producer.produce('estimate-complete', key=str(ret['task_id']), value=json.dumps(ret))
        producer.flush()

    return jsonify(ret), 201