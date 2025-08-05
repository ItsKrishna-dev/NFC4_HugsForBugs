/* ─── Initial chat store ───────────────────────────── */
let sessions = [
  { id: 1, name: "Chat 1", html: '<div class="message">Start chatting…</div>' }
];
let currentId   = 1;
let queuedFiles = [];                           // up to 2 files
const allowedExt = ["pdf", "docx", "txt"];
let userData = null;

// Load user data and chat history on page load
document.addEventListener('DOMContentLoaded', async function() {
    // Get user data from localStorage
    const userDataStr = localStorage.getItem('userData');
    if (!userDataStr) {
        alert('Please login first');
        window.location.href = './Loginpage.html';
        return;
    }
    
    userData = JSON.parse(userDataStr);
    
    // Set user name in profile section
    const userNameElement = document.getElementById('userName');
    if (userNameElement) {
        userNameElement.textContent = userData.username;
    }
    
    // Load chat history from backend
    try {
        const response = await fetch(`http://localhost:8000/auth/chat-history/${userData.user_id}`);
        const data = await response.json();
        
        if (response.ok && data.chat_history.length > 0) {
            // Group chat history by document_id or create a single chat session
            const chatHistory = data.chat_history;
            let chatHtml = '<div class="message">Previous chat history:</div>';
            
            chatHistory.forEach(chat => {
                chatHtml += `<div class="message user">${chat.question}</div>`;
                chatHtml += `<div class="message">${chat.answer}</div>`;
            });
            
            sessions[0].html = chatHtml;
            chatWindow.innerHTML = chatHtml;
        }
    } catch (error) {
        console.error('Error loading chat history:', error);
    }
});

/* ─── DOM shortcuts ───────────────────────────────── */
const chatWindow = document.getElementById("chatWindow");
const chatNameEl = document.getElementById("chatName");
const chatList   = document.getElementById("chatList");
const newChatBtn = document.getElementById("newChatBtn");

const fileInput  = document.getElementById("fileInput");
const previewBar = document.getElementById("filePreviewArea");
const chatForm   = document.getElementById("chatInputForm");
const chatInput  = document.getElementById("chatInput");
const exitBtn    = document.getElementById("exitBtn");
const logoutBtn  = document.getElementById("logoutBtn");
const modeToggle = document.getElementById("modeToggle");
const saveBtn    = document.getElementById("saveBtn"); // Add save button reference

/* ─── File-preview helpers ────────────────────────── */
function renderPreview() {
  previewBar.innerHTML = "";
  queuedFiles.forEach((file, idx) => {
    previewBar.insertAdjacentHTML(
      "beforeend",
      `<div class="file-block">
          <span class="file-name">📄 ${file.name}</span>
          <button class="remove-file" data-idx="${idx}">remove</button>
       </div>`
    );
  });
  previewBar.style.display = queuedFiles.length ? "block" : "none";
  
  // Update save button visibility based on PDF files
  updateSaveButtonVisibility();
}

previewBar.addEventListener("click", (e) => {
  if (!e.target.classList.contains("remove-file")) return;
  queuedFiles.splice(+e.target.dataset.idx, 1);
  renderPreview();
});

/* ─── Save button functionality ──────────────────── */
function updateSaveButtonVisibility() {
  const pdfFiles = queuedFiles.filter(file => 
    file.type === 'application/pdf' || 
    file.name.toLowerCase().endsWith('.pdf')
  );
  
  if (saveBtn) {
    saveBtn.style.display = pdfFiles.length > 0 ? 'block' : 'none';
  }
}

