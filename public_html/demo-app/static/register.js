// Register functionality
document.getElementById('registerForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = document.getElementById('username').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    const messageEl = document.getElementById('message');
    
    if (password !== confirmPassword) {
        messageEl.textContent = 'Passwords do not match';
        messageEl.className = 'message error';
        return;
    }
    
    try {
        const response = await fetch('/api/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, email, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            messageEl.textContent = 'Registration successful! Redirecting to login...';
            messageEl.className = 'message success';
            setTimeout(() => {
                window.location.href = '/login';
            }, 1500);
        } else {
            messageEl.textContent = data.error || 'Registration failed';
            messageEl.className = 'message error';
        }
    } catch (error) {
        messageEl.textContent = 'Network error';
        messageEl.className = 'message error';
    }
});