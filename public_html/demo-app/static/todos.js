// Todo Manager functionality
const token = localStorage.getItem('token');

if (!token) {
    window.location.href = '/login';
}

// Logout
document.getElementById('logoutBtn').addEventListener('click', (e) => {
    e.preventDefault();
    localStorage.removeItem('token');
    window.location.href = '/login';
});

let currentFilter = 'all';

// Load todos
async function loadTodos() {
    try {
        const response = await fetch('/api/todos', {
            headers: { 'Authorization': token }
        });
        
        if (!response.ok) {
            window.location.href = '/login';
            return;
        }
        
        const data = await response.json();
        displayTodos(data.todos);
    } catch (error) {
        console.error('Failed to load todos:', error);
    }
}

function displayTodos(todos) {
    const filtered = todos.filter(todo => {
        if (currentFilter === 'all') return true;
        if (currentFilter === 'active') return todo.completed === 0;
        if (currentFilter === 'completed') return todo.completed === 1;
    });
    
    const listEl = document.getElementById('todoList');
    
    if (filtered.length === 0) {
        listEl.innerHTML = '<p>No todos found</p>';
        return;
    }
    
    listEl.innerHTML = filtered.map(todo => `
        <div class="todo-item ${todo.completed ? 'completed' : ''}">
            <div class="todo-content">
                <div class="todo-title">${escapeHtml(todo.title)}</div>
                ${todo.description ? `<div class="todo-description">${escapeHtml(todo.description)}</div>` : ''}
            </div>
            <div class="todo-actions">
                <button class="btn btn-small btn-${todo.completed ? 'secondary' : 'success'}" 
                        onclick="toggleTodo(${todo.id}, ${todo.completed})">
                    ${todo.completed ? 'Undo' : 'Complete'}
                </button>
                <button class="btn btn-small" style="background: var(--danger);" 
                        onclick="deleteTodo(${todo.id})">
                    Delete
                </button>
            </div>
        </div>
    `).join('');
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Add todo
document.getElementById('addTodoForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const title = document.getElementById('todoTitle').value;
    const description = document.getElementById('todoDescription').value;
    
    try {
        const response = await fetch('/api/todos', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': token
            },
            body: JSON.stringify({ title, description })
        });
        
        if (response.ok) {
            document.getElementById('todoTitle').value = '';
            document.getElementById('todoDescription').value = '';
            loadTodos();
        }
    } catch (error) {
        console.error('Failed to add todo:', error);
    }
});

// Toggle todo
async function toggleTodo(id, completed) {
    try {
        await fetch(`/api/todos/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': token
            },
            body: JSON.stringify({ completed: completed ? 0 : 1 })
        });
        loadTodos();
    } catch (error) {
        console.error('Failed to toggle todo:', error);
    }
}

// Delete todo
async function deleteTodo(id) {
    if (!confirm('Delete this todo?')) return;
    
    try {
        await fetch(`/api/todos/${id}`, {
            method: 'DELETE',
            headers: { 'Authorization': token }
        });
        loadTodos();
    } catch (error) {
        console.error('Failed to delete todo:', error);
    }
}

// Filter buttons
document.querySelectorAll('[data-filter]').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('[data-filter]').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentFilter = btn.dataset.filter;
        loadTodos();
    });
});

loadTodos();