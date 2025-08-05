/* ── CAROUSEL (if you still use it) ─────────────────── */
const next = document.querySelector('.next');
const prev = document.querySelector('.prev');

if (next) {
  next.addEventListener('click', () => {
    const items = document.querySelectorAll('.item');
    if (items.length) document.querySelector('.slide').appendChild(items[0]);
  });
}

if (prev) {
  prev.addEventListener('click', () => {
    const items = document.querySelectorAll('.item');
    if (items.length) document.querySelector('.slide').prepend(items[items.length - 1]);
  });
}

/* ── PROFILE DRAWER LOGIC (ENHANCED) ───────────────── */
const profileBtn = document.getElementById('profileButton');
const profilePanel = document.getElementById('profilePanel');
const profileCloseBtn = document.getElementById('profileCloseBtn');
const profileExitBtn = document.getElementById('profileExitBtn');
const profileForm = document.getElementById('profileForm');
const logoutBtn = document.getElementById('logoutBtn');
const saveBtn = document.getElementById('saveBtn');
const editBtn = document.getElementById('editBtn');

/* Sample user data */
const userData = {
  name: 'Clay Jensen',
  mobile: '',
  city: '',
  docs: 12,
  chats: 5,
  isProfileSaved: false
};

/* Sample data for sections */
const samplePDFs = [
  { id: 1, name: "Research_Paper.pdf", uploadDate: "2025-01-15", size: "2.3 MB" },
  { id: 2, name: "Invoice_December.pdf", uploadDate: "2025-01-10", size: "456 KB" },
  { id: 3, name: "Contract_Agreement.pdf", uploadDate: "2025-01-08", size: "1.8 MB" }
];

const sampleChats = [
  { id: 1, title: "Chat 1", lastMessage: "How can I analyze this document?", date: "2025-01-15" },
  { id: 2, title: "Chat 2", lastMessage: "What are the key points in this PDF?", date: "2025-01-14" },
  { id: 3, title: "Document Analysis", lastMessage: "Great! That helps a lot.", date: "2025-01-12" }
];

/* ── PROFILE FUNCTIONS ──────────────────────────── */
function openProfile() {
  document.getElementById('profileName').textContent = userData.name;
  document.getElementById('docCount').textContent = samplePDFs.length;
  document.getElementById('chatCount').textContent = sampleChats.length;
  
  loadProfileData();
  profilePanel.classList.add('open');
  profilePanel.setAttribute('aria-hidden', 'false');
  initializeSections();
}

function closeProfile() {
  profilePanel.classList.remove('open');
  profilePanel.setAttribute('aria-hidden', 'true');
}

function loadProfileData() {
  const mobileInput = document.getElementById('mobileInput');
  const cityInput = document.getElementById('cityInput');
  const mobileDisplay = document.getElementById('mobileDisplay');
  const cityDisplay = document.getElementById('cityDisplay');
  
  if (userData.isProfileSaved && (userData.mobile || userData.city)) {
    // Show saved data
    mobileInput.style.display = 'none';
    cityInput.style.display = 'none';
    saveBtn.style.display = 'none';
    editBtn.style.display = 'block';
    
    mobileDisplay.style.display = 'block';
    cityDisplay.style.display = 'block';
    
    mobileDisplay.textContent = userData.mobile || 'Not provided';
    cityDisplay.textContent = userData.city || 'Not provided';
  } else {
    // Show input fields
    mobileInput.style.display = 'block';
    cityInput.style.display = 'block';
    saveBtn.style.display = 'block';
    editBtn.style.display = 'none';
    
    mobileDisplay.style.display = 'none';
    cityDisplay.style.display = 'none';
    
    mobileInput.value = userData.mobile;
    cityInput.value = userData.city;
  }
}

function showSuccessMessage(message) {
  const profileContent = document.querySelector('.profile-content');
  const existingMessage = document.querySelector('.success-message');
  
  if (existingMessage) existingMessage.remove();
  
  const successDiv = document.createElement('div');
  successDiv.className = 'success-message';
  successDiv.textContent = message;
  
  profileContent.insertBefore(successDiv, profileContent.firstChild);
  
  setTimeout(() => successDiv.remove(), 3000);
}

