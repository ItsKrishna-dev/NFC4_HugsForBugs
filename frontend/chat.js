/* ─── Initial chat store ───────────────────────────── */
let sessions = [
  { id: 1, name: "Chat 1", html: '<div class="message">Start chatting…</div>' }
];
let currentId   = 1;
let queuedFiles = [];                           // up to 2 files
const allowedExt = ["pdf", "docx", "txt"];
let userData = null;
let currentDocumentId = null;  // Track the current document for RAG
let ragInitialized = false;    // Track if RAG is initialized

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
    chatInput.placeholder = "Ask a question about your documents...";
    // Reset RAG state when switching to Q&A mode
    ragInitialized = false;
    currentDocumentId = null;
  } else {
    chatInput.placeholder = "Type text to summarize or upload documents...";
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

  // Show loading indicator
  const loadingId = Date.now();
  chatWindow.insertAdjacentHTML(
    "beforeend",
    `<div class="message system" id="loading-${loadingId}">🤖 Processing...</div>`
  );
  chatWindow.scrollTop = chatWindow.scrollHeight;

  try {
    if (queuedFiles.length > 0) {
      // Process uploaded files
      for (const file of queuedFiles) {
        // Add file message
        chatWindow.insertAdjacentHTML(
          "beforeend",
          `<div class="message user">📎 ${file.name}</div>`
        );
        
        // Process document with FastAPI
        const formData = new FormData();
        formData.append('file', file);
        formData.append('user_id', userData ? userData.user_id : 'anonymous');
        
        const response = await fetch('http://localhost:8000/process-document', {
          method: 'POST',
          body: formData
        });
        
        if (response.ok) {
          const result = await response.json();
          
          // Store document ID for RAG
          currentDocumentId = result.document_id;
          
          // Display summary
          const summary = result.summary;
          let summaryHtml = `<div class="message system">📄 <strong>${file.name}</strong> Summary:</div>`;
          
          // Overall summary
          if (summary.overall_summary) {
            summaryHtml += `<div class="message system"><strong>📝 Document Overview:</strong><br>${summary.overall_summary}</div>`;
          }
          
          // Section summaries
          if (summary.sections && summary.sections.length > 0) {
            summaryHtml += `<div class="message system"><strong>📑 Section Analysis:</strong></div>`;
            summary.sections.forEach(section => {
              summaryHtml += `<div class="message system"><strong>📖 ${section.title}:</strong><br>${section.summary}</div>`;
            });
          }
          
          // Document stats
          summaryHtml += `<div class="message system"><strong>📊 Stats:</strong> ${result.total_chunks} chunks, ${result.total_characters} characters</div>`;
          
          // Initialize RAG engine if in Q&A mode
          if (currentMode === "qa" && currentDocumentId) {
            try {
              const ragFormData = new FormData();
              ragFormData.append('document_id', currentDocumentId);
              ragFormData.append('user_id', userData ? userData.user_id : 'anonymous');
              
              const ragResponse = await fetch('http://localhost:8000/rag/initialize', {
                method: 'POST',
                body: ragFormData
              });
              
              if (ragResponse.ok) {
                const ragResult = await ragResponse.json();
                summaryHtml += `<div class="message system">🤖 <strong>RAG Engine Initialized:</strong> Ready for Q&A with ${ragResult.total_chunks} chunks</div>`;
                ragInitialized = true;
              } else {
                summaryHtml += `<div class="message system error">❌ Failed to initialize RAG engine</div>`;
              }
            } catch (error) {
              console.error('Error initializing RAG:', error);
              summaryHtml += `<div class="message system error">❌ Error initializing RAG engine</div>`;
            }
          }
          
          chatWindow.insertAdjacentHTML("beforeend", summaryHtml);
        } else {
          const errorData = await response.json();
          chatWindow.insertAdjacentHTML(
            "beforeend",
            `<div class="message system error">❌ Error processing ${file.name}: ${errorData.detail}</div>`
          );
        }
      }
    } else if (txt) {
      // Add user message
      const modeIndicator = currentMode === "qa" ? "💬" : "📝";
      chatWindow.insertAdjacentHTML(
        "beforeend",
        `<div class="message user">${modeIndicator} ${txt}</div>`
      );
      
      // If in summarize mode and no files, treat as text summarization
      if (currentMode === "summarize") {
        const formData = new FormData();
        formData.append('text', txt);
        formData.append('max_len', '150');
        formData.append('min_len', '40');
        
        const response = await fetch('http://localhost:8000/summarize-text', {
          method: 'POST',
          body: formData
        });
        
        if (response.ok) {
          const result = await response.json();
          const summary = result.summary;
          
          let summaryHtml = `<div class="message system">📝 <strong>Text Summary:</strong></div>`;
          
          if (summary.overall_summary) {
            summaryHtml += `<div class="message system">${summary.overall_summary}</div>`;
          }
          
          if (summary.sections && summary.sections.length > 0) {
            summaryHtml += `<div class="message system"><strong>📑 Sections:</strong></div>`;
            summary.sections.forEach(section => {
              summaryHtml += `<div class="message system"><strong>📖 ${section.title}:</strong><br>${section.summary}</div>`;
            });
          }
          
          chatWindow.insertAdjacentHTML("beforeend", summaryHtml);
        } else {
          const errorData = await response.json();
          chatWindow.insertAdjacentHTML(
            "beforeend",
            `<div class="message system error">❌ Error summarizing text: ${errorData.detail}</div>`
          );
        }
      } else {
        // Q&A mode - use RAG engine
        if (!ragInitialized) {
          chatWindow.insertAdjacentHTML(
            "beforeend",
            `<div class="message system error">❌ Please upload and process a document first to enable Q&A mode.</div>`
          );
        } else {
          try {
            // Ask question using RAG engine
            const ragFormData = new FormData();
            ragFormData.append('question', txt);
            ragFormData.append('user_id', userData ? userData.user_id : 'anonymous');
            
            const ragResponse = await fetch('http://localhost:8000/rag/ask', {
              method: 'POST',
              body: ragFormData
            });
            
            if (ragResponse.ok) {
              const ragResult = await ragResponse.json();
              
              // Display answer
              let answerHtml = `<div class="message system">🤖 <strong>Answer:</strong><br>${ragResult.answer}</div>`;
              
              // Display sources if available
              if (ragResult.sources && ragResult.sources.length > 0) {
                answerHtml += `<div class="message system"><strong>📚 Sources:</strong></div>`;
                ragResult.sources.forEach(source => {
                  answerHtml += `<div class="message system"><strong>📖 ${source.source}:</strong><br><em>${source.content}</em></div>`;
                });
              }
              
              chatWindow.insertAdjacentHTML("beforeend", answerHtml);
            } else {
              const errorData = await ragResponse.json();
              chatWindow.insertAdjacentHTML(
                "beforeend",
                `<div class="message system error">❌ Error asking question: ${errorData.detail}</div>`
              );
            }
          } catch (error) {
            console.error('Error asking question:', error);
            chatWindow.insertAdjacentHTML(
              "beforeend",
              `<div class="message system error">❌ Error asking question: ${error.message}</div>`
            );
          }
        }
      }
      
      // Save chat message to backend if user is logged in
      if (userData) {
        try {
          const formData = new FormData();
          formData.append('document_id', 'general');
          formData.append('question', txt);
          formData.append('answer', 'AI response generated');
          formData.append('user_id', userData.user_id);
          formData.append('mode', currentMode);
          
          await fetch('http://localhost:8000/chat/', {
            method: 'POST',
            body: formData
          });
        } catch (error) {
          console.error('Error saving chat message:', error);
        }
      }
    }
  } catch (error) {
    console.error('Error processing request:', error);
    chatWindow.insertAdjacentHTML(
      "beforeend",
      `<div class="message system error">❌ Error: ${error.message}</div>`
    );
  } finally {
    // Remove loading indicator
    const loadingElement = document.getElementById(`loading-${loadingId}`);
    if (loadingElement) {
      loadingElement.remove();
    }
    
    // Clear input and files
    chatInput.value = "";
    queuedFiles = [];
    renderPreview();
    chatWindow.scrollTop = chatWindow.scrollHeight;
  }
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
  
  // Reset RAG state for new chat
  ragInitialized = false;
  currentDocumentId = null;
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
  
  // Reset RAG state when switching chats
  ragInitialized = false;
  currentDocumentId = null;
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
