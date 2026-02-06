// Analytics functionality
const token = localStorage.getItem('token');

if (!token) {
    window.location.href = '/login';
}

document.getElementById('logoutBtn').addEventListener('click', (e) => {
    e.preventDefault();
    localStorage.removeItem('token');
    window.location.href = '/login';
});

// Load analytics
async function loadAnalytics() {
    try {
        const response = await fetch('/api/analytics', {
            headers: { 'Authorization': token }
        });
        
        if (!response.ok) {
            window.location.href = '/login';
            return;
        }
        
        const data = await response.json();
        
        document.getElementById('totalUsers').textContent = data.totalUsers;
        document.getElementById('totalTodos').textContent = data.totalTodos;
        document.getElementById('totalMessages').textContent = data.totalMessages;
        document.getElementById('totalFiles').textContent = data.totalFiles;
        
        // Mock activity
        document.getElementById('activityList').innerHTML = `
            <p>📊 System has ${data.totalUsers} registered users</p>
            <p>✅ ${data.totalTodos} total todos created</p>
            <p>💬 ${data.totalMessages} messages exchanged</p>
            <p>📁 ${data.totalFiles} files uploaded</p>
        `;
        
        // Mock top users table
        document.getElementById('topUsers').innerHTML = `
            <tr>
                <td>Demo User</td>
                <td>-</td>
                <td>-</td>
                <td>-</td>
            </tr>
        `;
    } catch (error) {
        console.error('Failed to load analytics:', error);
    }
}

loadAnalytics();