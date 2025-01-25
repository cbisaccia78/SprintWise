from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from src.database import db

from src.schemas.task_schemas import TaskCreate, TaskRead, TaskUpdate
from src.models import Task

task_bp = Blueprint('task_bp', __name__)

@task_bp.route('', methods=['GET'])
def get_tasks():
    tasks = Task.query.all()
    tasks = [TaskRead.model_validate(task).model_dump() for task in tasks]
    return jsonify([task for task in tasks]), 200

@task_bp.route('/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    task = TaskRead.model_validate(task).model_dump()
    return jsonify(task), 200

@task_bp.route('', methods=['POST'])
def create_task():
    try:
        data = request.get_json()
        task = TaskCreate(**data)
    except ValidationError as e:
        return jsonify({'error': e.errors()}), 422
    
    task = Task(title=task.title, description=task.description, project_id=task.project_id)
    db.session.add(task)
    db.session.commit()
    task = TaskRead.model_validate(task).model_dump()
    return jsonify(task), 201

@task_bp.route('/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    try:
        data = request.get_json()
        task_data = TaskUpdate(**data)
    except ValidationError as e:
        return jsonify({'error': e.errors()}), 422
    
    if task_data.title:
        task.title = task_data.title
    if task_data.description:
        task.description = task_data.description
    if task_data.project_id:
        task.project_id = task_data.project_id
    if task_data.status:
        task.status = task_data.status
    if task_data.estimated_time:
        task.estimated_time = task_data.estimated_time
    if task_data.assigned_user:
        task.assigned_user = task_data.assigned_user
    if task_data.priority:
        task.priority = task_data.priority
    
    
    db.session.commit()
    task = TaskRead.model_validate(task).model_dump()
    return jsonify(task), 200

@task_bp.route('/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': 'Task deleted'}), 200