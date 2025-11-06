import json
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .models import Contact

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
            contacts = list(Contact.objects.values('id', 'name', 'email', 'phone'))
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
        required_fields = ['name', 'email', 'phone']
        for field in required_fields:
            if field not in data or not data[field]:
                error_msg = f"Missing required field: {field}"
                print(f"❌ Error: {error_msg}")
                return JsonResponse({'error': error_msg}, status=400)

        try:
            contact = Contact.objects.create(
                name=data['name'],
                email=data['email'],
                phone=data['phone']
            )
            print(f"✅ Successfully created contact: ID={contact.id}, Name={contact.name}")
            return JsonResponse({
                'id': contact.id,
                'name': contact.name,
                'email': contact.email,
                'phone': contact.phone
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
            'email': contact.email,
            'phone': contact.phone
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
        contact.email = data.get('email', contact.email)
        contact.phone = data.get('phone', contact.phone)
        try:
            contact.save()
            print(f"✅ Successfully updated contact: {contact.name}")
            return JsonResponse({
                'id': contact.id,
                'name': contact.name,
                'email': contact.email,
                'phone': contact.phone
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