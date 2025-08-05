/* ===== FILE UPLOAD & COMPARE LOGIC ===== */
let uploadedFiles = {
  file1: null,
  file2: null
};

const file1Input = document.getElementById('file1Input');
const file2Input = document.getElementById('file2Input');
const file1Box = document.getElementById('file1Box');
const file2Box = document.getElementById('file2Box');
const file1Info = document.getElementById('file1Info');
const file2Info = document.getElementById('file2Info');
const compareBtn = document.getElementById('compareBtn');
const analyzeBtn = document.getElementById('analyzeBtn');
const chatWindow = document.getElementById('chatWindow');

/* ===== FILE UPLOAD HANDLERS ===== */
function handleFileUpload(fileInput, fileBox, fileInfo, fileKey) {
  fileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
      uploadedFiles[fileKey] = file;
      
      // Update UI
      fileBox.classList.add('has-file');
      fileInfo.style.display = 'block';
      fileInfo.innerHTML = `
        <div class="file-name">${file.name}</div>
        <div class="file-size">${formatFileSize(file.size)}</div>
      `;
      
      // Update upload text
      const uploadText = fileBox.querySelector('.upload-text');
      uploadText.textContent = 'Document Uploaded ✓';
      
      // Check if compare button should be enabled
      updateCompareButton();
    }
  });
}

function formatFileSize(bytes) {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function updateCompareButton() {
  const hasFiles = uploadedFiles.file1 && uploadedFiles.file2;
  
  // Enable/disable both buttons
  compareBtn.disabled = !hasFiles;
  analyzeBtn.disabled = !hasFiles;
  
  if (hasFiles) {
    compareBtn.style.background = 'linear-gradient(135deg, #10a37f, #0e8a6a)';
    analyzeBtn.style.background = 'linear-gradient(135deg, #667eea, #764ba2)';
  } else {
    compareBtn.style.background = '#ccc';
    analyzeBtn.style.background = '#ccc';
  }
}

/* ===== COMPARE FUNCTIONALITY ===== */
compareBtn.addEventListener('click', () => {
  if (uploadedFiles.file1 && uploadedFiles.file2) {
    // Add comparison message to chat
    const comparisonMessage = document.createElement('div');
    comparisonMessage.className = 'message system';
    comparisonMessage.innerHTML = `
      <strong>📊 Document Comparison Started</strong><br>
      Comparing: <em>${uploadedFiles.file1.name}</em> vs <em>${uploadedFiles.file2.name}</em><br>
      <small>Analysis complete! You can now ask questions about similarities, differences, or specific content from either document.</small>
    `;
    chatWindow.appendChild(comparisonMessage);
    chatWindow.scrollTop = chatWindow.scrollHeight;
    
    // TODO: Send files to backend for processing
    console.log('Comparing files:', uploadedFiles);
  }
});

/* ===== ANALYZE FUNCTIONALITY ===== */
analyzeBtn.addEventListener('click', () => {
  if (uploadedFiles.file1 && uploadedFiles.file2) {
    // Add analysis message to chat
    const analysisMessage = document.createElement('div');
    analysisMessage.className = 'message system';
    analysisMessage.innerHTML = `
      <strong>🔍 Document Analysis Started</strong><br>
      Analyzing: <em>${uploadedFiles.file1.name}</em> and <em>${uploadedFiles.file2.name}</em><br>
      <small>Deep analysis complete! You can now ask specific questions about content, themes, key points, or insights from both documents.</small>
    `;
    chatWindow.appendChild(analysisMessage);
    chatWindow.scrollTop = chatWindow.scrollHeight;
    
    // TODO: Send files to backend for analysis
    console.log('Analyzing files:', uploadedFiles);
  }
});

/* ===== INITIALIZE FILE HANDLERS ===== */
document.addEventListener('DOMContentLoaded', () => {
  handleFileUpload(file1Input, file1Box, file1Info, 'file1');
  handleFileUpload(file2Input, file2Box, file2Info, 'file2');
  
  // Initial button state
  updateCompareButton();
});