/* ── SECTION FUNCTIONS ──────────────────────────── */
function initializeSections() {
  const pdfSectionBtn = document.getElementById('pdfSectionBtn');
  const chatSectionBtn = document.getElementById('chatSectionBtn');
  const pdfSection = document.getElementById('pdfSection');
  const chatSection = document.getElementById('chatSection');

  // PDF Section Toggle
  if (pdfSectionBtn && pdfSection) {
    pdfSectionBtn.addEventListener('click', () => {
      const isOpen = pdfSection.style.display === 'block';
      pdfSection.style.display = isOpen ? 'none' : 'block';
      pdfSectionBtn.classList.toggle('active', !isOpen);
      
      if (!isOpen) loadPDFs();
    });
  }

  // Chat Section Toggle
  if (chatSectionBtn && chatSection) {
    chatSectionBtn.addEventListener('click', () => {
      const isOpen = chatSection.style.display === 'block';
      chatSection.style.display = isOpen ? 'none' : 'block';
      chatSectionBtn.classList.toggle('active', !isOpen);
      
      if (!isOpen) loadChatHistory();
    });
  }
}

function loadPDFs() {
  const pdfList = document.getElementById('pdfList');
  if (!pdfList) return;

  if (samplePDFs.length === 0) {
    pdfList.innerHTML = `<div class="empty-state">📄<br>No PDFs uploaded yet</div>`;
    return;
  }

  pdfList.innerHTML = samplePDFs.map(pdf => `
    <div class="pdf-item">
      <div class="pdf-info">
        <div class="pdf-details">
          <div class="pdf-name">${pdf.name}</div>
          <div class="pdf-date">Uploaded: ${pdf.uploadDate} • ${pdf.size}</div>
        </div>
      </div>
      <div class="pdf-actions">
        <button class="pdf-action-btn" onclick="viewPDF(${pdf.id})">View</button>
        <button class="pdf-action-btn" onclick="downloadPDF(${pdf.id})">Download</button>
      </div>
    </div>
  `).join('');
}

function loadChatHistory() {
  const chatHistoryList = document.getElementById('chatHistoryList');
  if (!chatHistoryList) return;

  if (sampleChats.length === 0) {
    chatHistoryList.innerHTML = `<div class="empty-state">💬<br>No chat history available</div>`;
    return;
  }

  chatHistoryList.innerHTML = sampleChats.map(chat => `
    <div class="chat-item" onclick="openChat(${chat.id})">
      <div class="chat-info">
        <div class="chat-details">
          <div class="chat-title">${chat.title}</div>
          <div class="chat-preview">${chat.lastMessage}</div>
        </div>
      </div>
      <div class="chat-date">${chat.date}</div>
    </div>
  `).join('');
}

/* ── ACTION FUNCTIONS ──────────────────────────── */
function viewPDF(pdfId) {
  const pdf = samplePDFs.find(p => p.id === pdfId);
  alert(`Opening ${pdf.name} for viewing`);
}

function downloadPDF(pdfId) {
  const pdf = samplePDFs.find(p => p.id === pdfId);
  alert(`Downloading ${pdf.name}`);
}

function openChat(chatId) {
  const chat = sampleChats.find(c => c.id === chatId);
  alert(`Opening ${chat.title}`);
  closeProfile();
}

/* ── EVENT LISTENERS ──────────────────────────── */
if (profileBtn) profileBtn.addEventListener('click', openProfile);
if (profileCloseBtn) profileCloseBtn.addEventListener('click', closeProfile);
if (profileExitBtn) profileExitBtn.addEventListener('click', closeProfile);

// Click outside to close
if (profilePanel) {
  profilePanel.addEventListener('click', e => {
    if (e.target === profilePanel) closeProfile();
  });
}

// Save form
if (profileForm) {
  profileForm.addEventListener('submit', e => {
    e.preventDefault();
    
    const mobile = document.getElementById('mobileInput').value.trim();
    const city = document.getElementById('cityInput').value.trim();
    
    // Update user data
    userData.mobile = mobile;
    userData.city = city;
    userData.isProfileSaved = true;
    
    // Show success popup
    alert('Profile saved successfully!');
    
    // Show success message in profile
    showSuccessMessage('Profile information saved successfully!');
    
    // Switch to display mode
    loadProfileData();
  });
}

// Edit button
if (editBtn) {
  editBtn.addEventListener('click', () => {
    userData.isProfileSaved = false;
    loadProfileData();
  });
}

// Logout
if (logoutBtn) {
  logoutBtn.addEventListener('click', () => {
    if (confirm('Are you sure you want to log out?')) {
      alert('Logged out successfully!');
      window.location.href = 'index.html';  
    }
  });
}

