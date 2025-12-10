from flask import Blueprint, request, jsonify
import models

# Create a Blueprint for contact routes
contact_bp = Blueprint('contacts', __name__)

@contact_bp.route('/contacts', methods=['GET'])
def get_contacts():
    """Get all contacts"""
    contacts = models.get_all_contacts()
    return jsonify(contacts)

@contact_bp.route('/contacts/<int:contact_id>', methods=['GET'])
def get_contact(contact_id):
    """Get a single contact by ID"""
    contact = models.get_contact_by_id(contact_id)
    if contact:
        return jsonify(contact)
    return jsonify({'error': 'Contact not found'}), 404

@contact_bp.route('/contacts', methods=['POST'])
def add_contact():
    """Add a new contact"""
    data = request.get_json()
    
    if not data or 'name' not in data or 'phone' not in data:
        return jsonify({'error': 'Name and phone number are required'}), 400
    
    contact_id = models.add_contact(data['name'], data['phone'])
    return jsonify({'id': contact_id, 'message': 'Contact added successfully'}), 201

@contact_bp.route('/contacts/<int:contact_id>', methods=['PUT'])
def update_contact(contact_id):
    """Update an existing contact"""
    data = request.get_json()
    
    if not data or 'name' not in data or 'phone' not in data:
        return jsonify({'error': 'Name and phone number are required'}), 400
    
    # Check if contact exists
    contact = models.get_contact_by_id(contact_id)
    if not contact:
        return jsonify({'error': 'Contact not found'}), 404
    
    models.update_contact(contact_id, data['name'], data['phone'])
    return jsonify({'message': 'Contact updated successfully'})

@contact_bp.route('/contacts/<int:contact_id>', methods=['DELETE'])
def delete_contact(contact_id):
    """Delete a contact"""
    # Check if contact exists
    contact = models.get_contact_by_id(contact_id)
    if not contact:
        return jsonify({'error': 'Contact not found'}), 404
    
    models.delete_contact(contact_id)
    return jsonify({'message': 'Contact deleted successfully'})