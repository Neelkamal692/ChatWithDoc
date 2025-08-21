// DOM Elements
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const urlInput = document.getElementById('urlInput');
const processBtn = document.getElementById('processBtn');
const fileList = document.getElementById('fileList');
const chatMessages = document.getElementById('chatMessages');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');

// API Base URL
const API_BASE = '/';

console.log('JavaScript loaded successfully');

// Event Listeners
uploadArea.addEventListener('click', () => {
    console.log('Upload area clicked');
    fileInput.click();
});

fileInput.addEventListener('change', (e) => {
    console.log('File input changed');
    const files = e.target.files;
    console.log('Files detected:', files.length); // Debug log
    
    if (files.length > 0) {
        console.log('Files selected:', files.length);
        
        // Clear previous documents and UI first
        clearPreviousDocuments();
        
        // Store files in an array BEFORE clearing input
        const fileArray = Array.from(files);
        console.log('Files stored in array:', fileArray.length);
        
        // Now process each file
        fileArray.forEach((file, index) => {
            console.log(`Processing file ${index + 1}:`, file.name, 'Type:', file.type);
            uploadFile(file);
        });
    } else {
        console.log('No files detected in change event');
    }
});

processBtn.addEventListener('click', () => {
    console.log('Process button clicked');
    processAllDocuments();
});

sendButton.addEventListener('click', () => {
    console.log('Send button clicked');
    sendMessage();
});

messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        console.log('Enter key pressed');
        sendMessage();
    }
});

// Separate function for clearing previous documents (doesn't clear current input)
function clearPreviousDocuments() {
    console.log('Clearing previous documents');
    
    // Clear the file list UI
    fileList.innerHTML = '';
    
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
    fetch(`${API_BASE}clear-documents`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        console.log('Clear documents response status:', response.status);
        return response.json();
    })
    .then(data => {
        console.log('Previous documents cleared:', data);
    })
    .catch(error => {
        console.error('Error clearing documents:', error);
    });
}

// Function for complete reset (used by clear button if you add one)
function clearAllFilesSync() {
    console.log('Clearing all files completely');
    
    // Clear the file input (only call this when you want to reset everything)
    fileInput.value = '';
    
    // Clear everything else
    clearPreviousDocuments();
}

function uploadFile(file) {
    console.log('Starting file upload for:', file.name);
    
    const formData = new FormData();
    formData.append('file', file);
    
    // Show file in UI immediately
    addFileToList(file.name, formatFileSize(file.size), 'uploading');
    
    console.log('Making fetch request to:', `${API_BASE}upload`);
    
    fetch(`${API_BASE}upload`, {
        method: 'POST',
        body: formData
    })
    .then(response => {
        console.log('Upload response status:', response.status);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('Upload response data:', data);
        if (data.error) {
            updateFileStatus(file.name, 'error');
            alert('Error uploading file: ' + data.error);
        } else {
            updateFileStatus(file.name, 'uploaded');
            console.log('File uploaded successfully:', file.name);
        }
    })
    .catch(error => {
        console.error('Upload error:', error);
        updateFileStatus(file.name, 'error');
        alert('Error uploading file: ' + error.message);
    });
}

function processAllDocuments() {
    console.log('Processing all documents');
    
    const url = urlInput.value.trim();
    const files = document.querySelectorAll('.file-item');
    
    console.log('URL:', url, 'Files count:', files.length);
    
    if (files.length === 0 && !url) {
        alert('Please upload files or enter a URL first');
        return;
    }
    
    // Show processing animation
    showProcessing();
    
    // Process all uploaded files
    let filePromise = Promise.resolve();
    if (files.length > 0) {
        // Update status to processing
        files.forEach(fileItem => {
            const fileName = fileItem.dataset.filename;
            updateFileStatus(fileName, 'processing');
        });
        
        console.log('Calling process-documents endpoint');
        
        filePromise = fetch(`${API_BASE}process-documents`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => {
            console.log('Process documents response status:', response.status);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Process documents response:', data);
            if (data.error) {
                throw new Error(data.error);
            }
            // Mark all files as processed
            files.forEach(fileItem => {
                const fileName = fileItem.dataset.filename;
                updateFileStatus(fileName, 'processed');
            });
            addBotMessage(`Successfully processed ${data.processed_count} files!`);
            return data;
        });
    }
    
    // Process URL if provided
    let urlPromise = Promise.resolve();
    if (url) {
        console.log('Processing URL:', url);
        
        urlPromise = fetch(`${API_BASE}process-url`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url: url })
        })
        .then(response => {
            console.log('Process URL response status:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('Process URL response:', data);
            if (data.error) {
                throw new Error(data.error);
            }
            addBotMessage(`URL processed successfully! Found ${data.document_info.num_pages} pages with ${data.document_info.num_chunks} text chunks.`);
            return data;
        });
    }
    
    // Wait for all processing to complete
    Promise.all([filePromise, urlPromise])
        .then(() => {
            console.log('All processing completed');
            hideProcessing();
            addBotMessage("All documents and URLs have been processed successfully! You can now ask questions about them.");
        })
        .catch(error => {
            console.error('Processing error:', error);
            hideProcessing();
            alert('Error processing documents: ' + error.message);
        });
}

