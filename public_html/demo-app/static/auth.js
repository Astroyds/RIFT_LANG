// Login functionality
document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const messageEl = document.getElementById('message');
    
    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            localStorage.setItem('token', data.token);
            localStorage.setItem('username', data.user.username);
            messageEl.textContent = 'Login successful! Redirecting...';
            messageEl.className = 'message success';
            setTimeout(() => {
                window.location.href = '/dashboard';
            }, 1000);
        } else {
            messageEl.textContent = data.error || 'Login failed';
            messageEl.className = 'message error';
        }
    } catch (error) {
        messageEl.textContent = 'Network error';
        messageEl.className = 'message error';
    }
});