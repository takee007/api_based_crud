/**
 * Student CV Hub - REST API CRUD Client
 * System 1 (Frontend) <--> System 2 (Django REST Backend) <--> PostgreSQL / SQLite Database
 */

const API_BASE = '/api/cvs/';
const AUTH_BASE = '/api/auth/';

// Application State
let allCVs = [];
let currentUser = null; // Currently logged in student object
let authToken = localStorage.getItem('auth_token') || '';
let activeCVId = localStorage.getItem('active_cv_id') ? parseInt(localStorage.getItem('active_cv_id')) : 102;
let activeCVPin = localStorage.getItem('active_cv_pin') || '2230907';

// DOM Elements
const profileViewSection = document.getElementById('profileViewSection');
const directoryViewSection = document.getElementById('directoryViewSection');
const apiDocsSection = document.getElementById('apiDocsSection');
const tabProfile = document.getElementById('tabProfile');
const tabDirectory = document.getElementById('tabDirectory');
const tabApi = document.getElementById('tabApi');
const directoryGrid = document.getElementById('directoryGrid');
const searchInput = document.getElementById('searchInput');

// Navbar Auth Elements
const navUserBadge = document.getElementById('navUserBadge');
const navGuestBadge = document.getElementById('navGuestBadge');
const navUserName = document.getElementById('navUserName');
const navUserId = document.getElementById('navUserId');
const navUserAvatar = document.getElementById('navUserAvatar');

// Modals
const cvFormModal = document.getElementById('cvFormModal');
const cvModalTitle = document.getElementById('cvModalTitle');
const cvForm = document.getElementById('cvForm');
const viewDetailsModal = document.getElementById('viewDetailsModal');
const viewDetailsContent = document.getElementById('viewDetailsContent');

// Initialize on Load
document.addEventListener('DOMContentLoaded', async () => {
  setupEventListeners();
  await checkAuthSession();
  await loadAllCVs();
});

function setupEventListeners() {
  // Navigation Tabs
  tabProfile.addEventListener('click', () => switchTab('profile'));
  tabDirectory.addEventListener('click', () => switchTab('directory'));
  tabApi.addEventListener('click', () => switchTab('api'));

  // Search
  searchInput.addEventListener('input', (e) => {
    filterDirectory(e.target.value);
  });

  // CV Form Submit (Create or Update)
  cvForm.addEventListener('submit', handleFormSubmit);

  // Close modals when clicking backdrop
  document.querySelectorAll('.modal-overlay').forEach(modal => {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) closeModal(modal.id);
    });
  });
}

// Check Active Authentication Session
async function checkAuthSession() {
  if (!authToken) {
    updateNavAuthState(null);
    return;
  }

  try {
    const res = await fetch(`${AUTH_BASE}me/`, {
      headers: {
        'Authorization': `Bearer ${authToken}`
      }
    });

    if (res.ok) {
      const data = await res.json();
      if (data.success && data.cv) {
        currentUser = data.cv;
        activeCVId = currentUser.id;
        localStorage.setItem('active_cv_id', activeCVId);
        updateNavAuthState(currentUser);
        return;
      }
    }
  } catch (err) {
    console.warn("Session check error:", err);
  }

  // If token is invalid or expired
  currentUser = null;
  authToken = '';
  localStorage.removeItem('auth_token');
  updateNavAuthState(null);
}

function updateNavAuthState(user) {
  if (user) {
    navUserBadge.style.display = 'flex';
    navGuestBadge.style.display = 'none';
    navUserName.innerText = user.name;
    navUserId.innerText = `(${user.student_id})`;
    navUserAvatar.src = user.avatar_url || 'https://api.dicebear.com/7.x/avataaars/svg?seed=' + user.id;
  } else {
    navUserBadge.style.display = 'none';
    navGuestBadge.style.display = 'flex';
  }
}

