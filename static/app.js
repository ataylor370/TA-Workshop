document.addEventListener('DOMContentLoaded', fetchTasks);

async function fetchTasks() {
    const response = await fetch('/api/tasks');
    const tasks = await response.json();
    const taskList = document.getElementById('task-list');
    taskList.innerHTML = '';

    tasks.forEach(task => {
        const li = document.createElement('li');
        const taskContent = document.createElement('div');
        const title = document.createElement('span');
        const priority = document.createElement('span');
        const deleteButton = document.createElement('button');
        const taskPriority = task.priority || 'Medium';

        title.textContent = task.title;
        priority.textContent = taskPriority;
        priority.className = `priority-badge priority-${taskPriority.toLowerCase()}`;
        deleteButton.textContent = 'Delete';
        deleteButton.className = 'delete-btn';
        deleteButton.onclick = () => deleteTask(task.id);

        taskContent.className = 'task-content';
        taskContent.appendChild(title);
        taskContent.appendChild(priority);
        li.appendChild(taskContent);
        li.appendChild(deleteButton);
        taskList.appendChild(li);
    });
}

async function addTask() {
    const titleInput = document.getElementById('task-title');
    const priorityInput = document.getElementById('task-priority');
    const title = titleInput.value.trim();
    const priority = priorityInput.value || 'Medium';

    if (!title) return;

    await fetch('/api/tasks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, priority })
    });

    titleInput.value = '';
    priorityInput.value = 'Medium';
    fetchTasks();
}

async function deleteTask(id) {
    await fetch(`/api/tasks/${id}`, {
        method: 'DELETE'
    });
    fetchTasks();
}
