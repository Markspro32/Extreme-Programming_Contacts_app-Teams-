// ====== CONFIGURATION ======
// Backend API address - use relative URL to work with any host
const API_BASE = '/contacts/';

// DOM
const contactForm = document.getElementById('add-contact-form');
const contactsList = document.getElementById('contacts-list');
const frequentlyAccessedList = document.getElementById('frequently-accessed-list');
const errorMessage = document.getElementById('error-message');
const addMethodBtn = document.getElementById('add-method-btn');
const contactMethodsContainer = document.getElementById('contact-methods-container');
const exportBtn = document.getElementById('export-btn');
const importFileInput = document.getElementById('import-file');
const successMessage = document.getElementById('success-message');

// Flag to track if event listeners are already attached
let eventListenersAttached = false;

// Flag to prevent multiple simultaneous bookmark requests
let bookmarkRequestInProgress = false;

// ====== PAGE INITIALIZATION ======
document.addEventListener('DOMContentLoaded', () => {
  console.log('✅ Frontend loaded. Fetching contacts from:', API_BASE);
  
  // Attach event listeners ONCE using event delegation
  setupEventDelegation();
  
  loadContacts();
  contactForm.addEventListener('submit', handleAddContact);
  addMethodBtn.addEventListener('click', addContactMethodField);
  
  // Import/Export functionality
  if (exportBtn) {
    exportBtn.addEventListener('click', handleExport);
  }
  if (importFileInput) {
    importFileInput.addEventListener('change', handleImport);
  }

  // Initialize remove buttons for existing method items
  setupRemoveMethodButtons();
});

// Flag to prevent multiple simultaneous load requests
let loadContactsInProgress = false;

// ====== LOAD CONTACTS ======
async function loadContacts() {
  // Prevent multiple simultaneous load requests
  if (loadContactsInProgress) {
    console.log('⚠️ Load contacts already in progress, ignoring...');
    return;
  }

  loadContactsInProgress = true;

  try {
    console.log('✅ Starting to load contacts...');
    const response = await fetch(API_BASE);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const contacts = await response.json();
    console.log('📊 Loaded contacts:', contacts);
    renderContacts(contacts);
  } catch (error) {
    console.error('❌ Failed to load contacts:', error);
    showError(`Failed to load contacts: ${error.message}`);
  } finally {
    loadContactsInProgress = false;
  }
}

// ====== RENDER CONTACTS ======
function renderContacts(contacts) {
  // Clear both lists
  contactsList.innerHTML = '';
  frequentlyAccessedList.innerHTML = '';
  
  if (contacts.length === 0) {
    contactsList.innerHTML = '<li>No contacts yet. Add one below!</li>';
    return;
  }

  // Separate bookmarked and non-bookmarked contacts
  const bookmarkedContacts = contacts.filter(c => c.bookmarked).sort((a, b) => a.name.localeCompare(b.name));
  const otherContacts = contacts.filter(c => !c.bookmarked).sort((a, b) => a.name.localeCompare(b.name));

  // Render frequently accessed (bookmarked) contacts
  if (bookmarkedContacts.length === 0) {
    frequentlyAccessedList.innerHTML = '<li class="empty-message">No bookmarked contacts yet. Click the star icon to bookmark a contact!</li>';
  } else {
    bookmarkedContacts.forEach(contact => {
      const li = createContactElement(contact);
      frequentlyAccessedList.appendChild(li);
    });
  }

  // Render all other contacts
  if (otherContacts.length === 0) {
    contactsList.innerHTML = '<li class="empty-message">All contacts are bookmarked!</li>';
  } else {
    otherContacts.forEach(contact => {
      const li = createContactElement(contact);
      contactsList.appendChild(li);
    });
  }

  // Event listeners are already attached via delegation, no need to re-attach
}

