const alertRegion = document.getElementById("alert-region");
const taskTableBody = document.getElementById("task-table-body");
const taskTableWrap = document.getElementById("task-table-wrap");
const emptyState = document.getElementById("empty-state");
const taskForm = document.getElementById("task-form");
const taskModalEl = document.getElementById("task-modal");
const taskModal = bootstrap.Modal.getOrCreateInstance(taskModalEl);
const taskIdInput = document.getElementById("task-id");
const taskTitleInput = document.getElementById("task-title");
const taskDescriptionInput = document.getElementById("task-description");
const taskModalTitle = document.getElementById("task-modal-title");

function showAlert(message, type = "danger") {
  alertRegion.innerHTML = `
    <div class="alert alert-${type} alert-dismissible fade show" role="alert">
      ${message}
      <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    </div>
  `;
}

function formatDate(value) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return "—";
  }
  const pad = (part) => String(part).padStart(2, "0");
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

function renderTasks(tasks) {
  const total = tasks.length;
  const completed = tasks.filter((task) => task.is_completed).length;
  document.getElementById("count-total").textContent = total;
  document.getElementById("count-completed").textContent = completed;
  document.getElementById("count-pending").textContent = total - completed;

  if (total === 0) {
    emptyState.classList.remove("d-none");
    taskTableWrap.classList.add("d-none");
    taskTableBody.innerHTML = "";
    return;
  }

  emptyState.classList.add("d-none");
  taskTableWrap.classList.remove("d-none");
  taskTableBody.innerHTML = tasks
    .map((task) => {
      const badgeClass = task.is_completed ? "text-bg-success" : "text-bg-warning";
      const badgeLabel = task.is_completed ? "Completed" : "Pending";
      const titleClass = task.is_completed ? "text-decoration-line-through text-secondary" : "";
      const toggleLabel = task.is_completed ? "Mark pending" : "Complete";
      const description = task.description ? task.description : "—";
      return `
        <tr data-task-id="${task.id}">
          <td><span class="badge ${badgeClass}">${badgeLabel}</span></td>
          <td class="${titleClass}"></td>
          <td></td>
          <td>${formatDate(task.created_at)}</td>
          <td class="text-end text-nowrap">
            <button class="btn btn-sm btn-outline-secondary" data-action="toggle">${toggleLabel}</button>
            <button class="btn btn-sm btn-outline-primary" data-action="edit">Edit</button>
            <button class="btn btn-sm btn-outline-danger" data-action="delete">Delete</button>
          </td>
        </tr>
      `;
    })
    .join("");

  Array.from(taskTableBody.querySelectorAll("tr")).forEach((row, index) => {
    const cells = row.querySelectorAll("td");
    cells[1].textContent = tasks[index].title;
    cells[2].textContent = tasks[index].description || "—";
  });
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  if (response.status === 204) {
    return null;
  }
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = data.detail;
    const message = Array.isArray(detail)
      ? detail.map((item) => item.msg || JSON.stringify(item)).join(", ")
      : detail || "Request failed";
    throw new Error(message);
  }
  return data;
}

async function refreshTasks() {
  const tasks = await api("/api/tasks");
  renderTasks(tasks);
}

document.getElementById("new-task-btn").addEventListener("click", () => {
  taskForm.reset();
  taskIdInput.value = "";
  taskModalTitle.textContent = "New task";
});

taskForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = {
    title: taskTitleInput.value.trim(),
    description: taskDescriptionInput.value.trim(),
  };
  try {
    if (taskIdInput.value) {
      await api(`/api/tasks/${taskIdInput.value}`, {
        method: "PATCH",
        body: JSON.stringify(payload),
      });
    } else {
      await api("/api/tasks", {
        method: "POST",
        body: JSON.stringify(payload),
      });
    }
    taskModal.hide();
    await refreshTasks();
    showAlert("Task saved.", "success");
  } catch (error) {
    showAlert(error.message);
  }
});

taskTableBody.addEventListener("click", async (event) => {
  const button = event.target.closest("button[data-action]");
  if (!button) {
    return;
  }
  const row = button.closest("tr");
  const taskId = row.dataset.taskId;
  const action = button.dataset.action;
  try {
    if (action === "delete") {
      if (!window.confirm("Delete this task?")) {
        return;
      }
      await api(`/api/tasks/${taskId}`, { method: "DELETE" });
    } else if (action === "toggle") {
      const isCompleted = row.querySelector(".badge").textContent.trim() === "Completed";
      await api(`/api/tasks/${taskId}`, {
        method: "PATCH",
        body: JSON.stringify({ is_completed: !isCompleted }),
      });
    } else if (action === "edit") {
      const task = await api(`/api/tasks/${taskId}`);
      taskIdInput.value = task.id;
      taskTitleInput.value = task.title;
      taskDescriptionInput.value = task.description;
      taskModalTitle.textContent = "Edit task";
      taskModal.show();
      return;
    }
    await refreshTasks();
  } catch (error) {
    showAlert(error.message);
  }
});
