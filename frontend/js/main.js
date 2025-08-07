// DOM Elements
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const urlInput = document.getElementById('urlInput');
const processBtn = document.getElementById('processBtn');
const fileList = document.getElementById('fileList');
const chatMessages = document.getElementById('chatMessages');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');

// API Base URL (adjust based on your deployment)
const API_BASE = '/api';

// Event Listeners
uploadArea.addEventListener('click', () => {
    fileInput.click();
});

fileInput.addEventListener('change', (e) => {
    const files = e.target.files;
    if (files.length > 0) {
        // Clear everything first
        clearAllFilesSync();
        // Then upload new files
        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            uploadFile(file);
        }
    }
});

processBtn.addEventListener('click', processAllDocuments);

sendButton.addEventListener('click', sendMessage);
messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

// Functions
function clearAllFilesSync() {
    // Clear the file list UI immediately
    fileList.innerHTML = '';
    // Clear the file input
    fileInput.value = '';
    // Clear URL input
    urlInput.value = '';
    
    // Clear chat messages and restore initial state
    chatMessages.innerHTML = `
        <div class="message bot-message">
            <div class="message-header">
                <i class="fas fa-robot"></i> ChatWithDoc Assistant
            </div>
            <div class="message-content">
                Previous documents cleared. Ready for new uploads!
            </div>
        </div>
    `;
    
    // Call backend to clear previous documents
    fetch(`${API_BASE}/clear-documents`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log('Previous documents cleared');
    })
    .catch(error => {
        console.error('Error clearing documents:', error);
    });
}

function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    // Show processing in UI
    addFileToList(file.name, formatFileSize(file.size), 'uploaded');
    
    fetch(`${API_BASE}/upload`, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            updateFileStatus(file.name, 'error');
            alert('Error uploading file: ' + data.error);
        } else {
            // Keep as 'uploaded' status - will be processed when button is clicked
            updateFileStatus(file.name, 'uploaded');
        }
    })
    .catch(error => {
        updateFileStatus(file.name, 'error');
        console.error('Error:', error);
        alert('Error uploading file');
    });
}

function processAllDocuments() {
    const url = urlInput.value.trim();
    const files = document.querySelectorAll('.file-item');
    
    if (files.length === 0 && !url) {
        alert('Please upload files or enter a URL first');
        return;
    }
    
    // Show processing animation
    showProcessing();
    
    // Process all uploaded files first (only those not already processed)
    const filePromises = Array.from(files)
        .filter(fileItem => {
            const fileName = fileItem.dataset.filename;
            const statusIcon = fileItem.querySelector('i');
            // Only process files that are not already processed (no green check)
            return !statusIcon.classList.contains('fa-check-circle');
        })
        .map(fileItem => {
            const fileName = fileItem.dataset.filename;
            return new Promise((resolve) => {
                // Simulate processing time for files
                setTimeout(() => {
                    updateFileStatus(fileName, 'processed');
                    resolve();
                }, 1000);
            });
        });
    
    // Process URL if provided
    let urlPromise = Promise.resolve();
    if (url) {
        urlPromise = fetch(`${API_BASE}/process-url`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url: url })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            // Show URL processing success
            addBotMessage(`URL processed successfully! Found ${data.document_info.num_pages} pages with ${data.document_info.num_chunks} text chunks.`);
            return data;
        });
    }
    
    // Wait for all processing to complete
    Promise.all([...filePromises, urlPromise])
        .then(() => {
            hideProcessing();
            addBotMessage("All documents and URLs have been processed successfully! You can now ask questions about them.");
        })
        .catch(error => {
            hideProcessing();
            console.error('Error:', error);
            alert('Error processing documents: ' + error.message);
        });
}