// Logout Handler
async function handleLogout() {
  if (authToken) {
    try {
      await fetch(`${AUTH_BASE}logout/`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${authToken}` }
      });
    } catch (_) {}
  }

  localStorage.removeItem('auth_token');
  localStorage.removeItem('active_cv_id');
  localStorage.removeItem('active_cv_pin');
  localStorage.removeItem('active_student_name');
  currentUser = null;
  authToken = '';
  
  showToast('Logged out successfully.', 'info');
  setTimeout(() => {
    window.location.href = '/login/';
  }, 600);
}

// Switch between Profile, Directory, and API Guide
function switchTab(tab) {
  tabProfile.classList.toggle('active', tab === 'profile');
  tabDirectory.classList.toggle('active', tab === 'directory');
  tabApi.classList.toggle('active', tab === 'api');

  profileViewSection.style.display = tab === 'profile' ? 'block' : 'none';
  directoryViewSection.style.display = tab === 'directory' ? 'block' : 'none';
  apiDocsSection.style.display = tab === 'api' ? 'block' : 'none';

  if (tab === 'directory') {
    loadAllCVs();
  }
}

// ==========================================
// API Operations (CRUD)
// ==========================================

// 1. READ: Fetch all CVs (GET /api/cvs/)
async function loadAllCVs() {
  try {
    const res = await fetch(API_BASE);
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    allCVs = await res.json();

    // Render directory
    renderDirectory(allCVs);

    // If logged in, show currentUser's profile
    if (currentUser) {
      const refreshedCurrent = allCVs.find(c => c.id === currentUser.id);
      if (refreshedCurrent) {
        currentUser = refreshedCurrent;
        renderMyProfile(currentUser);
        return;
      }
    }

    // If guest or activeCVId set
    let current = allCVs.find(c => c.id === activeCVId);
    if (!current && allCVs.length > 0) {
      current = allCVs[0];
      activeCVId = current.id;
    }

    if (current) {
      renderMyProfile(current);
    } else {
      renderEmptyProfile();
    }
  } catch (err) {
    showToast(`Failed to load CVs: ${err.message}`, 'error');
  }
}

// 2. READ: Fetch Single CV (GET /api/cvs/<id>/)
async function fetchSingleCV(id) {
  try {
    const res = await fetch(`${API_BASE}${id}/`);
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return await res.json();
  } catch (err) {
    showToast(`Failed to load CV #${id}: ${err.message}`, 'error');
    return null;
  }
}

// 3. CREATE or UPDATE: Handle Form Submit (POST /api/cvs/ or PUT /api/cvs/<id>/)
async function handleFormSubmit(e) {
  e.preventDefault();
  const formId = document.getElementById('formCvId').value;
  const isEditing = Boolean(formId);

  const rawSkills = document.getElementById('formSkills').value;
  const skillsArray = rawSkills.split(',').map(s => s.trim()).filter(Boolean);

  const payload = {
    name: document.getElementById('formName').value.trim(),
    student_id: document.getElementById('formStudentId').value.trim(),
    email: document.getElementById('formEmail').value.trim(),
    phone: document.getElementById('formPhone').value.trim(),
    education: document.getElementById('formEducation').value.trim(),
    skills: skillsArray,
    experience: document.getElementById('formExperience').value.trim(),
    bio: document.getElementById('formBio').value.trim(),
    avatar_url: document.getElementById('formAvatarUrl').value.trim() || 'https://api.dicebear.com/7.x/avataaars/svg?seed=' + encodeURIComponent(document.getElementById('formName').value.trim()),
    passcode: document.getElementById('formPasscode').value.trim()
  };

  const submitBtn = cvForm.querySelector('button[type="submit"]');
  submitBtn.disabled = true;
  submitBtn.innerText = 'Saving to Database...';

  try {
    const headers = {
      'Content-Type': 'application/json'
    };
    if (authToken) {
      headers['Authorization'] = `Bearer ${authToken}`;
    }
    if (payload.passcode) {
      headers['X-CV-PIN'] = payload.passcode;
    }

    let res;
    if (isEditing) {
      // PUT /api/cvs/<id>/
      res = await fetch(`${API_BASE}${formId}/`, {
        method: 'PUT',
        headers: headers,
        body: JSON.stringify(payload)
      });
    } else {
      // POST /api/cvs/
      res = await fetch(API_BASE, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify(payload)
      });
    }

    const data = await res.json();

    if (!res.ok) {
      if (res.status === 403) {
        throw new Error(data.detail || "Permission Denied: You cannot modify this CV. Only the owner can update it!");
      }
      const errorMsg = data.detail || Object.values(data).flat().join(' ') || `Error ${res.status}`;
      throw new Error(errorMsg);
    }

    showToast(isEditing ? 'CV updated successfully!' : 'New CV created and saved to database!', 'success');
    closeModal('cvFormModal');

    // Update active state
    activeCVId = data.id;
    if (currentUser && currentUser.id === data.id) {
      currentUser = data;
      updateNavAuthState(currentUser);
    }

    await loadAllCVs();
    switchTab('profile');
  } catch (err) {
    showToast(err.message, 'error');
  } finally {
    submitBtn.disabled = false;
    submitBtn.innerText = 'Save CV';
  }
}

// 4. DELETE: Delete CV (DELETE /api/cvs/<id>/)
async function deleteCV(id, name) {
  const isOwner = currentUser && currentUser.id === id;
  let pin = '';

  if (!isOwner) {
    pin = prompt(`To delete ${name}'s CV (#${id}), enter the owner password/PIN:`, activeCVPin || '');
    if (pin === null) return; // User cancelled
  }

  if (!confirm(`Are you sure you want to permanently delete CV #${id} (${name})?`)) {
    return;
  }

  try {
    const headers = {};
    if (authToken) headers['Authorization'] = `Bearer ${authToken}`;
    if (pin) headers['X-CV-PIN'] = pin;

    const res = await fetch(`${API_BASE}${id}/`, {
      method: 'DELETE',
      headers: headers
    });

    const data = await res.json().catch(() => ({}));

    if (!res.ok) {
      if (res.status === 403) {
        throw new Error(data.detail || "Permission Denied: Invalid credentials! Only the owner can delete their CV.");
      }
      throw new Error(data.detail || `HTTP Error ${res.status}`);
    }

    showToast(`CV #${id} (${name}) was deleted from the database.`, 'success');
    closeModal('viewDetailsModal');

    // If current user was deleted, log out
    if (currentUser && currentUser.id === id) {
      handleLogout();
      return;
    }

    await loadAllCVs();
    switchTab('directory');
  } catch (err) {
    showToast(err.message, 'error');
  }
}

// ==========================================
// Rendering Functions
// ==========================================

// Render My Profile View
function renderMyProfile(cv) {
  const isOwner = currentUser && currentUser.id === cv.id;

  document.getElementById('myAvatar').src = cv.avatar_url || 'https://api.dicebear.com/7.x/avataaars/svg?seed=user';
  document.getElementById('myName').innerText = cv.name;
  document.getElementById('myStudentIdBadge').innerText = `ID: ${cv.student_id}`;
  document.getElementById('mySubtext').innerText = `${cv.education} • Record #${cv.id}`;

  document.getElementById('myEmail').innerText = cv.email || 'Not specified';
  document.getElementById('myPhone').innerText = cv.phone || 'Not specified';
  document.getElementById('myEducation').innerText = cv.education || 'Not specified';
  document.getElementById('myExperience').innerText = cv.experience || 'Not specified';
  document.getElementById('myBio').innerText = cv.bio ? `"${cv.bio}"` : '"No bio provided yet."';

  // Skills
  const skillsContainer = document.getElementById('mySkills');
  skillsContainer.innerHTML = '';
  if (Array.isArray(cv.skills) && cv.skills.length > 0) {
    cv.skills.forEach(skill => {
      const tag = document.createElement('span');
      tag.className = 'skill-tag';
      tag.innerText = skill;
      skillsContainer.appendChild(tag);
    });
  } else {
    skillsContainer.innerHTML = '<span style="color:#94a3b8; font-size:0.85rem;">No skills added</span>';
  }

  // Setup Edit and Delete buttons for My Profile
  const editBtn = document.getElementById('btnEditMyCV');
  const deleteBtn = document.getElementById('btnDeleteMyCV');

  if (isOwner) {
    editBtn.style.display = 'inline-flex';
    deleteBtn.style.display = 'inline-flex';
    editBtn.onclick = () => openEditModal(cv);
    deleteBtn.onclick = () => deleteCV(cv.id, cv.name);
  } else {
    // Strict restriction: no one can edit or delete another student's CV
    editBtn.style.display = 'none';
    deleteBtn.style.display = 'none';
  }
}

function renderEmptyProfile() {
  document.getElementById('myName').innerText = 'No CV Selected';
  document.getElementById('mySubtext').innerText = 'Please sign in or select a CV from the Directory.';
  document.getElementById('myBio').innerText = 'Log in to view and edit your own CV.';
  document.getElementById('mySkills').innerHTML = '';
  document.getElementById('btnEditMyCV').style.display = 'none';
  document.getElementById('btnDeleteMyCV').style.display = 'none';
}

// Render Directory Grid (Classmate CVs)
function renderDirectory(cvList) {
  directoryGrid.innerHTML = '';
  document.getElementById('directoryCount').innerText = `${cvList.length} Student${cvList.length === 1 ? '' : 's'}`;

  if (cvList.length === 0) {
    directoryGrid.innerHTML = `
      <div class="empty-state" style="grid-column: 1 / -1;">
        <div style="font-size:2.5rem; margin-bottom:0.5rem;">🔍</div>
        <h3>No student CVs found</h3>
        <p>Try searching for a different keyword or create the first CV!</p>
      </div>
    `;
    return;
  }

  cvList.forEach(cv => {
    const isOwner = currentUser && currentUser.id === cv.id;
    const card = document.createElement('div');
    card.className = 'student-card';
    if (isOwner) card.style.borderColor = 'var(--primary)';

    const skillsHtml = (Array.isArray(cv.skills) ? cv.skills.slice(0, 4) : [])
      .map(s => `<span class="skill-tag-sm">${s}</span>`).join('');

    card.innerHTML = `
      ${isOwner ? '<span style="position:absolute; top:12px; right:12px; background:var(--primary); color:white; font-size:0.68rem; font-weight:700; padding:2px 8px; border-radius:999px;">YOU</span>' : ''}
      <div class="student-card-top">
        <img class="student-card-avatar" src="${cv.avatar_url || 'https://api.dicebear.com/7.x/avataaars/svg?seed=' + cv.id}" alt="${cv.name}">
        <div class="student-card-info">
          <h4>${cv.name}</h4>
          <span class="student-card-id">ID: ${cv.student_id}</span>
          <p class="student-card-degree">${cv.education || 'Student'}</p>
        </div>
      </div>
      <p style="font-size:0.83rem; color:var(--text-secondary); line-height:1.4; margin-bottom:0.5rem;">
        ${cv.experience || 'No experience listed.'}
      </p>
      <div class="student-card-skills">
        ${skillsHtml}
      </div>
      <div class="student-card-actions">
        <button class="btn btn-outline" onclick="openViewModal(${cv.id})">
          👁️ View CV
        </button>
        <button class="btn ${isOwner ? 'btn-primary' : 'btn-outline'}" onclick="handleCardAction(${cv.id})">
          ${isOwner ? '✏️ Edit My CV' : '👁️ View Profile'}
        </button>
      </div>
    `;
    directoryGrid.appendChild(card);
  });
}

function handleCardAction(cvId) {
  const isOwner = currentUser && currentUser.id === cvId;
  const cv = allCVs.find(c => c.id === cvId);
  if (!cv) return;

  if (isOwner) {
    openEditModal(cv);
  } else {
    openViewModal(cvId);
  }
}

// Filter Directory
function filterDirectory(query) {
  const q = query.toLowerCase().trim();
  if (!q) {
    renderDirectory(allCVs);
    return;
  }
  const filtered = allCVs.filter(cv =>
    cv.name.toLowerCase().includes(q) ||
    cv.student_id.toLowerCase().includes(q) ||
    (cv.email && cv.email.toLowerCase().includes(q)) ||
    (cv.education && cv.education.toLowerCase().includes(q)) ||
    (Array.isArray(cv.skills) && cv.skills.some(s => s.toLowerCase().includes(q)))
  );
  renderDirectory(filtered);
}

// Filter By Skill Tag Chip
function filterBySkill(skill) {
  if (!skill) {
    searchInput.value = '';
    renderDirectory(allCVs);
    return;
  }
  searchInput.value = skill;
  filterDirectory(skill);
}

// View Full CV Modal
async function openViewModal(id) {
  const cv = await fetchSingleCV(id);
  if (!cv) return;

  const isOwner = currentUser && currentUser.id === cv.id;
  const skillsHtml = (Array.isArray(cv.skills) ? cv.skills : [])
    .map(s => `<span class="skill-tag">${s}</span>`).join('');

  viewDetailsContent.innerHTML = `
    <div style="text-align: center; margin-bottom: 1.5rem;">
      <img src="${cv.avatar_url}" style="width:90px; height:90px; border-radius:50%; border:3px solid var(--primary-light); margin-bottom:0.75rem;" alt="${cv.name}">
      <h3 style="font-size:1.4rem; font-weight:800;">${cv.name}</h3>
      <p style="color:var(--primary); font-weight:700;">Student ID: ${cv.student_id}</p>
      <p style="color:var(--text-secondary); font-size:0.9rem;">${cv.education} • CV #${cv.id}</p>
      ${isOwner 
        ? '<span style="display:inline-block; margin-top:0.5rem; background:#dcfce7; color:#166534; font-size:0.75rem; font-weight:700; padding:2px 10px; border-radius:999px;">✓ This is your CV (You have edit/delete rights)</span>' 
        : '<span style="display:inline-block; margin-top:0.5rem; background:#f1f5f9; color:#64748b; font-size:0.75rem; font-weight:600; padding:2px 10px; border-radius:999px;">🔒 Read-Only Classmate CV (Owned by ' + cv.name + ')</span>'}
    </div>

    <div style="display:grid; gap:1rem;">
      <div class="info-tile">
        <div class="info-tile-title">📧 Email / Contact</div>
        <div class="info-tile-value">${cv.email} ${cv.phone ? `• ${cv.phone}` : ''}</div>
      </div>
      <div class="info-tile">
        <div class="info-tile-title">💡 Technical Skills</div>
        <div class="skills-wrapper">${skillsHtml || 'No skills listed'}</div>
      </div>
      <div class="info-tile">
        <div class="info-tile-title">💼 Experience</div>
        <div class="info-tile-value" style="font-size:0.95rem; font-weight:normal;">${cv.experience || 'None'}</div>
      </div>
      <div class="info-tile">
        <div class="info-tile-title">📖 Bio / Story</div>
        <div class="bio-quote" style="font-size:0.92rem;">${cv.bio ? `"${cv.bio}"` : 'No bio provided'}</div>
      </div>
    </div>

    <div style="display:flex; gap:0.75rem; justify-content:flex-end; align-items:center; margin-top:1.5rem; border-top:1px solid var(--border); padding-top:1rem;">
      <button class="btn btn-outline" onclick="copyCVJson(${cv.id})">📋 Copy JSON</button>
      ${isOwner 
        ? `<button class="btn btn-primary" onclick="closeModal('viewDetailsModal'); openEditModal(allCVs.find(c => c.id === ${cv.id}))">✏️ Edit My CV</button>
           <button class="btn btn-danger" onclick="deleteCV(${cv.id}, '${cv.name}')">🗑️ Delete</button>`
        : `<div style="display:inline-flex; align-items:center; gap:0.4rem; padding:0.4rem 0.85rem; background:#fee2e2; color:#991b1b; border-radius:6px; font-size:0.8rem; font-weight:700;">
             🔒 Read-Only: Only ${cv.name} can edit or delete this CV.
           </div>`
      }
    </div>
  `;

  openModal('viewDetailsModal');
}

// Copy raw JSON to clipboard for Postman verification
function copyCVJson(id) {
  const cv = allCVs.find(c => c.id === id);
  if (!cv) return;
  navigator.clipboard.writeText(JSON.stringify(cv, null, 2));
  showToast('CV JSON copied to clipboard!', 'success');
}

// Modal Helpers
function openModal(id) {
  document.getElementById(id).classList.add('active');
}

function closeModal(id) {
  document.getElementById(id).classList.remove('active');
}

function openCreateModal() {
  cvModalTitle.innerText = 'Create New Student CV';
  cvForm.reset();
  document.getElementById('formCvId').value = '';
  document.getElementById('formPasscode').required = false;
  document.getElementById('formPasscode').placeholder = 'e.g. 1234 (Used as your login password)';
  openModal('cvFormModal');
}

function openEditModal(cv) {
  if (!cv) return;

  // Strict Security Check: No one can edit another person's CV!
  if (currentUser && currentUser.id !== cv.id) {
    showToast(`Access Denied: You cannot edit ${cv.name}'s CV! Only ${cv.name} is allowed to edit their CV.`, 'error');
    return;
  }

  if (!currentUser) {
    showToast('Please sign in to edit your CV.', 'error');
    window.location.href = '/login/';
    return;
  }

  cvModalTitle.innerText = `Edit My CV #${cv.id} (${cv.name})`;
  document.getElementById('formCvId').value = cv.id;
  document.getElementById('formName').value = cv.name;
  document.getElementById('formStudentId').value = cv.student_id;
  document.getElementById('formEmail').value = cv.email;
  document.getElementById('formPhone').value = cv.phone || '';
  document.getElementById('formEducation').value = cv.education || '';
  document.getElementById('formSkills').value = Array.isArray(cv.skills) ? cv.skills.join(', ') : '';
  document.getElementById('formExperience').value = cv.experience || '';
  document.getElementById('formBio').value = cv.bio || '';
  document.getElementById('formAvatarUrl').value = cv.avatar_url || '';
  document.getElementById('formPasscode').value = localStorage.getItem('active_cv_pin') || '';
  document.getElementById('formPasscode').placeholder = 'Leave blank or update password';
  document.getElementById('formPasscode').required = false;

  openModal('cvFormModal');
}

// Quick Avatar Presets
function setAvatarPreset(gender) {
  const name = document.getElementById('formName').value || 'student';
  const url = `https://api.dicebear.com/7.x/avataaars/svg?seed=${encodeURIComponent(name + '_' + gender)}`;
  document.getElementById('formAvatarUrl').value = url;
}

// Toast Notification
function showToast(message, type = 'info') {
  const container = document.getElementById('toastContainer');
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  const icon = type === 'success' ? '✅' : type === 'error' ? '⚠️' : 'ℹ️';
  toast.innerHTML = `<span>${icon}</span> <span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}
