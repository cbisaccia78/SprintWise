from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from src.database import db

from src.schemas.project_schemas import ProjectCreate, ProjectRead, ProjectUpdate
from src.models import Project

project_bp = Blueprint('project_bp', __name__)

@project_bp.route('', methods=['GET'])
def get_projects():
    projects = Project.query.all()
    projects = [ProjectRead.model_validate(project).model_dump() for project in projects]
    return jsonify([[project] for project in projects]), 200

@project_bp.route('/<int:project_id>', methods=['GET'])
def get_project(project_id):
    project = Project.query.get(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    project = ProjectRead.model_validate(project).model_dump()
    return jsonify(project), 200

@project_bp.route('', methods=['POST'])
def create_project():
    try:
        data = request.get_json()
        project = ProjectCreate(**data)
    except ValidationError as e:
        return jsonify({'error': e.errors()}), 422
    
    project = Project(name=project.name, description=project.description)
    db.session.add(project)
    db.session.commit()
    project = ProjectRead.model_validate(project).model_dump()
    return jsonify(project), 201

@project_bp.route('/<int:project_id>', methods=['PUT'])
def update_project(project_id):
    project = Project.query.get(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    try:
        data = request.get_json()
        project_data = ProjectUpdate(**data)
    except ValidationError as e:
        return jsonify({'error': e.errors()}), 422
    
    if project_data.name:
        project.name = project_data.name
    if project_data.description:
        project.description = project_data.description
    
    db.session.commit()
    project = ProjectRead.model_validate(project).model_dump()
    return jsonify(project), 200

@project_bp.route('/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    project = Project.query.get(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    tasks = project.tasks
    for task in tasks:
        db.session.delete(task)
    
    db.session.delete(project)
    db.session.commit()
    return jsonify({'message': 'Project deleted'}), 200