from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from src.schemas.model_schemas import TaskEstimateRequest

model_bp = Blueprint('model_bp', __name__)

@model_bp.route('/task', methods=['POST'])
def estimate_task():
    try:
        data = request.get_json()
        task = TaskEstimateRequest(**data)
    except ValidationError as e:
        print(e.errors())
        return jsonify({'error': e.errors()}), 422
    
    # AI model estimation logic

    # return estimate
    ret = task.model_dump()

    ret["estimated_time"] = 2.4
    ret["confidence"] = 0.9

    return jsonify(ret), 201