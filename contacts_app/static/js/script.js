// ====== CONFIGURATION ======
// Backend API address - use relative URL to work with any host
const API_BASE = '/contacts/';

// DOM
const contactForm = document.getElementById('add-contact-form');
const contactsList = document.getElementById('contacts-list');
const frequentlyAccessedList = document.getElementById('frequently-accessed-list');
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

  // Attach event listeners to all buttons
  attachEventListeners();
}

// ====== CREATE CONTACT ELEMENT ======
function createContactElement(contact) {
  const li = document.createElement('li');
  li.className = contact.bookmarked ? 'bookmarked' : '';
  li.innerHTML = `
    <div>
      <strong>${escapeHtml(contact.name)}</strong>
      ${contact.bookmarked ? '<span class="bookmark-badge">★ Bookmarked</span>' : ''}
      <br>
      Email: ${escapeHtml(contact.email)}<br>
      Phone: ${escapeHtml(contact.phone)}
    </div>
    <div>
      <button class="bookmark-btn ${contact.bookmarked ? 'bookmarked' : ''}" data-id="${contact.id}" title="${contact.bookmarked ? 'Remove bookmark' : 'Add bookmark'}">
        ${contact.bookmarked ? '★' : '☆'}
      </button>
      <button class="edit-btn" data-id="${contact.id}">Edit</button>
      <button class="delete-btn" data-id="${contact.id}">Delete</button>
    </div>
  `;
  return li;
}

// ====== ATTACH EVENT LISTENERS ======
function attachEventListeners() {
  // Bookmark buttons
  document.querySelectorAll('.bookmark-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      toggleBookmark(btn.dataset.id);
    });
  });
  
  // Edit buttons
  document.querySelectorAll('.edit-btn').forEach(btn => {
    btn.addEventListener('click', () => showEditForm(btn.dataset.id));
  });
  
  // Delete buttons
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

// ====== TOGGLE BOOKMARK ======
async function toggleBookmark(id) {
  console.log(`⭐ Toggling bookmark for contact ID: ${id}`);
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
    loadContacts(); // Reload to update both lists
  } catch (error) {
    console.error('❌ Failed to toggle bookmark:', error);
    showError(`Failed to toggle bookmark: ${error.message}`);
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
  const contactElement = document.querySelector(`button[data-id="${id}"].save-btn`).closest('li');
  const name = contactElement.querySelector('.edit-name').value;
  const email = contactElement.querySelector('.edit-email').value;
  const phone = contactElement.querySelector('.edit-phone').value;

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
