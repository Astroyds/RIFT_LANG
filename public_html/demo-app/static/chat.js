// Chat functionality
const token = localStorage.getItem('token');
const username = localStorage.getItem('username');

if (!token) {
    window.location.href = '/login';
}

document.getElementById('logoutBtn').addEventListener('click', (e) => {
    e.preventDefault();
    localStorage.removeItem('token');
    window.location.href = '/login';
});

// Load messages
async function loadMessages() {
    try {
        const response = await fetch('/api/messages', {
            headers: { 'Authorization': token }
        });
        
        if (!response.ok) {
            window.location.href = '/login';
            return;
        }
        
        const data = await response.json();
        displayMessages(data.messages.reverse());
    } catch (error) {
        console.error('Failed to load messages:', error);
    }
}

function displayMessages(messages) {
    const container = document.getElementById('chatMessages');
    
    if (messages.length === 0) {
        container.innerHTML = '<p>No messages yet. Be the first to send one!</p>';
        return;
    }
    
    container.innerHTML = messages.map(msg => {
        const isOwn = msg.username === username;
        return `
            <div class="chat-message ${isOwn ? 'own' : ''}">
                ${!isOwn ? `<div class="username">${escapeHtml(msg.username)}</div>` : ''}
                <div class="message-text">${escapeHtml(msg.message)}</div>
                <div class="timestamp">${formatTime(msg.created_at)}</div>
            </div>
        `;
    }).join('');
    
    container.scrollTop = container.scrollHeight;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatTime(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

// Send message
document.getElementById('chatForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const input = document.getElementById('messageInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    try {
        const response = await fetch('/api/messages', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': token
            },
            body: JSON.stringify({ message })
        });
        
        if (response.ok) {
            input.value = '';
            loadMessages();
        }
    } catch (error) {
        console.error('Failed to send message:', error);
    }
});

// Auto-refresh messages every 3 seconds
setInterval(loadMessages, 3000);

loadMessages();