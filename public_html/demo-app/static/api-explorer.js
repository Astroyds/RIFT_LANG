// API Explorer functionality
const token = localStorage.getItem('token');

if (!token) {
    window.location.href = '/login';
}

document.getElementById('logoutBtn').addEventListener('click', (e) => {
    e.preventDefault();
    localStorage.removeItem('token');
    window.location.href = '/login';
});

// Endpoint selection
document.querySelectorAll('.endpoint-item').forEach(item => {
    item.addEventListener('click', () => {
        document.getElementById('apiMethod').value = item.dataset.method;
        document.getElementById('apiPath').value = item.dataset.path;
        
        // Set example body based on endpoint
        const path = item.dataset.path;
        let body = '';
        
        if (path.includes('/todos') && item.dataset.method === 'POST') {
            body = '{\n  "title": "New Todo",\n  "description": "Todo description"\n}';
        } else if (path.includes('/messages') && item.dataset.method === 'POST') {
            body = '{\n  "message": "Hello, world!"\n}';
        } else if (path.includes('/todos/:id') && item.dataset.method === 'PUT') {
            body = '{\n  "completed": 1\n}';
        }
        
        document.getElementById('apiBody').value = body;
    });
});

// Send request
document.getElementById('sendRequest').addEventListener('click', async () => {
    const method = document.getElementById('apiMethod').value;
    const path = document.getElementById('apiPath').value;
    const body = document.getElementById('apiBody').value;
    
    const options = {
        method,
        headers: { 'Authorization': token }
    };
    
    if (body && (method === 'POST' || method === 'PUT')) {
        options.headers['Content-Type'] = 'application/json';
        try {
            options.body = body;
        } catch (e) {
            document.getElementById('responseBody').textContent = 'Invalid JSON body';
            return;
        }
    }
    
    try {
        const response = await fetch(path, options);
        const data = await response.json();
        
        const statusEl = document.getElementById('responseStatus');
        statusEl.textContent = `Status: ${response.status} ${response.statusText}`;
        statusEl.style.background = response.ok ? '#d1fae5' : '#fee2e2';
        statusEl.style.color = response.ok ? '#065f46' : '#991b1b';
        
        document.getElementById('responseBody').textContent = 
            JSON.stringify(data, null, 2);
    } catch (error) {
        document.getElementById('responseBody').textContent = 
            `Error: ${error.message}`;
    }
});