// ====== CREATE CONTACT ELEMENT ======
function createContactElement(contact) {
  const li = document.createElement('li');
  li.className = contact.bookmarked ? 'bookmarked' : '';

  // Generate contact methods HTML
  let methodsHtml = '';
  if (contact.contact_methods && contact.contact_methods.length > 0) {
    const methodTypeLabels = {
      'phone': 'Phone',
      'email': 'Email',
      'social_media': 'Social Media',
      'address': 'Address'
    };
    
    methodsHtml = contact.contact_methods.map(method => {
      const methodTypeLabel = methodTypeLabels[method.method_type] || method.method_type;
      const labelPart = method.label ? ` <span class="method-label-text">(${escapeHtml(method.label)})</span>` : '';
      const primaryPart = method.is_primary ? ' <span class="primary-badge">Primary</span>' : '';
      return `<div class="contact-method ${method.method_type}"><strong>${methodTypeLabel}:</strong> ${escapeHtml(method.value)}${labelPart}${primaryPart}</div>`;
    }).join('');
  } else {
    methodsHtml = '<div class="no-methods">No contact methods</div>';
  }

  li.innerHTML = `
    <div class="contact-info">
      <strong>${escapeHtml(contact.name)}</strong>
      ${contact.bookmarked ? '<span class="bookmark-badge">★ Bookmarked</span>' : ''}
      <div class="contact-methods">
        ${methodsHtml}
      </div>
    </div>
    <div class="contact-actions">
      <button type="button" class="bookmark-btn ${contact.bookmarked ? 'bookmarked' : ''}" data-id="${contact.id}" title="${contact.bookmarked ? 'Remove bookmark' : 'Add bookmark'}">
        ${contact.bookmarked ? '★' : '☆'}
      </button>
      <button type="button" class="edit-btn" data-id="${contact.id}">Edit</button>
      <button type="button" class="delete-btn" data-id="${contact.id}">Delete</button>
    </div>
  `;
  return li;
}

// ====== SETUP EVENT DELEGATION ======
// This function is called ONCE on page load to set up event delegation
function setupEventDelegation() {
  if (eventListenersAttached) {
    console.warn('⚠️ Event listeners already attached, skipping...');
    return;
  }

  const allLists = [contactsList, frequentlyAccessedList];
  
  allLists.forEach(list => {
    if (!list) return;
    
    // Single event listener for all button clicks - attached ONCE
    list.addEventListener('click', (e) => {
      // Only prevent default if we're clicking a button
      const clickedButton = e.target.closest('button');
      if (!clickedButton) return;
      
      // Find the button that was clicked
      const bookmarkBtn = e.target.closest('.bookmark-btn');
      const editBtn = e.target.closest('.edit-btn');
      const deleteBtn = e.target.closest('.delete-btn');
      
      if (bookmarkBtn) {
        e.preventDefault();
        e.stopPropagation();
        const contactId = bookmarkBtn.getAttribute('data-id');
        console.log('🔖 Bookmark button clicked for contact ID:', contactId);
        if (contactId) {
          toggleBookmark(contactId);
        } else {
          console.error('❌ No contact ID found on bookmark button');
        }
        return;
      }
      
      if (editBtn) {
        e.preventDefault();
        e.stopPropagation();
        const contactId = editBtn.getAttribute('data-id');
        if (contactId) {
          showEditForm(contactId);
        }
        return;
      }
      
      if (deleteBtn) {
        e.preventDefault();
        e.stopPropagation();
        const contactId = deleteBtn.getAttribute('data-id');
        if (contactId) {
          deleteContact(contactId);
        }
        return;
      }
    });
  });
  
  eventListenersAttached = true;
  console.log('✅ Event delegation set up');
}

// ====== CONTACT METHOD FORM MANAGEMENT ======
function addContactMethodField() {
  const template = document.querySelector('.contact-method-item.first-item');
  const newItem = template.cloneNode(true);

  // Remove first-item class and add remove button
  newItem.classList.remove('first-item');
  
  // Add remove button if it doesn't exist
  if (!newItem.querySelector('.remove-method-btn')) {
    const removeBtn = document.createElement('button');
    removeBtn.type = 'button';
    removeBtn.className = 'remove-method-btn';
    removeBtn.title = 'Remove this contact method';
    removeBtn.textContent = '×';
    newItem.appendChild(removeBtn);
  }

  // Clear values in the new item
  newItem.querySelector('.method-type').value = '';
  newItem.querySelector('.method-label').value = '';
  newItem.querySelector('.method-value').value = '';
  newItem.querySelector('.method-primary').checked = false;

  contactMethodsContainer.appendChild(newItem);
  // No need to setup listeners - event delegation handles it
}

function removeContactMethodField(button) {
  const item = button.closest('.contact-method-item');
  const allItems = document.querySelectorAll('.contact-method-item');

  if (allItems.length > 1) {
    item.remove();
  } else {
    // If it's the last item, just clear it
    item.querySelector('.method-type').value = '';
    item.querySelector('.method-label').value = '';
    item.querySelector('.method-value').value = '';
    item.querySelector('.method-primary').checked = false;
  }
}

