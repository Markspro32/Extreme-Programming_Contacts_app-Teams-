import json
import pandas as pd
from io import BytesIO
from django.http import JsonResponse, HttpResponse
from django.db.utils import OperationalError
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


def maybe_db_not_ready_response(exc: Exception):
    """
    Provide a clearer message when migrations were never applied.
    Common on fresh deploys / new local setups.
    """
    if not isinstance(exc, OperationalError):
        return None
    msg = str(exc)
    if "no such table" in msg or "does not exist" in msg:
        return JsonResponse(
            {
                "error": "Database is not initialized (missing tables). Run migrations on the server/local machine.",
                "how_to_fix": "python manage.py migrate",
                "details": msg,
            },
            status=500,
        )
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
            maybe = maybe_db_not_ready_response(e)
            if maybe:
                return maybe
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
            maybe = maybe_db_not_ready_response(e)
            if maybe:
                return maybe
            return JsonResponse({'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class ContactDetailView(View):
    """Handle GET/PUT/DELETE requests for a single contact"""

    def get_contact(self, contact_id):
        try:
            return Contact.objects.get(id=contact_id)
        except Contact.DoesNotExist:
            return None
        except Exception as e:
            # Let callers surface a better error (e.g. missing tables)
            raise e

    def get(self, request, contact_id):
        print(f"✅ GET Request: Fetching contact ID={contact_id}")
        try:
            contact = self.get_contact(contact_id)
        except Exception as e:
            maybe = maybe_db_not_ready_response(e)
            if maybe:
                return maybe
            return JsonResponse({'error': str(e)}, status=500)
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
        try:
            contact = self.get_contact(contact_id)
        except Exception as e:
            maybe = maybe_db_not_ready_response(e)
            if maybe:
                return maybe
            return JsonResponse({'error': str(e)}, status=500)
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
            maybe = maybe_db_not_ready_response(e)
            if maybe:
                return maybe
            return JsonResponse({'error': str(e)}, status=500)

    def delete(self, request, contact_id):
        print(f"✅ DELETE Request: Deleting contact ID={contact_id}")
        try:
            contact = self.get_contact(contact_id)
        except Exception as e:
            maybe = maybe_db_not_ready_response(e)
            if maybe:
                return maybe
            return JsonResponse({'error': str(e)}, status=500)
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
            maybe = maybe_db_not_ready_response(e)
            if maybe:
                return maybe
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


@method_decorator(csrf_exempt, name='dispatch')
class ContactExportView(View):
    """Handle GET requests to export all contacts to Excel"""

    def get(self, request):
        print("✅ GET Request: Exporting contacts to Excel")
        try:
            # Get all contacts with their methods
            contacts = Contact.objects.prefetch_related('contact_methods').all()
            
            # Prepare data for Excel
            export_data = []
            for contact in contacts:
                # Get all contact methods grouped by type
                methods_by_type = {}
                for method in contact.contact_methods.all():
                    method_type = method.get_method_type_display()
                    if method_type not in methods_by_type:
                        methods_by_type[method_type] = []
                    
                    method_str = method.value
                    if method.label:
                        method_str += f" ({method.label})"
                    if method.is_primary:
                        method_str += " [Primary]"
                    
                    methods_by_type[method_type].append(method_str)
                
                # Create row data
                row = {
                    'Name': contact.name,
                    'Bookmarked': 'Yes' if contact.bookmarked else 'No',
                    'Phone': '; '.join(methods_by_type.get('Phone', [])),
                    'Email': '; '.join(methods_by_type.get('Email', [])),
                    'Social Media': '; '.join(methods_by_type.get('Social Media', [])),
                    'Address': '; '.join(methods_by_type.get('Address', []))
                }
                export_data.append(row)
            
            # Create DataFrame
            df = pd.DataFrame(export_data)
            
            # Create Excel file in memory
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Contacts')
                
                # Auto-adjust column widths
                worksheet = writer.sheets['Contacts']
                from openpyxl.utils import get_column_letter
                for idx, col in enumerate(df.columns):
                    max_length = max(
                        df[col].astype(str).map(len).max(),
                        len(col)
                    )
                    col_letter = get_column_letter(idx + 1)
                    worksheet.column_dimensions[col_letter].width = min(max_length + 2, 50)
            
            output.seek(0)
            
            # Create HTTP response
            response = HttpResponse(
                output.read(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename="contacts_export.xlsx"'
            
            print(f"✅ Successfully exported {len(export_data)} contacts")
            return response
            
        except Exception as e:
            print(f"❌ Export failed: {e}")
            import traceback
            traceback.print_exc()
            return JsonResponse({'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class ContactImportView(View):
    """Handle POST requests to import contacts from Excel"""

    def post(self, request):
        print("✅ POST Request: Importing contacts from Excel")
        
        if 'file' not in request.FILES:
            error_msg = "No file provided"
            print(f"❌ Error: {error_msg}")
            return JsonResponse({'error': error_msg}, status=400)
        
        file = request.FILES['file']
        
        # Check file extension
        if not file.name.endswith(('.xlsx', '.xls')):
            error_msg = "Invalid file type. Please upload an Excel file (.xlsx or .xls)"
            print(f"❌ Error: {error_msg}")
            return JsonResponse({'error': error_msg}, status=400)
        
        try:
            # Read Excel file
            df = pd.read_excel(file, engine='openpyxl')
            
            # Validate required columns
            required_columns = ['Name']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                error_msg = f"Missing required columns: {', '.join(missing_columns)}"
                print(f"❌ Error: {error_msg}")
                return JsonResponse({'error': error_msg}, status=400)
            
            # Process each row
            imported_count = 0
            skipped_count = 0
            errors = []
            
            for index, row in df.iterrows():
                try:
                    name = str(row['Name']).strip()
                    if not name or name == 'nan':
                        skipped_count += 1
                        continue
                    
                    # Check if contact already exists
                    bookmarked = str(row.get('Bookmarked', 'No')).strip().lower() == 'yes'
                    
                    # Create contact
                    contact, created = Contact.objects.get_or_create(
                        name=name,
                        defaults={'bookmarked': bookmarked}
                    )
                    
                    if not created:
                        # Update bookmark status if contact exists
                        contact.bookmarked = bookmarked
                        contact.save()
                        # Clear existing methods for re-import
                        contact.contact_methods.all().delete()
                    
                    # Add contact methods
                    method_mappings = {
                        'Phone': 'phone',
                        'Email': 'email',
                        'Social Media': 'social_media',
                        'Address': 'address'
                    }
                    
                    for excel_col, method_type in method_mappings.items():
                        if excel_col in df.columns:
                            value = str(row.get(excel_col, '')).strip()
                            if value and value != 'nan':
                                # Handle multiple values separated by semicolon
                                values = [v.strip() for v in value.split(';')]
                                for val in values:
                                    if val:
                                        # Parse label and primary status
                                        label = ''
                                        is_primary = False
                                        
                                        if '[' in val and ']' in val:
                                            if '[Primary]' in val:
                                                is_primary = True
                                                val = val.replace('[Primary]', '').strip()
                                        
                                        if '(' in val and ')' in val:
                                            # Extract label
                                            start = val.rfind('(')
                                            end = val.rfind(')')
                                            if start < end:
                                                label = val[start+1:end].strip()
                                                val = val[:start].strip()
                                        
                                        if val:
                                            ContactMethod.objects.create(
                                                contact=contact,
                                                method_type=method_type,
                                                label=label if label else '',
                                                value=val,
                                                is_primary=is_primary
                                            )
                    
                    imported_count += 1
                    
                except Exception as e:
                    error_msg = f"Row {index + 2}: {str(e)}"  # +2 because Excel is 1-indexed and has header
                    errors.append(error_msg)
                    print(f"❌ Error processing row {index + 2}: {e}")
                    skipped_count += 1
            
            result = {
                'message': f'Successfully imported {imported_count} contact(s)',
                'imported': imported_count,
                'skipped': skipped_count
            }
            
            if errors:
                result['errors'] = errors[:10]  # Limit to first 10 errors
            
            print(f"✅ Successfully imported {imported_count} contacts, skipped {skipped_count}")
            return JsonResponse(result, status=200)
            
        except Exception as e:
            print(f"❌ Import failed: {e}")
            import traceback
            traceback.print_exc()
            return JsonResponse({'error': f'Failed to import file: {str(e)}'}, status=500)

