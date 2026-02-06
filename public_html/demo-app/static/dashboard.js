// Dashboard functionality
const token = localStorage.getItem('token');

if (!token) {
    window.location.href = '/login';
}

// Logout handler
document.getElementById('logoutBtn').addEventListener('click', (e) => {
    e.preventDefault();
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    window.location.href = '/login';
});

// Load stats
async function loadStats() {
    try {
        const response = await fetch('/api/stats', {
            headers: { 'Authorization': token }
        });
        
        if (!response.ok) {
            window.location.href = '/login';
            return;
        }
        
        const data = await response.json();
        
        document.getElementById('welcomeMessage').textContent = 
            `Welcome back, ${data.username}!`;
        document.getElementById('todoCount').textContent = data.todoCount;
        document.getElementById('completedCount').textContent = data.completedCount;
        document.getElementById('fileCount').textContent = data.fileCount;
        document.getElementById('messageCount').textContent = data.messageCount;
    } catch (error) {
        console.error('Failed to load stats:', error);
    }
}

loadStats();