function sendMessage() {
    const message = messageInput.value.trim();
    console.log('Sending message:', message);
    
    if (message) {
        addUserMessage(message);
        messageInput.value = '';
        
        // Show typing indicator
        showTypingIndicator();
        
        fetch(`${API_BASE}chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: message })
        })
        .then(response => {
            console.log('Chat response status:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('Chat response:', data);
            hideTypingIndicator();
            if (data.error) {
                addBotMessage("Sorry, I encountered an error: " + data.error);
            } else {
                addBotMessage(data.response);
            }
        })
        .catch(error => {
            console.error('Chat error:', error);
            hideTypingIndicator();
            addBotMessage("Sorry, I encountered an error processing your request.");
        });
    }
}

function addFileToList(name, size, status = 'success') {
    console.log('Adding file to list:', name, 'Status:', status);
    
    const fileItem = document.createElement('div');
    fileItem.className = 'file-item';
    fileItem.dataset.filename = name;
    
    let statusIcon = '';
    if (status === 'uploading') {
        statusIcon = '<i class="fas fa-spinner fa-spin"></i>';
    } else if (status === 'processing') {
        statusIcon = '<i class="fas fa-cog fa-spin"></i>';
    } else if (status === 'error') {
        statusIcon = '<i class="fas fa-exclamation-circle" style="color: var(--danger);"></i>';
    } else if (status === 'processed') {
        statusIcon = '<i class="fas fa-check-circle" style="color: var(--success);"></i>';
    } else if (status === 'uploaded') {
        statusIcon = '<i class="fas fa-file-alt"></i>';
    } else {
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
        console.log('Removing file:', name);
        fileItem.remove();
    });
}

function updateFileStatus(name, status) {
    console.log('Updating file status:', name, 'to', status);
    
    const fileItems = document.querySelectorAll('.file-item');
    fileItems.forEach(item => {
        if (item.dataset.filename === name) {
            let statusIcon = '';
            if (status === 'uploading') {
                statusIcon = '<i class="fas fa-spinner fa-spin"></i>';
            } else if (status === 'processing') {
                statusIcon = '<i class="fas fa-cog fa-spin"></i>';
            } else if (status === 'error') {
                statusIcon = '<i class="fas fa-exclamation-circle" style="color: var(--danger);"></i>';
            } else if (status === 'processed') {
                statusIcon = '<i class="fas fa-check-circle" style="color: var(--success);"></i>';
            } else if (status === 'uploaded') {
                statusIcon = '<i class="fas fa-file-alt"></i>';
            } else {
                statusIcon = '<i class="fas fa-file-alt"></i>';
            }
            const iconElement = item.querySelector('i');
            if (iconElement) {
                iconElement.outerHTML = statusIcon;
            }
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
    // Convert markdown to HTML
    const markdownHTML = DOMPurify.sanitize(marked.parse(text));
    messageDiv.className = 'message bot-message';
    messageDiv.innerHTML = `
        <div class="message-header">
            <i class="fas fa-robot"></i> ChatWithDoc Assistant
        </div>
        <div class="message-content">${markdownHTML}</div>
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
    console.log('Showing processing indicator');
    const processingDiv = document.createElement('div');
    processingDiv.className = 'processing';
    processingDiv.id = 'processingIndicator';
    processingDiv.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing documents and URLs...';
    
    // Replace chat messages with processing indicator
    chatMessages.innerHTML = '';
    chatMessages.appendChild(processingDiv);
}

function hideProcessing() {
    console.log('Hiding processing indicator');
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
    console.log('Drag over upload area');
    uploadArea.style.borderColor = 'var(--primary)';
    uploadArea.style.backgroundColor = 'rgba(67, 97, 238, 0.1)';
});

uploadArea.addEventListener('dragleave', () => {
    console.log('Drag leave upload area');
    uploadArea.style.borderColor = 'var(--light-gray)';
    uploadArea.style.backgroundColor = '';
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    console.log('Files dropped on upload area');
    uploadArea.style.borderColor = 'var(--light-gray)';
    uploadArea.style.backgroundColor = '';
    
    const files = e.dataTransfer.files;
    console.log('Dropped files count:', files.length);
    
    if (files.length > 0) {
        // Clear previous documents first
        clearPreviousDocuments();
        
        // Store files in array before processing
        const fileArray = Array.from(files);
        
        // Process each file
        fileArray.forEach(file => {
            console.log('Processing dropped file:', file.name, 'Type:', file.type);
            if (file.type === 'application/pdf' || 
                file.type === 'application/msword' || 
                file.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' ||
                file.type === 'text/plain') {
                uploadFile(file);
            } else {
                console.log('Unsupported file type:', file.type);
                alert(`Unsupported file type: ${file.type}. Please upload PDF, DOC, DOCX, or TXT files.`);
            }
        });
    }
});

console.log('All event listeners attached successfully');