function sendMessage() {
    const message = messageInput.value.trim();
    if (message) {
        addUserMessage(message);
        messageInput.value = '';
        
        // Show typing indicator
        showTypingIndicator();
        
        fetch(`${API_BASE}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: message })
        })
        .then(response => response.json())
        .then(data => {
            hideTypingIndicator();
            if (data.error) {
                addBotMessage("Sorry, I encountered an error: " + data.error);
            } else {
                addBotMessage(data.response);
            }
        })
        .catch(error => {
            hideTypingIndicator();
            console.error('Error:', error);
            addBotMessage("Sorry, I encountered an error processing your request.");
        });
    }
}

function addFileToList(name, size, status = 'success') {
    const fileItem = document.createElement('div');
    fileItem.className = 'file-item';
    fileItem.dataset.filename = name;
    
    let statusIcon = '';
    if (status === 'processing') {
        statusIcon = '<i class="fas fa-spinner fa-spin"></i>';
    } else if (status === 'error') {
        statusIcon = '<i class="fas fa-exclamation-circle" style="color: var(--danger);"></i>';
    } else if (status === 'processed') {
        statusIcon = '<i class="fas fa-check-circle" style="color: var(--success);"></i>';
    } else if (status === 'uploaded') {
        statusIcon = '<i class="fas fa-file-alt"></i>';
    }
    else {
        statusIcon = '<i class="fas fa-file-alt"></i>';
    }
    
    fileItem.innerHTML = `
        ${statusIcon}
        <div class="file-info">
            <div class="file-name">${name}</div>
            <div class="file-size">${size}</div>
        </div>
        <div class="file-actions">
            <button title="Remove"><i class="fas fa-times"></i></button>
        </div>
    `;
    
    fileList.appendChild(fileItem);
    
    // Add remove functionality
    fileItem.querySelector('.file-actions button').addEventListener('click', () => {
        fileItem.remove();
    });
}

function updateFileStatus(name, status) {
    const fileItems = document.querySelectorAll('.file-item');
    fileItems.forEach(item => {
        if (item.dataset.filename === name) {
            let statusIcon = '';
            if (status === 'processing') {
                statusIcon = '<i class="fas fa-spinner fa-spin"></i>';
            } else if (status === 'error') {
                statusIcon = '<i class="fas fa-exclamation-circle" style="color: var(--danger);"></i>';
            } else if (status === 'processed') {
                statusIcon = '<i class="fas fa-check-circle" style="color: var(--success);"></i>';
            } else if (status === 'uploaded') {
                statusIcon = '<i class="fas fa-file-alt"></i>';
            }
            else {
                statusIcon = '<i class="fas fa-file-alt"></i>';
            }
            item.querySelector('i').outerHTML = statusIcon;
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

function addUserMessage(text) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message user-message';
    messageDiv.innerHTML = `
        <div class="message-header">
            <i class="fas fa-user"></i> You
        </div>
        <div class="message-content">${text}</div>
    `;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function addBotMessage(text) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot-message';
    messageDiv.innerHTML = `
        <div class="message-header">
            <i class="fas fa-robot"></i> ChatWithDoc Assistant
        </div>
        <div class="message-content">${text}</div>
    `;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showTypingIndicator() {
    const typingIndicator = document.createElement('div');
    typingIndicator.className = 'typing-indicator';
    typingIndicator.id = 'typingIndicator';
    typingIndicator.innerHTML = `
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
    `;
    chatMessages.appendChild(typingIndicator);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function hideTypingIndicator() {
    const typingIndicator = document.getElementById('typingIndicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

function showProcessing() {
    const processingDiv = document.createElement('div');
    processingDiv.className = 'processing';
    processingDiv.id = 'processingIndicator';
    processingDiv.innerHTML = '<i class="fas fa-spinner"></i> Processing documents and URLs...';
    
    // Replace chat messages with processing indicator
    chatMessages.innerHTML = '';
    chatMessages.appendChild(processingDiv);
}

function hideProcessing() {
    const processingIndicator = document.getElementById('processingIndicator');
    if (processingIndicator) {
        processingIndicator.remove();
    }
    
    // Restore initial message
    chatMessages.innerHTML = `
        <div class="message bot-message">
            <div class="message-header">
                <i class="fas fa-robot"></i> ChatWithDoc Assistant
            </div>
            <div class="message-content">
                Hello! I'm your document assistant. Upload some documents or enter URLs, then ask me anything about their content. I'll help you find answers quickly.
            </div>
        </div>
    `;
}

// Drag and drop functionality
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.style.borderColor = 'var(--primary)';
    uploadArea.style.backgroundColor = 'rgba(67, 97, 238, 0.1)';
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.style.borderColor = 'var(--light-gray)';
    uploadArea.style.backgroundColor = '';
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.style.borderColor = 'var(--light-gray)';
    uploadArea.style.backgroundColor = '';
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        // Clear everything first
        clearAllFilesSync();
        // Then upload new files
        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            if (file.type === 'application/pdf' || 
                file.type === 'application/msword' || 
                file.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' ||
                file.type === 'text/plain') {
                uploadFile(file);
            }
        }
    }
});