// Save button click handler
if (saveBtn) {
  saveBtn.addEventListener('click', async () => {
    const pdfFiles = queuedFiles.filter(file => 
      file.type === 'application/pdf' || 
      file.name.toLowerCase().endsWith('.pdf')
    );
    
    if (pdfFiles.length > 0 && userData) {
      try {
        // Create FormData for file upload
        const formData = new FormData();
        
        pdfFiles.forEach((file, index) => {
          formData.append(`file_${index}`, file);
        });
        formData.append('user_id', userData.user_id);
        formData.append('document_count', pdfFiles.length);
        
        // Upload files to backend
        const response = await fetch('http://localhost:8000/upload/documents', {
          method: 'POST',
          body: formData
        });
        
        const result = await response.json();
        
        if (response.ok) {
          // Show success message
          alert(`PDF file(s) saved successfully!\nFiles: ${pdfFiles.map(f => f.name).join(', ')}`);
          
          // Add success message to chat
          chatWindow.insertAdjacentHTML(
            "beforeend",
            `<div class="message system">✅ Successfully saved ${pdfFiles.length} PDF file(s): ${pdfFiles.map(f => f.name).join(', ')}</div>`
          );
          
          // Clear saved files from queue (optional)
          queuedFiles = queuedFiles.filter(file => 
            !(file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf'))
          );
          renderPreview();
          
          chatWindow.scrollTop = chatWindow.scrollHeight;
        } else {
          alert('Error saving files: ' + result.message);
        }
      } catch (error) {
        console.error('Error saving PDF files:', error);
        alert('Error saving files. Please try again.');
      }
    } else {
      alert('No PDF files to save or user not logged in.');
    }
  });
}

/* ─── Mode toggle functionality ───────────────────── */
let currentMode = "qa"; // Default mode

modeToggle.addEventListener("click", () => {
  currentMode = currentMode === "qa" ? "summarize" : "qa";
  
  // Update button appearance
  modeToggle.setAttribute("data-mode", currentMode);
  
  // Update button text and icon
  const toggleText = modeToggle.querySelector(".toggle-text");
  const toggleIcon = modeToggle.querySelector(".toggle-icon");
  
  if (currentMode === "qa") {
    toggleText.textContent = "Q&A";
    toggleIcon.textContent = "💬";
  } else {
    toggleText.textContent = "Summarize";
    toggleIcon.textContent = "📝";
  }
  
  // Update placeholder text based on mode
  if (currentMode === "qa") {
    chatInput.placeholder = "Ask a question...";
  } else {
    chatInput.placeholder = "Ask to summarize...";
  }
});

/* ─── Handle file select ──────────────────────────── */
fileInput.addEventListener("change", (e) => {
  queuedFiles = [...queuedFiles, ...Array.from(e.target.files)]
    .filter((f) => allowedExt.includes(f.name.split(".").pop().toLowerCase()))
    .slice(0, 2);                // keep max 2
  fileInput.value = "";
  renderPreview();
});

/* ─── Send message ───────────────────────────────── */
chatForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const txt = chatInput.value.trim();
  if (!txt && !queuedFiles.length) return;

  if (txt) {
    // Add mode indicator to the message
    const modeIndicator = currentMode === "qa" ? "💬" : "📝";
    chatWindow.insertAdjacentHTML(
      "beforeend",
      `<div class="message user">${modeIndicator} ${txt}</div>`
    );
    
    // Save chat message to backend
    if (userData) {
      try {
        const formData = new FormData();
        formData.append('document_id', 'general'); // You can modify this based on your needs
        formData.append('question', txt);
        formData.append('answer', 'AI response will be added here'); // You can integrate with your AI service
        formData.append('user_id', userData.user_id);
        formData.append('mode', currentMode); // Add mode to the request
        
        await fetch('http://localhost:8000/chat/', {
          method: 'POST',
          body: formData
        });
      } catch (error) {
        console.error('Error saving chat message:', error);
      }
    }
  }
  
  queuedFiles.forEach((f) => {
    chatWindow.insertAdjacentHTML(
      "beforeend",
      `<div class="message user">📎 ${f.name}</div>`
    );
  });

  chatInput.value = "";
  queuedFiles = [];
  renderPreview();
  chatWindow.scrollTop = chatWindow.scrollHeight;
});

/* ─── Persist current chat before leaving it ─────── */
function persistCurrentChat() {
  const html = chatWindow.innerHTML.trim();
  const existing = sessions.find((s) => s.id === currentId);
  existing.html = html;
}

/* ─── New chat creation ──────────────────────────── */
newChatBtn.addEventListener("click", () => {
  persistCurrentChat();

  currentId = sessions.length
    ? Math.max(...sessions.map((s) => s.id)) + 1
    : 1;
  const name = `Chat ${currentId}`;
  sessions.push({ id: currentId, name, html: '<div class="message">Start chatting…</div>' });

  chatList.querySelectorAll("li").forEach((li) => li.classList.remove("active"));
  chatList.insertAdjacentHTML(
    "afterbegin",
    `<li class="active" data-id="${currentId}">${name}</li>`
  );

  chatNameEl.textContent = name;
  chatWindow.innerHTML = sessions.find((s) => s.id === currentId).html;
});

/* ─── Switch chat from sidebar ───────────────────── */
chatList.addEventListener("click", (e) => {
  const li = e.target.closest("li");
  if (!li || +li.dataset.id === currentId) return;

  persistCurrentChat();
  chatList
    .querySelectorAll("li")
    .forEach((el) => el.classList.toggle("active", el === li));

  const session = sessions.find((s) => s.id == li.dataset.id);
  currentId = session.id;
  chatNameEl.textContent = session.name;
  chatWindow.innerHTML = session.html;
  queuedFiles = [];
  renderPreview();
});

/* ─── Exit chat (NO history deletion) ─────────────── */
exitBtn.addEventListener("click", (e) => {
  // optional confirmation
  const ok = confirm("Leave this page and go back to Home?");
  if (!ok) {
    e.preventDefault();          // stay on page
    return;
  }

  /* Persist the current chat in memory before leaving */
  persistCurrentChat();

  /* TODO: save `sessions` to your backend here if desired
  fetch('/api/save', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify(sessions)
  });
  */
  /* No reset, no deletion — the sessions array remains intact.
     The <a> element then navigates to ./MainHomePage.html */
});

/* ─── Logout functionality ───────────────────────────── */
logoutBtn.addEventListener("click", () => {
  const ok = confirm("Are you sure you want to logout?");
  if (ok) {
    localStorage.removeItem('userData');
    window.location.href = './Loginpage.html';
  }
});
