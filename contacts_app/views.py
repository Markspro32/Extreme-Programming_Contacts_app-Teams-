import json
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .models import Contact, ContactMethod


# Helper function to safely parse JSON from request body
def parse_json_body(request):
    try:
        return json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        print(f"❌ JSON parsing failed: {e}")
        return None

@method_decorator(csrf_exempt, name='dispatch')
class ContactListView(View):
    """Handle GET and POST requests for contact list"""

    def get(self, request):
        print("✅ GET Request: Fetching all contacts")
        try:
            contacts = []
            for contact in Contact.objects.prefetch_related('contact_methods'):
                contact_data = {
                    'id': contact.id,
                    'name': contact.name,
                    'bookmarked': contact.bookmarked,
                    'contact_methods': [
                        {
                            'id': method.id,
                            'method_type': method.method_type,
                            'label': method.label,
                            'value': method.value,
                            'is_primary': method.is_primary
                        }
                        for method in contact.contact_methods.all()
                    ]
                }
                contacts.append(contact_data)
            print(f"📊 Returning {len(contacts)} contacts")
            return JsonResponse(contacts, safe=False)
        except Exception as e:
            print(f"❌ GET Failed: {e}")
            return JsonResponse({'error': str(e)}, status=500)

    def post(self, request):
        print("✅ POST Request: Adding new contact")
        print(f"📥 Request Body: {request.body.decode('utf-8')[:200]}...")  # Print first 200 chars

        data = parse_json_body(request)
        if not data:
            error_msg = "Invalid JSON"
            print(f"❌ Error: {error_msg}")
            return JsonResponse({'error': error_msg}, status=400)

        # Validate required fields
        if 'name' not in data or not data['name']:
            error_msg = "Missing required field: name"
            print(f"❌ Error: {error_msg}")
            return JsonResponse({'error': error_msg}, status=400)

        # Validate contact methods
        contact_methods = data.get('contact_methods', [])
        if not contact_methods or len(contact_methods) == 0:
            error_msg = "At least one contact method is required"
            print(f"❌ Error: {error_msg}")
            return JsonResponse({'error': error_msg}, status=400)

        # Validate each contact method has required fields
        for idx, method in enumerate(contact_methods):
            if 'method_type' not in method or not method['method_type']:
                error_msg = f"Contact method {idx + 1}: missing method_type"
                print(f"❌ Error: {error_msg}")
                return JsonResponse({'error': error_msg}, status=400)
            if 'value' not in method or not method['value']:
                error_msg = f"Contact method {idx + 1}: missing value"
                print(f"❌ Error: {error_msg}")
                return JsonResponse({'error': error_msg}, status=400)

        try:
            contact = Contact.objects.create(
                name=data['name']
            )

            # Create contact methods if provided
            contact_methods_data = data.get('contact_methods', [])
            for method_data in contact_methods_data:
                ContactMethod.objects.create(
                    contact=contact,
                    method_type=method_data['method_type'],
                    label=method_data.get('label', ''),
                    value=method_data['value'],
                    is_primary=method_data.get('is_primary', False)
                )

            print(f"✅ Successfully created contact: ID={contact.id}, Name={contact.name}")
            return JsonResponse({
                'id': contact.id,
                'name': contact.name,
                'bookmarked': contact.bookmarked,
                'contact_methods': [
                    {
                        'id': method.id,
                        'method_type': method.method_type,
                        'label': method.label,
                        'value': method.value,
                        'is_primary': method.is_primary
                    }
                    for method in contact.contact_methods.all()
                ]
            }, status=201)
        except Exception as e:
            print(f"❌ Failed to create contact: {e}")
            return JsonResponse({'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class ContactDetailView(View):
    """Handle GET/PUT/DELETE requests for a single contact"""

    def get_contact(self, contact_id):
        try:
            return Contact.objects.get(id=contact_id)
        except Contact.DoesNotExist:
            return None

    def get(self, request, contact_id):
        print(f"✅ GET Request: Fetching contact ID={contact_id}")
        contact = self.get_contact(contact_id)
        if not contact:
            error_msg = f"Contact with ID {contact_id} not found"
            print(f"❌ Error: {error_msg}")
            return JsonResponse({'error': error_msg}, status=404)

        print(f"✅ Returning contact: {contact.name}")
        return JsonResponse({
            'id': contact.id,
            'name': contact.name,
            'bookmarked': contact.bookmarked,
            'contact_methods': [
                {
                    'id': method.id,
                    'method_type': method.method_type,
                    'label': method.label,
                    'value': method.value,
                    'is_primary': method.is_primary
                }
                for method in contact.contact_methods.all()
            ]
        })

    def put(self, request, contact_id):
        print(f"✅ PUT Request: Updating contact ID={contact_id}")
        contact = self.get_contact(contact_id)
        if not contact:
            error_msg = f"Contact with ID {contact_id} not found"
            print(f"❌ Error: {error_msg}")
            return JsonResponse({'error': error_msg}, status=404)

        data = parse_json_body(request)
        if not data:
            error_msg = "Invalid JSON"
            print(f"❌ Error: {error_msg}")
            return JsonResponse({'error': error_msg}, status=400)

        # Update fields
        contact.name = data.get('name', contact.name)
        if 'bookmarked' in data:
            contact.bookmarked = data.get('bookmarked', contact.bookmarked)

        # Handle contact methods update
        if 'contact_methods' in data:
            # Delete existing contact methods and create new ones
            contact.contact_methods.all().delete()
            for method_data in data['contact_methods']:
                ContactMethod.objects.create(
                    contact=contact,
                    method_type=method_data['method_type'],
                    label=method_data.get('label', ''),
                    value=method_data['value'],
                    is_primary=method_data.get('is_primary', False)
                )

        try:
            contact.save()
            print(f"✅ Successfully updated contact: {contact.name}")
            return JsonResponse({
                'id': contact.id,
                'name': contact.name,
                'bookmarked': contact.bookmarked,
                'contact_methods': [
                    {
                        'id': method.id,
                        'method_type': method.method_type,
                        'label': method.label,
                        'value': method.value,
                        'is_primary': method.is_primary
                    }
                    for method in contact.contact_methods.all()
                ]
            })
        except Exception as e:
            print(f"❌ Update failed: {e}")
            return JsonResponse({'error': str(e)}, status=500)

    def delete(self, request, contact_id):
        print(f"✅ DELETE Request: Deleting contact ID={contact_id}")
        contact = self.get_contact(contact_id)
        if not contact:
            error_msg = f"Contact with ID {contact_id} not found"
            print(f"❌ Error: {error_msg}")
            return JsonResponse({'error': error_msg}, status=404)

        try:
            contact.delete()
            print(f"✅ Successfully deleted contact: {contact.name}")
            return JsonResponse({'message': 'Contact deleted successfully'}, status=204)
        except Exception as e:
            print(f"❌ Delete failed: {e}")
            return JsonResponse({'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class ContactBookmarkView(View):
    """Handle POST requests to toggle bookmark status of a contact"""

    def get_contact(self, contact_id):
        try:
            return Contact.objects.get(id=contact_id)
        except Contact.DoesNotExist:
            return None

    def post(self, request, contact_id):
        print(f"✅ POST Request: Toggling bookmark for contact ID={contact_id}")
        contact = self.get_contact(contact_id)
        if not contact:
            error_msg = f"Contact with ID {contact_id} not found"
            print(f"❌ Error: {error_msg}")
            return JsonResponse({'error': error_msg}, status=404)

        # Toggle bookmark status
        contact.bookmarked = not contact.bookmarked
        try:
            contact.save()
            print(f"✅ Successfully {'bookmarked' if contact.bookmarked else 'unbookmarked'} contact: {contact.name}")
            return JsonResponse({
                'id': contact.id,
                'name': contact.name,
                'bookmarked': contact.bookmarked,
                'contact_methods': [
                    {
                        'id': method.id,
                        'method_type': method.method_type,
                        'label': method.label,
                        'value': method.value,
                        'is_primary': method.is_primary
                    }
                    for method in contact.contact_methods.all()
                ]
            })
        except Exception as e:
            print(f"❌ Bookmark toggle failed: {e}")
            return JsonResponse({'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class ContactMethodListView(View):
    """Handle GET and POST requests for contact methods of a specific contact"""

    def get_contact(self, contact_id):
        try:
            return Contact.objects.get(id=contact_id)
        except Contact.DoesNotExist:
            return None

    def get(self, request, contact_id):
        print(f"✅ GET Request: Fetching contact methods for contact ID={contact_id}")
        contact = self.get_contact(contact_id)
        if not contact:
            error_msg = f"Contact with ID {contact_id} not found"
            print(f"❌ Error: {error_msg}")
            return JsonResponse({'error': error_msg}, status=404)

        methods = [
            {
                'id': method.id,
                'method_type': method.method_type,
                'label': method.label,
                'value': method.value,
                'is_primary': method.is_primary
            }
            for method in contact.contact_methods.all()
        ]

        print(f"✅ Returning {len(methods)} contact methods")
        return JsonResponse(methods, safe=False)

    def post(self, request, contact_id):
        print(f"✅ POST Request: Adding contact method to contact ID={contact_id}")
        contact = self.get_contact(contact_id)
        if not contact:
            error_msg = f"Contact with ID {contact_id} not found"
            print(f"❌ Error: {error_msg}")
            return JsonResponse({'error': error_msg}, status=404)

        data = parse_json_body(request)
        if not data:
            error_msg = "Invalid JSON"
            print(f"❌ Error: {error_msg}")
            return JsonResponse({'error': error_msg}, status=400)

        # Validate required fields
        required_fields = ['method_type', 'value']
        for field in required_fields:
            if field not in data:
                error_msg = f"Missing required field: {field}"
                print(f"❌ Error: {error_msg}")
                return JsonResponse({'error': error_msg}, status=400)

        try:
            method = ContactMethod.objects.create(
                contact=contact,
                method_type=data['method_type'],
                label=data.get('label', ''),
                value=data['value'],
                is_primary=data.get('is_primary', False)
            )
            print(f"✅ Successfully created contact method: ID={method.id}")
            return JsonResponse({
                'id': method.id,
                'method_type': method.method_type,
                'label': method.label,
                'value': method.value,
                'is_primary': method.is_primary
            }, status=201)
        except Exception as e:
            print(f"❌ Failed to create contact method: {e}")
            return JsonResponse({'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class ContactMethodDetailView(View):
    """Handle PUT and DELETE requests for a specific contact method"""

    def get_method(self, method_id):
        try:
            return ContactMethod.objects.get(id=method_id)
        except ContactMethod.DoesNotExist:
            return None

    def put(self, request, contact_id, method_id):
        print(f"✅ PUT Request: Updating contact method ID={method_id}")
        method = self.get_method(method_id)
        if not method:
            error_msg = f"Contact method with ID {method_id} not found"
            print(f"❌ Error: {error_msg}")
            return JsonResponse({'error': error_msg}, status=404)

        data = parse_json_body(request)
        if not data:
            error_msg = "Invalid JSON"
            print(f"❌ Error: {error_msg}")
            return JsonResponse({'error': error_msg}, status=400)

        # Update fields
        method.method_type = data.get('method_type', method.method_type)
        method.label = data.get('label', method.label)
        method.value = data.get('value', method.value)
        if 'is_primary' in data:
            method.is_primary = data.get('is_primary', method.is_primary)

        try:
            method.save()
            print(f"✅ Successfully updated contact method: {method.id}")
            return JsonResponse({
                'id': method.id,
                'method_type': method.method_type,
                'label': method.label,
                'value': method.value,
                'is_primary': method.is_primary
            })
        except Exception as e:
            print(f"❌ Update failed: {e}")
            return JsonResponse({'error': str(e)}, status=500)

    def delete(self, request, contact_id, method_id):
        print(f"✅ DELETE Request: Deleting contact method ID={method_id}")
        method = self.get_method(method_id)
        if not method:
            error_msg = f"Contact method with ID {method_id} not found"
            print(f"❌ Error: {error_msg}")
            return JsonResponse({'error': error_msg}, status=404)

        try:
            method.delete()
            print(f"✅ Successfully deleted contact method: {method_id}")
            return JsonResponse({'message': 'Contact method deleted successfully'}, status=204)
        except Exception as e:
            print(f"❌ Delete failed: {e}")
            return JsonResponse({'error': str(e)}, status=500)

