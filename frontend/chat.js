/* ─── Initial chat store ───────────────────────────── */
const sessions = [
  { id: 1, name: "Chat 1", html: '<div class="message">Start chatting…</div>' }
];
let currentId   = 1;
let queuedFiles = [];                           // up to 2 files
const allowedExt = ["pdf", "docx", "txt"];

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
}
previewBar.addEventListener("click", (e) => {
  if (!e.target.classList.contains("remove-file")) return;
  queuedFiles.splice(+e.target.dataset.idx, 1);
  renderPreview();
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
chatForm.addEventListener("submit", (e) => {
  e.preventDefault();
  const txt = chatInput.value.trim();
  if (!txt && !queuedFiles.length) return;

  if (txt) {
    chatWindow.insertAdjacentHTML(
      "beforeend",
      `<div class="message user">${txt}</div>`
    );
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