function setupRemoveMethodButtons() {
  // Use event delegation on the container for better reliability
  if (!contactMethodsContainer) return;
  
  // Remove any existing listener by cloning (if needed)
  // Actually, we'll use a flag to prevent duplicate listeners
  if (contactMethodsContainer.dataset.listenersAttached === 'true') {
    return;
  }
  
  contactMethodsContainer.addEventListener('click', (e) => {
    const removeBtn = e.target.closest('.remove-method-btn');
    if (removeBtn) {
      e.preventDefault();
      e.stopPropagation();
      removeContactMethodField(removeBtn);
    }
  });
  
  contactMethodsContainer.dataset.listenersAttached = 'true';
}

// ====== ADD CONTACT ======
async function handleAddContact(e) {
  e.preventDefault();

  const name = document.getElementById('name').value.trim();

  // Collect contact methods
  const contactMethods = [];
  const methodItems = document.querySelectorAll('.contact-method-item');

  methodItems.forEach(item => {
    const methodType = item.querySelector('.method-type').value;
    const label = item.querySelector('.method-label').value.trim();
    const value = item.querySelector('.method-value').value.trim();
    const isPrimary = item.querySelector('.method-primary').checked;

    if (methodType && value) {
      contactMethods.push({
        method_type: methodType,
        label: label,
        value: value,
        is_primary: isPrimary
      });
    }
  });

  if (contactMethods.length === 0) {
    showError('Please add at least one contact method');
    return;
  }

  try {
    const response = await fetch(API_BASE, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, contact_methods: contactMethods })
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || `HTTP ${response.status}`);
    }

    // Clear the form and refresh the list after you add a contact
    contactForm.reset();
    // Reset contact methods to one empty item
    resetContactMethodsForm();
    loadContacts();
    console.log('✅ Contact added');
  } catch (error) {
    console.error('❌ Failed to add contact:', error);
    showError(`Failed to add contact: ${error.message}`);
  }
}

// ====== RESET CONTACT METHODS FORM ======
function resetContactMethodsForm() {
  const container = document.getElementById('contact-methods-container');
  const methodItems = container.querySelectorAll('.contact-method-item');
  methodItems.forEach((item, index) => {
    if (index > 0) {
      item.remove();
    } else {
      // Reset the first item
      item.querySelector('.method-type').value = '';
      item.querySelector('.method-label').value = '';
      item.querySelector('.method-value').value = '';
      item.querySelector('.method-primary').checked = false;
    }
  });
}

