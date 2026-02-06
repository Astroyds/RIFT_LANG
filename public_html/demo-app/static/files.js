// File Manager functionality
const token = localStorage.getItem('token');

if (!token) {
    window.location.href = '/login';
}

document.getElementById('logoutBtn').addEventListener('click', (e) => {
    e.preventDefault();
    localStorage.removeItem('token');
    window.location.href = '/login';
});

// Load files
async function loadFiles() {
    try {
        const response = await fetch('/api/files', {
            headers: { 'Authorization': token }
        });
        
        if (!response.ok) {
            window.location.href = '/login';
            return;
        }
        
        const data = await response.json();
        displayFiles(data.files);
    } catch (error) {
        console.error('Failed to load files:', error);
    }
}

function displayFiles(files) {
    const listEl = document.getElementById('fileList');
    
    if (files.length === 0) {
        listEl.innerHTML = '<p>No files uploaded yet</p>';
        return;
    }
    
    listEl.innerHTML = files.map(file => `
        <div class="file-item">
            <div class="file-info">
                <div class="file-name">📄 ${escapeHtml(file.filename)}</div>
                <div class="file-meta">
                    ${formatBytes(file.filesize)} • ${formatDate(file.uploaded_at)}
                </div>
            </div>
            <button class="btn btn-small" style="background: var(--danger);">
                Delete
            </button>
        </div>
    `).join('');
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

function formatDate(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

// Upload file
document.getElementById('uploadForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];
    
    if (!file) return;
    
    // Show progress
    const progressBar = document.getElementById('uploadProgress');
    progressBar.style.display = 'block';
    
    // Simulate upload
    try {
        const response = await fetch('/api/files', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': token
            },
            body: JSON.stringify({
                filename: file.name,
                filesize: file.size
            })
        });
        
        if (response.ok) {
            fileInput.value = '';
            progressBar.style.display = 'none';
            loadFiles();
        }
    } catch (error) {
        console.error('Failed to upload file:', error);
    }
});

loadFiles();