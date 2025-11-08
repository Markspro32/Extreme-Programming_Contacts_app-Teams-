// ====== CONFIGURATION ======
// Backend API address
const API_BASE = 'http://8.138.121.2:8000/contacts/';

// DOM
const contactForm = document.getElementById('add-contact-form');
const contactsList = document.getElementById('contacts-list');
const errorMessage = document.getElementById('error-message');

// ====== PAGE INITIALIZATION ======
document.addEventListener('DOMContentLoaded', () => {
  console.log('✅ Frontend loaded. Fetching contacts from:', API_BASE);
  loadContacts();
  contactForm.addEventListener('submit', handleAddContact);
});

// ====== LOAD CONTACTS ======
async function loadContacts() {
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
  }
}

// ====== RENDER CONTACTS ======
function renderContacts(contacts) {
  contactsList.innerHTML = '';
  
  if (contacts.length === 0) {
    contactsList.innerHTML = '<li>No contacts yet. Add one below!</li>';
    return;
  }

  contacts.forEach(contact => {
    const li = document.createElement('li');
    li.innerHTML = `
      <div>
        <strong>${escapeHtml(contact.name)}</strong><br>
        Email: ${escapeHtml(contact.email)}<br>
        Phone: ${escapeHtml(contact.phone)}
      </div>
      <div>
        <button class="edit-btn" data-id="${contact.id}">Edit</button>
        <button class="delete-btn" data-id="${contact.id}">Delete</button>
      </div>
    `;
    contactsList.appendChild(li);
  });

  // Button
  document.querySelectorAll('.edit-btn').forEach(btn => {
    btn.addEventListener('click', () => showEditForm(btn.dataset.id));
  });
  document.querySelectorAll('.delete-btn').forEach(btn => {
    btn.addEventListener('click', () => deleteContact(btn.dataset.id));
  });
}

// ====== ADD CONTACT ======
async function handleAddContact(e) {
  e.preventDefault();
  
  const name = document.getElementById('name').value;
  const email = document.getElementById('email').value;
  const phone = document.getElementById('phone').value;

  try {
    const response = await fetch(API_BASE, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, phone })
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || `HTTP ${response.status}`);
    }

    // Clear the form and refresh the list after you add a contact
    contactForm.reset();
    loadContacts();
    console.log('✅ Contact added');
  } catch (error) {
    console.error('❌ Failed to add contact:', error);
    showError(`Failed to add contact: ${error.message}`);
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
  const contactEmail = contactElement.querySelectorAll('div')[0].textContent.split('Email: ')[1].split('Phone: ')[0].trim();
  const contactPhone = contactElement.querySelectorAll('div')[0].textContent.split('Phone: ')[1].trim();

  contactElement.innerHTML = `
    <div>
      <input type="text" class="edit-name" value="${escapeHtml(contactName)}" />
      <input type="email" class="edit-email" value="${escapeHtml(contactEmail)}" />
      <input type="text" class="edit-phone" value="${escapeHtml(contactPhone)}" />
    </div>
    <div>
      <button class="save-btn" data-id="${id}">Save</button>
      <button class="cancel-btn">Cancel</button>
    </div>
  `;

  contactElement.querySelector('.save-btn').addEventListener('click', () => saveContact(id));
  contactElement.querySelector('.cancel-btn').addEventListener('click', loadContacts);
}

async function saveContact(id) {
  const name = document.querySelector('.edit-name').value;
  const email = document.querySelector('.edit-email').value;
  const phone = document.querySelector('.edit-phone').value;

  try {
    const response = await fetch(`${API_BASE}${id}/`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, phone })
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
  errorMessage.textContent = message;
  setTimeout(() => {
    errorMessage.textContent = '';
  }, 5000);
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}