// ====== TOGGLE BOOKMARK ======
async function toggleBookmark(id) {
  // Prevent multiple simultaneous requests
  if (bookmarkRequestInProgress) {
    console.log('⚠️ Bookmark request already in progress, ignoring...');
    return;
  }

  console.log(`⭐ Toggling bookmark for contact ID: ${id}`);
  bookmarkRequestInProgress = true;

  try {
    const response = await fetch(`${API_BASE}${id}/bookmark/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      }
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || `HTTP ${response.status}`);
    }

    const result = await response.json();
    console.log('✅ Bookmark toggled successfully:', result);
    
    // Small delay before reloading to prevent rapid-fire requests
    await new Promise(resolve => setTimeout(resolve, 100));
    
    await loadContacts(); // Reload to update both lists
  } catch (error) {
    console.error('❌ Failed to toggle bookmark:', error);
    showError(`Failed to toggle bookmark: ${error.message}`);
  } finally {
    bookmarkRequestInProgress = false;
  }
}

// ====== DELETE CONTACT ======
async function deleteContact(id) {
    console.log(`🗑️ Delete button clicked for ID: ${id}`);
  if (!confirm('Are you sure you want to delete this contact?')) return;

  try {
    const response = await fetch(`${API_BASE}${id}/`, {
      method: 'DELETE'
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    loadContacts();
    console.log('✅ Contact deleted');
  } catch (error) {
    console.error('❌ Failed to delete contact:', error);
    showError(`Failed to delete contact: ${error.message}`);
  }
}

// ====== EDIT CONTACT ======
function showEditForm(id) {
  const contactElement = document.querySelector(`button[data-id="${id}"]`).closest('li');
  const contactName = contactElement.querySelector('strong').textContent;

  // Find contact data from current contacts
  let contactData = null;
  const allContacts = [...document.querySelectorAll('#contacts-list li'), ...document.querySelectorAll('#frequently-accessed-list li')];
  for (const li of allContacts) {
    const btn = li.querySelector(`button[data-id="${id}"]`);
    if (btn) {
      // We need to get the contact data from our current state - this is a bit hacky
      // In a real app, we'd store the contact data or refetch it
      break;
    }
  }

  // For now, let's refetch the contact data
  fetchContactData(id).then(contact => {
    if (contact) {
      renderEditForm(contactElement, contact);
    }
  });
}

async function fetchContactData(contactId) {
  try {
    const response = await fetch(`${API_BASE}${contactId}/`);
    if (response.ok) {
      return await response.json();
    }
  } catch (error) {
    console.error('Failed to fetch contact data:', error);
  }
  return null;
}

function renderEditForm(contactElement, contact) {
  let methodsHtml = '';
  if (contact.contact_methods && contact.contact_methods.length > 0) {
    methodsHtml = contact.contact_methods.map((method, index) => {
      const isFirst = index === 0;
      const removeButton = isFirst ? '' : `<button type="button" class="remove-edit-method-btn" data-index="${index}">Remove</button>`;
      const firstClass = isFirst ? 'first-item' : '';
      return `<div class="edit-method-item ${firstClass}">
        <select class="edit-method-type" data-index="${index}">
          <option value="phone" ${method.method_type === 'phone' ? 'selected' : ''}>Phone</option>
          <option value="email" ${method.method_type === 'email' ? 'selected' : ''}>Email</option>
          <option value="social_media" ${method.method_type === 'social_media' ? 'selected' : ''}>Social Media</option>
          <option value="address" ${method.method_type === 'address' ? 'selected' : ''}>Address</option>
        </select>
        <input type="text" class="edit-method-label" data-index="${index}" value="${escapeHtml(method.label)}" placeholder="Label" />
        <input type="text" class="edit-method-value" data-index="${index}" value="${escapeHtml(method.value)}" placeholder="Value" />
        <label><input type="checkbox" class="edit-method-primary" data-index="${index}" ${method.is_primary ? 'checked' : ''} /> Primary</label>
        ${removeButton}
      </div>`;
    }).join('');
  }

  contactElement.innerHTML = `
    <div class="edit-form">
      <input type="text" class="edit-name" value="${escapeHtml(contact.name)}" placeholder="Name" />
      <div class="edit-methods-container">
        ${methodsHtml}
      </div>
      <button type="button" class="add-edit-method-btn">Add Contact Method</button>
    </div>
    <div class="edit-actions">
      <button class="save-btn" data-id="${contact.id}">Save</button>
      <button class="cancel-btn">Cancel</button>
    </div>
  `;

  // Add event listeners
  contactElement.querySelector('.save-btn').addEventListener('click', () => saveContact(contact.id));
  contactElement.querySelector('.cancel-btn').addEventListener('click', loadContacts);
  contactElement.querySelector('.add-edit-method-btn').addEventListener('click', () => addEditMethodField(contactElement));
  setupEditRemoveButtons(contactElement);
}

function addEditMethodField(contactElement) {
  const container = contactElement.querySelector('.edit-methods-container');
  const index = container.querySelectorAll('.edit-method-item').length;

  const newMethod = document.createElement('div');
  newMethod.className = 'edit-method-item';
  newMethod.innerHTML = `
    <select class="edit-method-type" data-index="${index}">
      <option value="phone">Phone</option>
      <option value="email">Email</option>
      <option value="social_media">Social Media</option>
      <option value="address">Address</option>
    </select>
    <input type="text" class="edit-method-label" data-index="${index}" placeholder="Label" />
    <input type="text" class="edit-method-value" data-index="${index}" placeholder="Value" />
    <label><input type="checkbox" class="edit-method-primary" data-index="${index}" /> Primary</label>
    <button type="button" class="remove-edit-method-btn" data-index="${index}">Remove</button>
  `;

  container.appendChild(newMethod);
  setupEditRemoveButtons(contactElement);
}

function setupEditRemoveButtons(contactElement) {
  contactElement.querySelectorAll('.remove-edit-method-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const item = btn.closest('.edit-method-item');
      const container = contactElement.querySelector('.edit-methods-container');
      if (container.querySelectorAll('.edit-method-item').length > 1) {
        item.remove();
      } else {
        // Clear the last item
        item.querySelector('.edit-method-type').value = 'phone';
        item.querySelector('.edit-method-label').value = '';
        item.querySelector('.edit-method-value').value = '';
        item.querySelector('.edit-method-primary').checked = false;
      }
    });
  });
}

async function saveContact(id) {
  const contactElement = document.querySelector(`button[data-id="${id}"].save-btn`).closest('li');
  const name = contactElement.querySelector('.edit-name').value.trim();

  // Collect contact methods
  const contactMethods = [];
  const methodItems = contactElement.querySelectorAll('.edit-method-item');

  methodItems.forEach(item => {
    const methodType = item.querySelector('.edit-method-type').value;
    const label = item.querySelector('.edit-method-label').value.trim();
    const value = item.querySelector('.edit-method-value').value.trim();
    const isPrimary = item.querySelector('.edit-method-primary').checked;

    if (methodType && value) {
      contactMethods.push({
        method_type: methodType,
        label: label,
        value: value,
        is_primary: isPrimary
      });
    }
  });

  if (contactMethods.length === 0) {
    showError('Please add at least one contact method');
    return;
  }

  try {
    const response = await fetch(`${API_BASE}${id}/`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, contact_methods: contactMethods })
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    loadContacts();
    console.log('✅ Contact updated');
  } catch (error) {
    console.error('❌ Failed to update contact:', error);
    showError(`Failed to update contact: ${error.message}`);
  }
}

// ====== HELPER FUNCTIONS ======
function showError(message) {
  if (errorMessage) {
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
    setTimeout(() => {
      errorMessage.textContent = '';
      errorMessage.style.display = 'none';
    }, 5000);
  } else {
    console.error('Error:', message);
    alert(message); // Fallback if error element doesn't exist
  }
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// ====== EXPORT CONTACTS ======
async function handleExport() {
  console.log('📥 Exporting contacts to Excel...');
  
  try {
    const response = await fetch(`${API_BASE}export/`, {
      method: 'GET'
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || `HTTP ${response.status}`);
    }

    // Get the blob from response
    const blob = await response.blob();
    
    // Create download link
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'contacts_export.xlsx';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);

    showSuccess('Contacts exported successfully!');
    console.log('✅ Contacts exported successfully');
  } catch (error) {
    console.error('❌ Failed to export contacts:', error);
    showError(`Failed to export contacts: ${error.message}`);
  }
}

// ====== IMPORT CONTACTS ======
async function handleImport(event) {
  const file = event.target.files[0];
  
  if (!file) {
    return;
  }

  console.log('📤 Importing contacts from Excel...', file.name);

  // Validate file type
  if (!file.name.endsWith('.xlsx') && !file.name.endsWith('.xls')) {
    showError('Invalid file type. Please upload an Excel file (.xlsx or .xls)');
    importFileInput.value = ''; // Reset file input
    return;
  }

  // Create FormData
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await fetch(`${API_BASE}import/`, {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || `HTTP ${response.status}`);
    }

    const result = await response.json();
    console.log('✅ Import result:', result);

    // Reset file input
    importFileInput.value = '';

    // Show success message
    let message = result.message || `Successfully imported ${result.imported || 0} contact(s)`;
    if (result.skipped > 0) {
      message += ` (${result.skipped} skipped)`;
    }
    showSuccess(message);

    // Show errors if any
    if (result.errors && result.errors.length > 0) {
      console.warn('⚠️ Import errors:', result.errors);
      const errorList = result.errors.slice(0, 5).join(', ');
      showError(`Some rows had errors: ${errorList}${result.errors.length > 5 ? '...' : ''}`);
    }

    // Reload contacts
    await loadContacts();
  } catch (error) {
    console.error('❌ Failed to import contacts:', error);
    showError(`Failed to import contacts: ${error.message}`);
    importFileInput.value = ''; // Reset file input
  }
}

// ====== SHOW SUCCESS MESSAGE ======
function showSuccess(message) {
  if (successMessage) {
    successMessage.textContent = message;
    successMessage.style.display = 'block';
    setTimeout(() => {
      successMessage.textContent = '';
      successMessage.style.display = 'none';
    }, 5000);
  } else {
    console.log('Success:', message);
  }
}
