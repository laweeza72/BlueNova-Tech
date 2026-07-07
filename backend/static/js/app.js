// Core ERP Utility and Interaction Layer
window.addActivityLog = function(userId, action) {
    const logs = JSON.parse(localStorage.getItem("erp_logs") || "[]");
    const newLog = {
        id: logs.length + 1,
        user_id: userId,
        action: action,
        ip_address: "127.0.0.1",
        user_agent: navigator.userAgent,
        timestamp: new Date().toISOString()
    };
    logs.unshift(newLog);
    localStorage.setItem("erp_logs", JSON.stringify(logs));
};
// Named alias so bare addActivityLog() calls also work
function addActivityLog(userId, action) { window.addActivityLog(userId, action); }

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function refreshSystemState() {
    return fetch("/erp/api/system-state/")
        .then(res => {
            if (res.status === 401 || res.status === 403) {
                window.location.href = "/auth/login/";
            }
            return res.json();
        })
        .then(data => {
            localStorage.setItem("erp_users", JSON.stringify(data.users));
            localStorage.setItem("erp_files", JSON.stringify(data.files));
            localStorage.setItem("erp_notifications", JSON.stringify(data.notifications));
            localStorage.setItem("erp_messages", JSON.stringify(data.messages));
            localStorage.setItem("erp_logs", JSON.stringify(data.logs));
            localStorage.setItem("erp_history", JSON.stringify(data.history));
            
            handleNotificationsBadge();
            const pathName = window.location.pathname;
            if (pathName.includes("dashboard.html") || pathName.endsWith("/erp/dashboard/")) {
                renderUserDashboard();
            } else if (pathName.includes("admin-dashboard.html") || pathName.endsWith("/erp/admin-dashboard/")) {
                renderAdminDashboard();
            } else if (pathName.includes("user-management.html") || pathName.endsWith("/erp/user-management/")) {
                renderUserManagement();
            } else if (pathName.includes("notifications.html") || pathName.endsWith("/erp/notifications/")) {
                renderNotificationsPage();
            }
            return data;
        })
        .catch(err => console.error("System state refresh failed:", err));
}

window.filterUsers = function(filterVal, btnEl) {
    currentFilter = filterVal;
    document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
    if (btnEl) {
        btnEl.classList.add('active');
    }
    renderUserManagement();
};


function startRealtimePolling() {
    const session = localStorage.getItem("erp_session");
    if (!session) return;
    
    setInterval(() => {
        fetch("/erp/api/check-status/")
            .then(res => {
                if (res.status === 401 || res.status === 403) {
                    window.location.href = "/auth/login/";
                }
                return res.json();
            })
            .then(data => {
                if (data.status === 'deleted') {
                    showToast(data.message || "Your account has been removed.", "danger");
                    localStorage.clear();
                    setTimeout(() => {
                        window.location.href = "/auth/login/";
                    }, 2000);
                } else if (data.status === 'disabled') {
                    showToast(data.message || "Your account has been disabled.", "danger");
                    localStorage.clear();
                    setTimeout(() => {
                        window.location.href = "/auth/login/";
                    }, 2000);
                } else if (data.status === 'ok') {
                    // Update badges
                    const badges = document.querySelectorAll(".notif-badge");
                    badges.forEach(badge => {
                        if (data.unread_count > 0) {
                            badge.textContent = data.unread_count;
                            badge.style.display = "inline-block";
                        } else {
                            badge.style.display = "none";
                        }
                    });
                }
            })
            .catch(err => console.debug("Status sync check failed (user offline or backend idle)."));
    }, 4000);
}

document.addEventListener("DOMContentLoaded", () => {
    initTheme();
    setupSidebarToggle();
    handleNotificationsBadge();
    startRealtimePolling();
    
    // Page specific handlers
    const pathName = window.location.pathname;
    
    if (pathName.includes("dashboard.html") || pathName.endsWith("/erp/dashboard/")) {
        renderUserDashboard();
    } else if (pathName.includes("admin-dashboard.html") || pathName.endsWith("/erp/admin-dashboard/")) {
        renderAdminDashboard();
    } else if (pathName.includes("user-management.html") || pathName.endsWith("/erp/user-management/")) {
        const searchInput = document.getElementById("admin-search-users");
        if (searchInput) {
            searchInput.addEventListener("input", (e) => {
                searchQuery = e.target.value.toLowerCase().trim();
                renderUserManagement();
            });
        }
        const urlParams = new URLSearchParams(window.location.search);
        const filterParam = urlParams.get('filter');
        if (filterParam) {
            currentFilter = filterParam;
            setTimeout(() => {
                const activeBtn = Array.from(document.querySelectorAll('.filter-btn'))
                    .find(btn => btn.getAttribute('onclick').includes(`'${filterParam}'`));
                if (activeBtn) {
                    document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
                    activeBtn.classList.add('active');
                }
            }, 100);
        }
        renderUserManagement();
    } else if (pathName.includes("upload-files.html") || pathName.endsWith("/erp/upload-files/")) {
        setupFileUploader();
    } else if (pathName.includes("messages.html") || pathName.endsWith("/erp/messages/")) {
        setupMessagesSystem();
    } else if (pathName.includes("edit-profile.html") || pathName.endsWith("/erp/edit-profile/")) {
        setupEditProfileForm();
    } else if (pathName.includes("settings.html") || pathName.endsWith("/erp/settings/")) {
        setupSettings();
    } else if (pathName.includes("activity-logs.html") || pathName.endsWith("/erp/activity-logs/")) {
        renderActivityLogs();
    } else if (pathName.includes("data-management.html") || pathName.endsWith("/erp/data-management/")) {
        setupDataManagement();
    } else if (pathName.includes("reports.html") || pathName.endsWith("/erp/reports/")) {
        renderReportsPage();
    } else if (pathName.includes("analytics.html") || pathName.endsWith("/erp/analytics/")) {
        renderAnalyticsPage();
    } else if (pathName.includes("search.html") || pathName.endsWith("/erp/search/")) {
        setupSearchPage();
    } else if (pathName.includes("history.html") || pathName.endsWith("/erp/history/")) {
        renderHistoryPage();
    } else if (pathName.includes("notifications.html") || pathName.endsWith("/erp/notifications/")) {
        renderNotificationsPage();
    } else if (pathName.includes("profile.html") || pathName.endsWith("/erp/profile/") || (pathName.includes("/erp/profile/") && !pathName.includes("/erp/edit-profile/"))) {
        renderProfilePage();
    } else if (pathName.includes("feedback.html") || pathName.endsWith("/erp/feedback/")) {
        setupFeedbackForm();
    } else if (pathName.includes("help-center.html") || pathName.endsWith("/erp/help-center/")) {
        setupHelpCenter();
    }
});

// Toast Notifier
function showToast(message, type = "info") {
    let container = document.querySelector(".toast-container");
    if (!container) {
        container = document.createElement("div");
        container.className = "toast-container";
        document.body.appendChild(container);
    }
    
    const toast = document.createElement("div");
    toast.className = `custom-toast border-start border-4`;
    
    let icon = "💡";
    let borderClass = "border-info";
    if (type === "success") { icon = "✅"; borderClass = "border-success"; }
    else if (type === "danger") { icon = "❌"; borderClass = "border-danger"; }
    else if (type === "warning") { icon = "⚠️"; borderClass = "border-warning"; }
    
    toast.classList.add(borderClass);
    toast.innerHTML = `<span>${icon}</span> <div>${message}</div>`;
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.opacity = "0";
        toast.style.transform = "translateX(100%) scale(0.9)";
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// Global Auth Getters
function getLoggedInUser() {
    const session = localStorage.getItem("erp_session");
    if (!session) return null;
    
    const users = JSON.parse(localStorage.getItem("erp_users") || "[]");
    return users.find(u => u.token === session) || null;
}

function checkAuthentication(requiredRole) {
    const user = getLoggedInUser();
    if (!user) {
        window.location.href = "/auth/login/";
        return null;
    }
    if (requiredRole && user.role !== requiredRole) {
        window.location.href = "/404/";
        return null;
    }
    return user;
}

// Theme Engine
function initTheme() {
    const currentTheme = localStorage.getItem("erp_theme") || "dark";
    document.documentElement.setAttribute("data-theme", currentTheme);
    
    const switchers = document.querySelectorAll(".theme-toggle-btn");
    switchers.forEach(btn => {
        btn.addEventListener("click", () => {
            const nextTheme = document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
            document.documentElement.setAttribute("data-theme", nextTheme);
            localStorage.setItem("erp_theme", nextTheme);
            showToast(`Theme switched to ${nextTheme} mode!`, "success");
        });
    });
}

// Sidebar responsive drawer and toggle collapse
function setupSidebarToggle() {
    const togglers = document.querySelectorAll(".sidebar-toggle-btn");
    const sidebar = document.querySelector(".app-sidebar");
    
    togglers.forEach(btn => {
        btn.addEventListener("click", () => {
            if (sidebar) {
                if (window.innerWidth < 992) {
                    sidebar.classList.toggle("show");
                } else {
                    sidebar.classList.toggle("collapsed");
                }
            }
        });
    });
}

function handleNotificationsBadge() {
    const user = getLoggedInUser();
    if (!user) return;
    const notifications = JSON.parse(localStorage.getItem("erp_notifications") || "[]");
    const unreadCount = notifications.filter(n => n.user_id === user.id && !n.is_read).length;
    
    const badges = document.querySelectorAll(".notif-badge");
    badges.forEach(badge => {
        if (unreadCount > 0) {
            badge.textContent = unreadCount;
            badge.style.display = "inline-block";
        } else {
            badge.style.display = "none";
        }
    });
}

// Dynamic dashboard loader for standard user (Intern)
function renderUserDashboard() {
    const user = checkAuthentication("user");
    if (!user) return;
    
    // Set Profile Summary Details
    document.getElementById("user-fullname").textContent = user.full_name || user.username;
    document.getElementById("user-track").textContent = user.track || "Not Assigned";
    document.getElementById("user-status").textContent = user.status;
    
    const statusBadge = document.getElementById("user-status");
    statusBadge.className = `badge-status status-${user.status}`;
    
    const avatarImg = document.getElementById("user-avatar");
    if (avatarImg && user.avatar) avatarImg.src = user.avatar;
    
    // Render logs count
    const files = JSON.parse(localStorage.getItem("erp_files") || "[]").filter(f => Number(f.user_id) === Number(user.id));
    const notifications = JSON.parse(localStorage.getItem("erp_notifications") || "[]").filter(n => n.user_id === user.id);
    
    document.getElementById("stat-files").textContent = files.length;
    document.getElementById("stat-notifications").textContent = notifications.length;
    
    // Draw dummy metrics graph using Chart.js
    const ctx = document.getElementById("userDashboardChart");
    if (ctx) {
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
                datasets: [{
                    label: 'Milestone Progress (%)',
                    data: [25, 50, 75, 100],
                    borderColor: '#00c853',
                    backgroundColor: 'rgba(0, 200, 83, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#64748b' } },
                    x: { grid: { display: false }, ticks: { color: '#64748b' } }
                }
            }
        });
    }
    
    // Render dynamic tables
    renderRecentActivities(user.id);
}
function renderRecentActivities(userId) {
    const logs = JSON.parse(localStorage.getItem("erp_logs") || "[]").filter(l => Number(l.user_id) === Number(userId));
    logs.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
    const tbody = document.getElementById("recent-activities-table");
    if (!tbody) return;
    
    tbody.innerHTML = "";
    if (logs.length === 0) {
        tbody.innerHTML = `<tr><td colspan="3" class="text-center text-muted">No recent activities found.</td></tr>`;
        return;
    }
    
    logs.slice(0, 5).forEach(log => {
        const tr = document.createElement("tr");
        const formattedDate = new Date(log.timestamp).toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' });
        tr.innerHTML = `
            <td>${log.action}</td>
            <td>${formattedDate}</td>
        `;
        tbody.appendChild(tr);
    });
}

let currentFilter = 'all';
let searchQuery = '';

// Dynamic dashboard loader for System Admin
function renderAdminDashboard() {
    checkAuthentication("admin");
    
    const users = JSON.parse(localStorage.getItem("erp_users") || "[]").filter(u => u.role !== "admin");
    const files = JSON.parse(localStorage.getItem("erp_files") || "[]");
    const logs = JSON.parse(localStorage.getItem("erp_logs") || "[]");
    
    document.getElementById("admin-stat-interns").textContent = users.length;
    document.getElementById("admin-stat-pending").textContent = users.filter(u => u.status === "pending").length;
    document.getElementById("admin-stat-uploads").textContent = files.length;
    document.getElementById("admin-stat-logs").textContent = logs.length;
    
    // Admin charts
    const ctx = document.getElementById("adminCohortChart");
    if (ctx) {
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Software Eng', 'UI/UX Design', 'Data Analytics'],
                datasets: [{
                    label: 'Intern Count',
                    data: [
                        users.filter(u => u.track === 'Software Engineering').length,
                        users.filter(u => u.track === 'UI/UX Design').length,
                        users.filter(u => u.track === 'Data Analytics').length
                    ],
                    backgroundColor: ['#00c853', '#69f0ae', '#00e676'],
                    borderRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#64748b' } },
                    x: { grid: { display: false }, ticks: { color: '#64748b' } }
                }
            }
        });
    }
    
    renderRecentUsers();
}

function renderRecentUsers() {
    const users = JSON.parse(localStorage.getItem("erp_users") || "[]")
        .filter(u => u.role !== "admin" && u.status === "pending");
    const tbody = document.getElementById("recent-users-table");
    if (!tbody) return;
    
    tbody.innerHTML = "";
    
    const statPending = document.getElementById("admin-stat-pending");
    if (statPending) {
        statPending.textContent = users.length;
    }
    
    if (users.length === 0) {
        tbody.innerHTML = `<tr><td colspan="4" class="text-center text-muted py-4">No pending candidate applications.</td></tr>`;
        return;
    }
    
    users.slice(0, 5).forEach(u => {
        const tr = document.createElement("tr");
        tr.style.transition = "all 0.3s ease";
        tr.innerHTML = `
            <td>
                <div class="d-flex align-items-center gap-3">
                    <img src="${u.avatar}" class="rounded-circle" width="36" height="36" alt="">
                    <div>
                        <div class="fw-bold text-white">${u.full_name || u.username}</div>
                        <div class="small text-secondary">${u.email}</div>
                    </div>
                </div>
            </td>
            <td>${u.track || "N/A"}</td>
            <td><span class="badge-status status-${u.status}">${u.status}</span></td>
            <td>
                <button class="btn btn-sm btn-success me-2" onclick="changeUserStatus(${u.id}, 'approved')">Approve</button>
                <button class="btn btn-sm btn-danger" onclick="changeUserStatus(${u.id}, 'rejected')">Reject</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

// Global user management helpers
window.changeUserStatus = function(userId, newStatus) {
    // Optimistic UI updates
    let users = JSON.parse(localStorage.getItem("erp_users") || "[]");
    const userIndex = users.findIndex(u => u.id === userId);
    if (userIndex !== -1) {
        users[userIndex].status = newStatus;
        localStorage.setItem("erp_users", JSON.stringify(users));
        
        if (window.location.pathname.includes("admin-dashboard.html") || window.location.pathname.endsWith("/admin-dashboard/")) {
            renderAdminDashboard();
        } else if (window.location.pathname.includes("user-management.html") || window.location.pathname.endsWith("/user-management/")) {
            renderUserManagement();
        }
    }
    
    fetch("/erp/admin/api/users/action/", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            user_id: userId,
            action: newStatus === 'approved' ? 'approve' : 'reject'
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            showToast(data.message, "success");
        } else {
            showToast(data.message || "Failed to update user status", "danger");
        }
    })
    .catch(err => {
        showToast("Error updating user status on server.", "danger");
        console.error(err);
    });
};

window.toggleAccountStatus = function(userId, currentIsActive) {
    const action = currentIsActive ? 'disable' : 'enable';
    
    // Optimistic UI update
    const users = JSON.parse(localStorage.getItem("erp_users") || "[]");
    const idx = users.findIndex(usr => usr.id === userId);
    if (idx !== -1) {
        users[idx].is_active = !currentIsActive;
        localStorage.setItem("erp_users", JSON.stringify(users));
        renderUserManagement();
    }
    
    fetch("/erp/admin/api/users/action/", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            user_id: userId,
            action: action
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            showToast(data.message, "success");
        } else {
            showToast(data.message || "Failed to update account status", "danger");
        }
    })
    .catch(err => {
        showToast("Error updating status on server.", "danger");
        console.error(err);
    });
};

window.resetPasswordModal = function(userId) {
    const users = JSON.parse(localStorage.getItem("erp_users") || "[]");
    const u = users.find(usr => usr.id === userId);
    if (!u) return;
    
    const targetName = u.full_name || u.username;
    
    const modalHtml = `
        <div class="modal fade show d-block" id="resetPasswordModal" tabindex="-1" style="background: rgba(0,0,0,0.6); backdrop-filter: blur(5px); z-index: 1050;">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content glass-panel p-4" style="border: 1px solid var(--card-hover-border)">
                    <div class="modal-header border-0 pb-0">
                        <h4 class="modal-title text-white fw-bold">Reset Password</h4>
                        <button type="button" class="btn-close btn-close-white" onclick="document.getElementById('resetPasswordModal').remove()"></button>
                    </div>
                    <div class="modal-body py-3">
                        <p class="text-secondary small">Set a new password for candidate <strong>${targetName}</strong>.</p>
                        <form id="resetPasswordForm">
                            <div class="mb-3">
                                <label class="form-label text-secondary small">New Password</label>
                                <input type="password" class="form-control form-control-premium" id="m-new-password" required minlength="6" placeholder="At least 6 characters">
                            </div>
                            <div class="text-end">
                                <button type="button" class="btn btn-secondary-premium btn-sm me-2" onclick="document.getElementById('resetPasswordModal').remove()">Cancel</button>
                                <button type="submit" class="btn btn-premium btn-sm">Reset Password</button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    document.getElementById("resetPasswordForm").addEventListener("submit", (e) => {
        e.preventDefault();
        const newPassword = document.getElementById("m-new-password").value;
        
        fetch("/erp/admin/api/users/action/", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                user_id: userId,
                action: 'reset_password',
                password: newPassword
            })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                showToast(data.message, "success");
                document.getElementById('resetPasswordModal').remove();
            } else {
                showToast(data.message || "Failed to reset password", "danger");
            }
        })
        .catch(err => {
            showToast("Error resetting password on server.", "danger");
            console.error(err);
        });
    });
};

window.createNewUserModal = function() {
    const modalHtml = `
        <div class="modal fade show d-block" id="createUserModal" tabindex="-1" style="background: rgba(0,0,0,0.6); backdrop-filter: blur(5px); z-index: 1050;">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content glass-panel p-4" style="border: 1px solid var(--card-hover-border)">
                    <div class="modal-header border-0 pb-0">
                        <h4 class="modal-title text-white fw-bold">Create Candidate Profile</h4>
                        <button type="button" class="btn-close btn-close-white" onclick="document.getElementById('createUserModal').remove()"></button>
                    </div>
                    <div class="modal-body py-3">
                        <form id="createUserForm">
                            <div class="mb-3">
                                <label class="form-label text-secondary small">Username</label>
                                <input type="text" class="form-control form-control-premium" id="c-username" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label text-secondary small">Email</label>
                                <input type="email" class="form-control form-control-premium" id="c-email" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label text-secondary small">Full Name</label>
                                <input type="text" class="form-control form-control-premium" id="c-fullname" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label text-secondary small">Track</label>
                                <select class="form-select form-control-premium" id="c-track" required>
                                    <option value="Software Engineering">Software Engineering</option>
                                    <option value="UI/UX Design">UI/UX Design</option>
                                    <option value="Data Analytics">Data Analytics</option>
                                </select>
                            </div>
                            <div class="text-end">
                                <button type="button" class="btn btn-secondary-premium btn-sm me-2" onclick="document.getElementById('createUserModal').remove()">Cancel</button>
                                <button type="submit" class="btn btn-premium btn-sm">Add User</button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    document.getElementById("createUserForm").addEventListener("submit", (e) => {
        e.preventDefault();
        const uname = document.getElementById("c-username").value.trim().toLowerCase();
        const email = document.getElementById("c-email").value.trim();
        const fname = document.getElementById("c-fullname").value.trim();
        const track = document.getElementById("c-track").value;
        
        fetch("/erp/admin/api/users/action/", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                action: 'create',
                username: uname,
                email: email,
                fullname: fname,
                track: track
            })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                showToast(data.message, "success");
                document.getElementById('createUserModal').remove();
                
                const users = JSON.parse(localStorage.getItem("erp_users") || "[]");
                users.push({
                    id: users.length + 1000,
                    username: uname,
                    email: email,
                    role: "user",
                    track: track,
                    status: "pending",
                    full_name: fname,
                    is_active: true,
                    completion_percentage: 42,
                    avatar: "/media/profile_pictures/default-avatar.png",
                    date_joined: new Date().toISOString(),
                    last_login: ""
                });
                localStorage.setItem("erp_users", JSON.stringify(users));
                renderUserManagement();
            } else {
                showToast(data.message || "Failed to create candidate", "danger");
            }
        })
        .catch(err => {
            showToast("Error creating candidate on server.", "danger");
            console.error(err);
        });
    });
};

// Render dynamic User CRUD List (Admin Panel)
function renderUserManagement() {
    checkAuthentication("admin");
    const tbody = document.getElementById("users-list");
    if (!tbody) return;
    
    let users = JSON.parse(localStorage.getItem("erp_users") || "[]").filter(u => u.role !== "admin");
    
    // Filters
    if (currentFilter === 'pending') {
        users = users.filter(u => u.status === 'pending');
    } else if (currentFilter === 'approved') {
        users = users.filter(u => u.status === 'approved');
    } else if (currentFilter === 'rejected') {
        users = users.filter(u => u.status === 'rejected');
    } else if (currentFilter === 'active') {
        users = users.filter(u => u.is_active === true);
    } else if (currentFilter === 'disabled') {
        users = users.filter(u => u.is_active === false);
    }
    
    // Search
    if (searchQuery) {
        users = users.filter(u => {
            const name = (u.full_name || '').toLowerCase();
            const email = (u.email || '').toLowerCase();
            const track = (u.track || '').toLowerCase();
            const role = (u.role || '').toLowerCase();
            const status = (u.status || '').toLowerCase();
            const completion = (u.completion_percentage !== undefined ? u.completion_percentage.toString() : '42');
            
            return name.includes(searchQuery) ||
                   email.includes(searchQuery) ||
                   track.includes(searchQuery) ||
                   role.includes(searchQuery) ||
                   status.includes(searchQuery) ||
                   completion.includes(searchQuery);
        });
    }
    
    tbody.innerHTML = "";
    if (users.length === 0) {
        tbody.innerHTML = `<tr><td colspan="11" class="text-center text-muted py-4">No matching records found in database.</td></tr>`;
        return;
    }
    
    users.forEach(u => {
        const tr = document.createElement("tr");
        const dateJoined = u.date_joined ? new Date(u.date_joined).toLocaleDateString() : 'N/A';
        const lastLogin = u.last_login ? new Date(u.last_login).toLocaleDateString() : 'Never';
        const completionVal = u.completion_percentage !== undefined ? u.completion_percentage : 42;
        
        const activeBadge = u.is_active ? 
            `<span class="badge bg-success-bg text-success border border-success" style="font-size:0.75rem; padding:4px 8px;">Active</span>` :
            `<span class="badge bg-danger-bg text-danger border border-danger" style="font-size:0.75rem; padding:4px 8px;">Disabled</span>`;
            
        tr.innerHTML = `
            <td>${u.id}</td>
            <td>
                <div class="d-flex align-items-center gap-3">
                    <img src="${u.avatar}" class="rounded-circle border border-secondary" width="36" height="36" alt="">
                    <div class="fw-bold text-white">${u.full_name || u.username}</div>
                </div>
            </td>
            <td><span class="small text-secondary">${u.email}</span></td>
            <td><span class="badge bg-secondary" style="font-size:0.7rem;">${u.role.toUpperCase()}</span></td>
            <td><span class="small text-white">${u.track || 'Not Assigned'}</span></td>
            <td><span class="badge-status status-${u.status}">${u.status}</span></td>
            <td>${activeBadge}</td>
            <td><span class="small text-secondary">${dateJoined}</span></td>
            <td><span class="small text-secondary">${lastLogin}</span></td>
            <td>
                <div class="d-flex align-items-center gap-2">
                    <span class="small text-white fw-bold">${completionVal}%</span>
                    <div class="progress-premium" style="width: 60px; height: 6px;">
                        <div class="progress-bar" style="width: ${completionVal}%;"></div>
                    </div>
                </div>
            </td>
            <td>
                <div class="d-flex align-items-center gap-2">
                    <div class="status-action-btns">
                        ${u.status === 'pending' ? `
                            <div class="d-flex align-items-center gap-1">
                                <button class="btn btn-success btn-sm py-1 px-2" onclick="changeUserStatus(${u.id}, 'approved')" title="Approve Candidate"><i class="bi bi-check-lg"></i> Approve</button>
                                <button class="btn btn-danger btn-sm py-1 px-2" onclick="changeUserStatus(${u.id}, 'rejected')" title="Reject Candidate"><i class="bi bi-x-lg"></i> Reject</button>
                            </div>
                        ` : u.status === 'approved' ? `
                            <div class="d-flex align-items-center gap-1">
                                <span class="badge bg-success-bg text-success border border-success py-1 px-2" style="font-size:0.75rem;"><i class="bi bi-check-circle-fill"></i> Approved</span>
                                <button class="btn btn-outline-danger btn-sm py-1 px-2" onclick="changeUserStatus(${u.id}, 'rejected')" title="Change to Rejected" style="border-color: rgba(244, 63, 94, 0.4); color: #f43f5e;"><i class="bi bi-x-lg"></i></button>
                            </div>
                        ` : `
                            <div class="d-flex align-items-center gap-1">
                                <span class="badge bg-danger-bg text-danger border border-danger py-1 px-2" style="font-size:0.75rem;"><i class="bi bi-x-circle-fill"></i> Rejected</span>
                                <button class="btn btn-outline-success btn-sm py-1 px-2" onclick="changeUserStatus(${u.id}, 'approved')" title="Change to Approved" style="border-color: rgba(0, 230, 118, 0.4); color: #00e676;"><i class="bi bi-check-lg"></i></button>
                            </div>
                        `}
                    </div>
                    <div class="dropdown">
                        <button class="btn btn-secondary-premium btn-sm dropdown-toggle py-1 px-2" type="button" data-bs-toggle="dropdown" aria-expanded="false">
                            Options
                        </button>
                        <ul class="dropdown-menu dropdown-menu-dark glass-panel" style="border:1px solid var(--card-border);">
                            <li><a class="dropdown-item" href="#" onclick="editUserModal(${u.id})"><i class="bi bi-pencil me-2 text-primary"></i> Edit User</a></li>
                            <li><a class="dropdown-item" href="#" onclick="toggleAccountStatus(${u.id}, ${u.is_active})"><i class="bi ${u.is_active ? 'bi-shield-slash-fill text-warning' : 'bi-shield-fill-check text-success'} me-2"></i> ${u.is_active ? 'Disable Account' : 'Enable Account'}</a></li>
                            <li><a class="dropdown-item" href="#" onclick="resetPasswordModal(${u.id})"><i class="bi bi-key-fill me-2 text-info"></i> Reset Password</a></li>
                            <hr class="dropdown-divider border-secondary">
                            <li><a class="dropdown-item" href="#" onclick="viewUserDetailsModal(${u.id}, 'profile')"><i class="bi bi-person-fill me-2"></i> View Profile</a></li>
                            <li><a class="dropdown-item" href="#" onclick="viewUserDetailsModal(${u.id}, 'uploads')"><i class="bi bi-file-earmark-arrow-up-fill me-2"></i> View Uploads</a></li>
                            <li><a class="dropdown-item" href="#" onclick="viewUserDetailsModal(${u.id}, 'reports')"><i class="bi bi-file-earmark-bar-graph-fill me-2"></i> View Reports</a></li>
                            <li><a class="dropdown-item" href="#" onclick="viewUserDetailsModal(${u.id}, 'notifications')"><i class="bi bi-bell-fill me-2"></i> View Notifications</a></li>
                            <hr class="dropdown-divider border-secondary">
                            <li><a class="dropdown-item" href="#" onclick="deleteUser(${u.id})"><i class="bi bi-trash-fill me-2 text-danger"></i> Delete User</a></li>
                        </ul>
                    </div>
                </div>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

// Admin CRUD functions
window.deleteUser = function(userId) {
    const users = JSON.parse(localStorage.getItem("erp_users") || "[]");
    const u = users.find(usr => usr.id === userId);
    if (!u) return;
    
    const targetName = u.full_name || u.username;
    
    const modalHtml = `
        <div class="modal fade show d-block" id="deleteConfirmModal" tabindex="-1" style="background: rgba(0,0,0,0.6); backdrop-filter: blur(5px); z-index: 1060;">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content glass-panel p-4" style="border: 1px solid var(--danger);">
                    <div class="modal-header border-0 pb-0">
                        <h4 class="modal-title text-danger fw-bold"><i class="bi bi-exclamation-triangle-fill me-2"></i> Delete User?</h4>
                        <button type="button" class="btn-close btn-close-white" onclick="document.getElementById('deleteConfirmModal').remove()"></button>
                    </div>
                    <div class="modal-body py-3">
                        <p class="text-white">Are you sure you want to permanently remove <strong>${targetName}</strong>?</p>
                        <p class="text-secondary small">This action cannot be undone. This will delete their profile, files, notifications, active sessions, and invalidate login credentials.</p>
                    </div>
                    <div class="modal-footer border-0 pt-0 justify-content-end">
                        <button type="button" class="btn btn-secondary-premium btn-sm me-2" onclick="document.getElementById('deleteConfirmModal').remove()">Cancel</button>
                        <button type="button" class="btn btn-danger btn-sm" id="confirm-delete-btn">Delete User</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    document.getElementById("confirm-delete-btn").addEventListener("click", () => {
        let usersList = JSON.parse(localStorage.getItem("erp_users") || "[]");
        usersList = usersList.filter(usr => usr.id !== userId);
        localStorage.setItem("erp_users", JSON.stringify(usersList));
        
        document.getElementById('deleteConfirmModal').remove();
        
        if (window.location.pathname.includes("user-management.html") || window.location.pathname.endsWith("/user-management/")) {
            renderUserManagement();
        } else if (window.location.pathname.includes("admin-dashboard.html") || window.location.pathname.endsWith("/admin-dashboard/")) {
            renderAdminDashboard();
        }
        
        fetch("/erp/admin/api/users/delete/", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ user_id: userId })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                showToast(data.message, "success");
            } else {
                showToast(data.message || "Failed to delete user", "danger");
            }
        })
        .catch(err => {
            showToast("Error executing deletion on server.", "danger");
            console.error(err);
        });
    });
};

window.viewUserDetailsModal = function(userId, activeTab = 'profile') {
    fetch(`/erp/admin/api/users/${userId}/details/`)
        .then(res => res.json())
        .then(data => {
            if (!data.success) {
                showToast(data.message || "Failed to fetch user details", "danger");
                return;
            }
            
            const u = data.user;
            const files = data.files || [];
            const notifications = data.notifications || [];
            const logs = data.logs || [];
            const reports = data.reports || [];
            
            const modalHtml = `
                <div class="modal fade show d-block" id="userDetailsModal" tabindex="-1" style="background: rgba(0,0,0,0.6); backdrop-filter: blur(5px); z-index: 1050;">
                    <div class="modal-dialog modal-dialog-centered modal-lg">
                        <div class="modal-content glass-panel p-4" style="border: 1px solid var(--card-hover-border);">
                            <div class="modal-header border-0 pb-2">
                                <h4 class="modal-title text-white fw-bold"><i class="bi bi-person-circle text-primary me-2"></i> Candidate Workspace</h4>
                                <button type="button" class="btn-close btn-close-white" onclick="document.getElementById('userDetailsModal').remove()"></button>
                            </div>
                            <div class="modal-body pt-1">
                                <ul class="nav nav-tabs border-secondary mb-3" id="detailsTab" role="tablist">
                                    <li class="nav-item">
                                        <button class="nav-link text-white bg-transparent border-0 py-2 px-3 ${activeTab === 'profile' ? 'active border-bottom border-primary fw-bold text-primary' : 'text-secondary'}" onclick="switchDetailsTab('profile')">Profile</button>
                                    </li>
                                    <li class="nav-item">
                                        <button class="nav-link text-white bg-transparent border-0 py-2 px-3 ${activeTab === 'uploads' ? 'active border-bottom border-primary fw-bold text-primary' : 'text-secondary'}" onclick="switchDetailsTab('uploads')">Uploads (${files.length})</button>
                                    </li>
                                    <li class="nav-item">
                                        <button class="nav-link text-white bg-transparent border-0 py-2 px-3 ${activeTab === 'notifications' ? 'active border-bottom border-primary fw-bold text-primary' : 'text-secondary'}" onclick="switchDetailsTab('notifications')">Notifications (${notifications.length})</button>
                                    </li>
                                    <li class="nav-item">
                                        <button class="nav-link text-white bg-transparent border-0 py-2 px-3 ${activeTab === 'reports' ? 'active border-bottom border-primary fw-bold text-primary' : 'text-secondary'}" onclick="switchDetailsTab('reports')">Reports (${reports.length})</button>
                                    </li>
                                    <li class="nav-item">
                                        <button class="nav-link text-white bg-transparent border-0 py-2 px-3 ${activeTab === 'logs' ? 'active border-bottom border-primary fw-bold text-primary' : 'text-secondary'}" onclick="switchDetailsTab('logs')">System Logs (${logs.length})</button>
                                    </li>
                                </ul>
                                
                                <div class="tab-content text-white" id="detailsTabContent" style="max-height: 400px; overflow-y: auto;">
                                    <div class="tab-pane fade ${activeTab === 'profile' ? 'show active' : ''}" id="details-profile">
                                        <div class="d-flex align-items-center gap-4 mb-4">
                                            <img src="${u.avatar}" class="rounded-circle border border-primary border-3" width="90" height="90">
                                            <div>
                                                <h3 class="fw-bold mb-0 text-white">${u.full_name || u.username}</h3>
                                                <div class="text-secondary small mb-2">${u.email}</div>
                                                <span class="badge bg-secondary me-2">Role: ${u.role.toUpperCase()}</span>
                                                <span class="badge-status status-${u.status}">Application: ${u.status.toUpperCase()}</span>
                                            </div>
                                        </div>
                                        
                                        <div class="row g-3">
                                            <div class="col-md-6">
                                                <div class="p-3 bg-tertiary rounded">
                                                    <div class="text-secondary small">Internship Track</div>
                                                    <div class="fw-bold text-white">${u.track || 'N/A'}</div>
                                                </div>
                                            </div>
                                            <div class="col-md-6">
                                                <div class="p-3 bg-tertiary rounded">
                                                    <div class="text-secondary small">Academic Background</div>
                                                    <div class="fw-bold text-white">${u.academic || 'N/A'}</div>
                                                </div>
                                            </div>
                                            <div class="col-md-6">
                                                <div class="p-3 bg-tertiary rounded">
                                                    <div class="text-secondary small">Phone Number</div>
                                                    <div class="fw-bold text-white">${u.phone || 'N/A'}</div>
                                                </div>
                                            </div>
                                            <div class="col-md-6">
                                                <div class="p-3 bg-tertiary rounded">
                                                    <div class="text-secondary small">Skills Specialization</div>
                                                    <div class="fw-bold text-white text-truncate">${u.skills || 'N/A'}</div>
                                                </div>
                                            </div>
                                            <div class="col-12">
                                                <div class="p-3 bg-tertiary rounded">
                                                    <div class="text-secondary small">Biographical Summary</div>
                                                    <div class="text-white small" style="white-space: pre-line;">${u.bio || 'No bio provided.'}</div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                    
                                    <div class="tab-pane fade ${activeTab === 'uploads' ? 'show active' : ''}" id="details-uploads">
                                        <div class="table-responsive">
                                            <table class="table table-dark table-hover mb-0">
                                                <thead>
                                                    <tr>
                                                        <th>File Name</th>
                                                        <th>Size</th>
                                                        <th>Uploaded At</th>
                                                        <th>Action</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    ${files.length === 0 ? '<tr><td colspan="4" class="text-center text-secondary small py-4">No uploaded files.</td></tr>' : files.map(f => `
                                                        <tr>
                                                            <td><i class="bi bi-file-earmark-arrow-up text-primary me-2"></i> ${f.name}</td>
                                                            <td>${(f.size / 1024).toFixed(1)} KB</td>
                                                            <td>${new Date(f.uploaded_at).toLocaleDateString()}</td>
                                                            <td><a href="${f.url}" download class="btn btn-sm btn-outline-primary py-0 px-2"><i class="bi bi-download"></i></a></td>
                                                        </tr>
                                                    `).join('')}
                                                </tbody>
                                            </table>
                                        </div>
                                    </div>
                                    
                                    <div class="tab-pane fade ${activeTab === 'notifications' ? 'show active' : ''}" id="details-notifications">
                                        <div class="d-flex flex-column gap-2">
                                            ${notifications.length === 0 ? '<div class="text-center text-secondary small py-4">No notifications recorded.</div>' : notifications.map(n => `
                                                <div class="p-3 bg-tertiary rounded border-start border-3 ${n.level === 'success' ? 'border-success' : n.level === 'warning' ? 'border-warning' : n.level === 'danger' ? 'border-danger' : 'border-info'}">
                                                    <div class="d-flex justify-content-between">
                                                        <strong class="text-white">${n.title}</strong>
                                                        <span class="text-secondary" style="font-size: 0.75rem;">${new Date(n.created_at).toLocaleString()}</span>
                                                    </div>
                                                    <p class="mb-0 text-secondary small mt-1">${n.message}</p>
                                                </div>
                                            `).join('')}
                                        </div>
                                    </div>
                                    
                                    <div class="tab-pane fade ${activeTab === 'reports' ? 'show active' : ''}" id="details-reports">
                                        <div class="table-responsive">
                                            <table class="table table-dark table-hover mb-0">
                                                <thead>
                                                    <tr>
                                                        <th>Report Name</th>
                                                        <th>Description</th>
                                                        <th>Date Generated</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    ${reports.length === 0 ? '<tr><td colspan="3" class="text-center text-secondary small py-4">No reports assigned.</td></tr>' : reports.map(r => `
                                                        <tr>
                                                            <td><i class="bi bi-file-pdf text-danger me-2"></i> ${r.title}</td>
                                                            <td>${r.description}</td>
                                                            <td>${new Date(r.created_at).toLocaleDateString()}</td>
                                                        </tr>
                                                    `).join('')}
                                                </tbody>
                                            </table>
                                        </div>
                                    </div>
                                    
                                    <div class="tab-pane fade ${activeTab === 'logs' ? 'show active' : ''}" id="details-logs">
                                        <div class="table-responsive">
                                            <table class="table table-dark table-hover mb-0" style="font-size: 0.85rem;">
                                                <thead>
                                                    <tr>
                                                        <th>Action Triggered</th>
                                                        <th>IP Connection</th>
                                                        <th>Timestamp</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    ${logs.length === 0 ? '<tr><td colspan="3" class="text-center text-secondary small py-4">No activity logged.</td></tr>' : logs.map(l => `
                                                        <tr>
                                                            <td>${l.action}</td>
                                                            <td>${l.ip_address}</td>
                                                            <td>${new Date(l.timestamp).toLocaleString()}</td>
                                                        </tr>
                                                    `).join('')}
                                                </tbody>
                                            </table>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            document.body.insertAdjacentHTML('beforeend', modalHtml);
            
            window.switchDetailsTab = function(tabName) {
                document.querySelectorAll('#detailsTab button').forEach(btn => {
                    btn.className = 'nav-link text-white bg-transparent border-0 py-2 px-3 text-secondary';
                });
                
                const selBtn = Array.from(document.querySelectorAll('#detailsTab button'))
                    .find(btn => btn.getAttribute('onclick').includes(`'${tabName}'`));
                if (selBtn) {
                    selBtn.className = 'nav-link text-white bg-transparent border-0 py-2 px-3 active border-bottom border-primary fw-bold text-primary';
                }
                
                document.querySelectorAll('#detailsTabContent > div').forEach(pane => {
                    pane.classList.remove('show', 'active');
                });
                
                const pane = document.getElementById(`details-${tabName}`);
                if (pane) {
                    pane.classList.add('show', 'active');
                }
            };
        })
        .catch(err => {
            showToast("Failed to fetch candidate details.", "danger");
            console.error(err);
        });
};

window.editUserModal = function(userId) {
    const users = JSON.parse(localStorage.getItem("erp_users") || "[]");
    const u = users.find(usr => usr.id === userId);
    if (!u) return;
    
    const modalHtml = `
        <div class="modal fade show d-block" id="editUserModal" tabindex="-1" style="background: rgba(0,0,0,0.6); backdrop-filter: blur(5px); z-index: 1050;">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content glass-panel p-4" style="border: 1px solid var(--card-hover-border)">
                    <div class="modal-header border-0 pb-0">
                        <h4 class="modal-title text-white">Edit User (#${u.id})</h4>
                        <button type="button" class="btn-close btn-close-white" onclick="document.getElementById('editUserModal').remove()"></button>
                    </div>
                    <div class="modal-body">
                        <form id="editUserAdminForm">
                            <div class="mb-3">
                                <label class="form-label text-secondary small">Username</label>
                                <input type="text" class="form-control form-control-premium" id="m-username" value="${u.username || ''}" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label text-secondary small">Email</label>
                                <input type="email" class="form-control form-control-premium" id="m-email" value="${u.email || ''}" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label text-secondary small">Full Name</label>
                                <input type="text" class="form-control form-control-premium" id="m-fullname" value="${u.full_name || ''}">
                            </div>
                            <div class="mb-3">
                                <label class="form-label text-secondary small">Track</label>
                                <select class="form-select form-control-premium" id="m-track">
                                    <option value="" ${!u.track ? 'selected' : ''}>Not Assigned</option>
                                    <option value="Software Engineering" ${u.track === 'Software Engineering' ? 'selected' : ''}>Software Engineering</option>
                                    <option value="UI/UX Design" ${u.track === 'UI/UX Design' ? 'selected' : ''}>UI/UX Design</option>
                                    <option value="Data Analytics" ${u.track === 'Data Analytics' ? 'selected' : ''}>Data Analytics</option>
                                </select>
                            </div>
                            <div class="mb-3">
                                <label class="form-label text-secondary small">Role</label>
                                <select class="form-select form-control-premium" id="m-role">
                                    <option value="user" ${u.role === 'user' ? 'selected' : ''}>Intern/Candidate</option>
                                    <option value="admin" ${u.role === 'admin' ? 'selected' : ''}>Administrator</option>
                                </select>
                            </div>
                            <div class="mb-3">
                                <label class="form-label text-secondary small">Application Status</label>
                                <select class="form-select form-control-premium" id="m-status">
                                    <option value="pending" ${u.status === 'pending' ? 'selected' : ''}>Pending</option>
                                    <option value="approved" ${u.status === 'approved' ? 'selected' : ''}>Approved</option>
                                    <option value="rejected" ${u.status === 'rejected' ? 'selected' : ''}>Rejected</option>
                                </select>
                            </div>
                            <div class="mb-3">
                                <label class="form-label text-secondary small">Completion %</label>
                                <input type="number" class="form-control form-control-premium" id="m-completion" value="${u.completion_percentage !== undefined ? u.completion_percentage : 42}" min="0" max="100">
                            </div>
                            <div class="text-end">
                                <button type="button" class="btn btn-secondary-premium me-2" onclick="document.getElementById('editUserModal').remove()">Cancel</button>
                                <button type="submit" class="btn btn-premium">Save Changes</button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    document.getElementById("editUserAdminForm").addEventListener("submit", (e) => {
        e.preventDefault();
        const username = document.getElementById("m-username").value.trim();
        const email = document.getElementById("m-email").value.trim();
        const fullname = document.getElementById("m-fullname").value.trim();
        const track = document.getElementById("m-track").value;
        const role = document.getElementById("m-role").value;
        const status = document.getElementById("m-status").value;
        const completion = document.getElementById("m-completion").value;
        
        // Optimistic UI updates
        const usersList = JSON.parse(localStorage.getItem("erp_users") || "[]");
        const idx = usersList.findIndex(usr => usr.id === u.id);
        if (idx !== -1) {
            usersList[idx].username = username;
            usersList[idx].email = email;
            usersList[idx].full_name = fullname;
            usersList[idx].track = track;
            usersList[idx].role = role;
            usersList[idx].status = status;
            usersList[idx].completion_percentage = parseInt(completion);
            localStorage.setItem("erp_users", JSON.stringify(usersList));
            
            document.getElementById('editUserModal').remove();
            renderUserManagement();
        }
        
        fetch("/erp/admin/api/users/action/", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                user_id: u.id,
                action: 'edit',
                username: username,
                email: email,
                fullname: fullname,
                track: track,
                role: role,
                status: status,
                completion_percentage: completion
            })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                showToast(data.message, "success");
            } else {
                showToast(data.message || "Failed to edit user", "danger");
            }
        })
        .catch(err => {
            showToast("Error updating user details on server.", "danger");
            console.error(err);
        });
    });
};

// Setup dynamic file uploader drag & drop
function setupFileUploader() {
    const user = getLoggedInUser();
    if (!user) return;
    
    const dropZone = document.getElementById("drop-zone");
    const fileInput = document.getElementById("file-input");
    const tableBody = document.getElementById("uploaded-files-table");
    
    if (dropZone) {
        dropZone.addEventListener("click", () => fileInput.click());
        
        dropZone.addEventListener("dragover", (e) => {
            e.preventDefault();
            dropZone.classList.add("dragover");
        });
        
        dropZone.addEventListener("dragleave", () => {
            dropZone.classList.remove("dragover");
        });
        
        dropZone.addEventListener("drop", (e) => {
            e.preventDefault();
            dropZone.classList.remove("dragover");
            const files = e.dataTransfer.files;
            handleFilesUpload(files, user.id);
        });
        
        fileInput.addEventListener("change", () => {
            handleFilesUpload(fileInput.files, user.id);
        });
    }
    
    renderFilesList(user.id);
}

function handleFilesUpload(filesList, userId) {
    if (filesList.length === 0) return;
    
    const allowedTypes = ["pdf", "docx", "zip", "png", "jpg", "jpeg"];
    const progressContainer = document.getElementById("progress-container");
    const progressBar = document.getElementById("progress-bar");
    const uploadPercent = document.getElementById("upload-percent");
    const uploadStatusText = document.getElementById("upload-status-text");

    for (let i = 0; i < filesList.length; i++) {
        const file = filesList[i];
        const ext = file.name.split(".").pop().toLowerCase();
        
        if (!allowedTypes.includes(ext)) {
            showToast(`Extension .${ext} is not allowed. Upload PDF, DOCX, ZIP, or Images.`, "danger");
            continue;
        }
        
        if (file.size > 10485760) {
            showToast(`File ${file.name} is too large. Limit is 10MB.`, "danger");
            continue;
        }
        
        // Show progress UI if present
        if (progressContainer) {
            progressContainer.style.display = "block";
            progressBar.style.width = "0%";
            uploadPercent.textContent = "0%";
            uploadStatusText.textContent = `Uploading ${file.name}...`;
        }
        
        const xhr = new XMLHttpRequest();
        xhr.open("POST", "/erp/upload-files/");
        xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
        
        xhr.upload.addEventListener("progress", (e) => {
            if (e.lengthComputable && progressBar && uploadPercent) {
                const percent = Math.round((e.loaded / e.total) * 100);
                progressBar.style.width = percent + "%";
                uploadPercent.textContent = percent + "%";
            }
        });
        
        xhr.addEventListener("load", () => {
            if (progressContainer) progressContainer.style.display = "none";
            try {
                const data = JSON.parse(xhr.responseText);
                if (data.success) {
                    showToast(`File ${file.name} uploaded successfully!`, "success");
                    window.addActivityLog(userId, `Uploaded document ${file.name}`);
                    
                    const localFiles = JSON.parse(localStorage.getItem("erp_files") || "[]");
                    localFiles.push(data.file);
                    localStorage.setItem("erp_files", JSON.stringify(localFiles));
                    
                    renderFilesList(userId);
                } else {
                    showToast(data.message || "Failed to upload file", "danger");
                }
            } catch (err) {
                showToast("Failed to process upload response", "danger");
            }
        });
        
        xhr.addEventListener("error", () => {
            if (progressContainer) progressContainer.style.display = "none";
            showToast("Network error during file upload", "danger");
        });
        
        const formData = new FormData();
        formData.append("file", file);
        xhr.send(formData);
    }
}

function renderFilesList(userId) {
    const tableBody = document.getElementById("uploaded-files-table");
    if (!tableBody) return;
    
    const files = JSON.parse(localStorage.getItem("erp_files") || "[]").filter(f => Number(f.user_id) === Number(userId));
    tableBody.innerHTML = "";
    
    if (files.length === 0) {
        tableBody.innerHTML = `<tr><td colspan="4" class="text-center text-muted">No files uploaded.</td></tr>`;
        return;
    }
    
    files.forEach(f => {
        const tr = document.createElement("tr");
        const formattedSize = (f.file_size / (1024 * 1024)).toFixed(2) + " MB";
        const formattedDate = new Date(f.uploaded_at).toLocaleDateString();
        
        let iconClass = "bi-file-earmark-image text-info";
        if (f.file_type === 'pdf') iconClass = "bi-filetype-pdf text-danger";
        else if (f.file_type === 'zip') iconClass = "bi-file-zip text-warning";
        else if (f.file_type === 'docx') iconClass = "bi-filetype-docx text-primary";
        
        tr.innerHTML = `
            <td>
                <div class="d-flex align-items-center gap-2">
                    <i class="bi ${iconClass} fs-5"></i>
                    <span class="text-white">${f.file_name}</span>
                </div>
            </td>
            <td>${formattedSize}</td>
            <td>${formattedDate}</td>
            <td>
                <a href="${f.file_url || '#'}" download class="btn btn-sm btn-outline-info me-2"><i class="bi bi-download"></i></a>
                <button class="btn btn-sm btn-outline-danger" onclick="deleteUserFile(${f.id}, ${userId})"><i class="bi bi-trash"></i></button>
            </td>
        `;
        tableBody.appendChild(tr);
    });
}

window.deleteUserFile = function(fileId, userId) {
    if (confirm("Are you sure you want to delete this file?")) {
        fetch(`/erp/delete-file/${fileId}/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": getCookie("csrftoken")
            }
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                let files = JSON.parse(localStorage.getItem("erp_files") || "[]");
                const file = files.find(f => f.id === fileId);
                files = files.filter(f => f.id !== fileId);
                localStorage.setItem("erp_files", JSON.stringify(files));
                
                if (file) window.addActivityLog(userId, `Deleted document ${file.file_name}`);
                showToast("File deleted", "success");
                renderFilesList(userId);
            } else {
                showToast(data.message || "Failed to delete file", "danger");
            }
        })
        .catch(err => {
            showToast("Error deleting file from server", "danger");
            console.error(err);
        });
    }
};

// Interactive Messenger Layout
// Interactive Messenger Layout
function setupMessagesSystem() {
    const user = getLoggedInUser();
    if (!user) return;
    
    const inboxList = document.getElementById("inbox-list");
    const chatWindow = document.getElementById("chat-window");
    const msgForm = document.getElementById("message-reply-form");
    
    if (inboxList) {
        renderInbox(user);
    }
    
    if (msgForm) {
        msgForm.addEventListener("submit", (e) => {
            e.preventDefault();
            const messageBody = document.getElementById("message-input").value;
            if (!messageBody.trim()) return;
            
            const chatType = chatWindow.dataset.chatType || "direct";
            const chatTarget = chatWindow.dataset.chatTarget || "1";
            
            const postData = {
                body: messageBody
            };
            if (chatType === "group") {
                postData.group_name = chatTarget;
            } else {
                postData.receiver_id = parseInt(chatTarget);
            }
            
            fetch("/erp/api/messages/send/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken")
                },
                body: JSON.stringify(postData)
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    const messages = JSON.parse(localStorage.getItem("erp_messages") || "[]");
                    messages.push(data.msg);
                    localStorage.setItem("erp_messages", JSON.stringify(messages));
                    document.getElementById("message-input").value = "";
                    renderChatHistory(user.id, chatType, chatTarget);
                    refreshSystemState();
                } else {
                    showToast(data.message || "Failed to send message", "danger");
                }
            })
            .catch(err => {
                showToast("Error communicating with server.", "danger");
                console.error(err);
            });
        });
    }
}

function renderInbox(currentUser, autoSelect = true) {
    const inboxList = document.getElementById("inbox-list");
    if (!inboxList) return;
    
    const users = JSON.parse(localStorage.getItem("erp_users") || "[]");
    const messages = JSON.parse(localStorage.getItem("erp_messages") || "[]");
    inboxList.innerHTML = "";
    
    // 1. Gather Group Chats
    let rawGroups = [];
    if (currentUser.role === "admin") {
        rawGroups = [
            { id: "all-cohort", name: "All Cohort Candidates", desc: "All candidate tracks", isGroup: true, avatarInitials: "AC" },
            { id: "Software Engineering", name: "Software Engineering Group", desc: "Software Engineering track Group Chat", isGroup: true, avatarInitials: "SE" },
            { id: "UI/UX Design", name: "UI/UX Design Group", desc: "UI/UX Design track Group Chat", isGroup: true, avatarInitials: "UX" },
            { id: "Data Analytics", name: "Data Analytics Group", desc: "Data Analytics track Group Chat", isGroup: true, avatarInitials: "DA" }
        ];
    } else {
        rawGroups = [
            { id: "all-cohort", name: "All Cohort Candidates", desc: "All candidate tracks", isGroup: true, avatarInitials: "AC" }
        ];
        const track = currentUser.track || "Software Engineering";
        let initials = "SE";
        if (track === "UI/UX Design") initials = "UX";
        if (track === "Data Analytics") initials = "DA";
        rawGroups.push({ id: track, name: `${track} Group`, desc: `${track} Group Chat`, isGroup: true, avatarInitials: initials });
    }
    
    // Process Groups
    const groupItems = rawGroups.map(g => {
        const thread = messages.filter(m => m.group_name === g.id);
        const lastMsg = thread.length > 0 ? thread[thread.length - 1] : null;
        const lastTime = lastMsg ? new Date(lastMsg.created_at) : new Date(0);
        const hasUnread = thread.some(m => m.sender_id !== currentUser.id && !m.is_read);
        return {
            id: g.id,
            name: g.name,
            desc: lastMsg ? lastMsg.body : g.desc,
            isGroup: true,
            avatarInitials: g.avatarInitials,
            lastMessageTime: lastTime,
            hasUnread: hasUnread
        };
    });
    
    // 2. Gather Direct Contacts
    let rawContacts = [];
    if (currentUser.role === "admin") {
        rawContacts = users.filter(u => u.role !== "admin");
    } else {
        rawContacts = users.filter(u => u.role === "admin");
    }
    
    // Process Direct Contacts
    const contactItems = rawContacts.map(contact => {
        const thread = messages.filter(m => 
            !m.group_name && (
                (m.sender_id === currentUser.id && m.receiver_id === contact.id) ||
                (m.sender_id === contact.id && m.receiver_id === currentUser.id)
            )
        );
        const lastMsg = thread.length > 0 ? thread[thread.length - 1] : null;
        const lastTime = lastMsg ? new Date(lastMsg.created_at) : new Date(0);
        const hasUnread = thread.some(m => m.sender_id === contact.id && !m.is_read);
        return {
            id: contact.id,
            name: contact.full_name || contact.username,
            desc: lastMsg ? lastMsg.body : (contact.role === "admin" ? "Systems Administrator" : (contact.track || "")),
            isGroup: false,
            avatar: contact.avatar,
            lastMessageTime: lastTime,
            hasUnread: hasUnread
        };
    });
    
    // 3. Combine and Sort by lastMessageTime descending (newest on top)
    const allItems = [...groupItems, ...contactItems].sort((a, b) => b.lastMessageTime - a.lastMessageTime);
    
    // 4. Render
    const chatWindow = document.getElementById("chat-window");
    const activeType = chatWindow ? chatWindow.dataset.chatType : "";
    const activeTarget = chatWindow ? chatWindow.dataset.chatTarget : "";
    
    allItems.forEach(item => {
        const div = document.createElement("div");
        
        // Active border highlights
        const isActive = (item.isGroup && activeType === "group" && activeTarget === item.id) ||
                         (!item.isGroup && activeType === "direct" && activeTarget && parseInt(activeTarget) === item.id);
        
        div.className = `p-3 mb-2 glass-panel glass-panel-hover border ${isActive ? 'border-primary' : 'border-secondary'}`;
        div.style.cursor = "pointer";
        
        // Red dot styling
        const redDotHtml = item.hasUnread ? 
            `<span class="badge rounded-circle bg-danger p-0 ms-2" style="width: 8px; height: 8px; display: inline-block;" title="Unread Message"></span>` : "";
            
        // Avatar column
        let avatarHtml = "";
        if (item.isGroup) {
            avatarHtml = `<div class="rounded-circle d-flex align-items-center justify-content-center bg-primary text-white fw-bold" style="width:40px; height:40px; font-size:0.85rem; background: var(--primary-gradient); flex-shrink: 0;">
                ${item.avatarInitials}
            </div>`;
        } else {
            avatarHtml = `<img src="${item.avatar}" class="rounded-circle border border-secondary" width="40" height="40" style="flex-shrink: 0;">`;
        }
        
        // Format last message time
        let timeString = "";
        if (item.lastMessageTime.getTime() > 0) {
            const h = String(item.lastMessageTime.getHours()).padStart(2, '0');
            const m = String(item.lastMessageTime.getMinutes()).padStart(2, '0');
            timeString = `<span class="small text-secondary" style="font-size:0.7rem;">${h}:${m}</span>`;
        }
        
        div.innerHTML = `
            <div class="d-flex align-items-center gap-3">
                ${avatarHtml}
                <div class="flex-grow-1 overflow-hidden">
                    <div class="d-flex align-items-center justify-content-between">
                        <div class="fw-bold text-white d-flex align-items-center">
                            <span>${item.name}</span>
                            ${item.isGroup ? `<span class="badge bg-secondary ms-2" style="font-size:0.55rem;">GROUP</span>` : ""}
                            ${redDotHtml}
                        </div>
                        ${timeString}
                    </div>
                    <div class="small text-secondary text-truncate mt-1" style="font-size:0.8rem;">${item.desc}</div>
                </div>
            </div>
        `;
        
        div.addEventListener("click", () => {
            document.querySelectorAll("#inbox-list > div").forEach(d => d.className = "p-3 mb-2 glass-panel glass-panel-hover border border-secondary");
            div.className = "p-3 mb-2 glass-panel glass-panel-hover border border-primary";
            openChatWith(currentUser.id, item.isGroup ? "group" : "direct", item.id, item.name);
        });
        
        inboxList.appendChild(div);
    });
    
    // Auto load first item on initial load
    if (autoSelect && allItems.length > 0) {
        openChatWith(currentUser.id, allItems[0].isGroup ? "group" : "direct", allItems[0].id, allItems[0].name);
    }
}

function openChatWith(currentUserId, chatType, chatTarget, name) {
    const chatWindow = document.getElementById("chat-window");
    if (!chatWindow) return;
    
    chatWindow.dataset.chatType = chatType;
    chatWindow.dataset.chatTarget = chatTarget;
    document.getElementById("chat-partner-name").textContent = name;
    
    // Mark messages as read locally
    const messages = JSON.parse(localStorage.getItem("erp_messages") || "[]");
    let changed = false;
    if (chatType === "group") {
        messages.forEach(m => {
            if (m.group_name === chatTarget && m.sender_id !== currentUserId && !m.is_read) {
                m.is_read = true;
                changed = true;
            }
        });
    } else {
        const targetUserId = parseInt(chatTarget);
        messages.forEach(m => {
            if (!m.group_name && m.sender_id === targetUserId && m.receiver_id === currentUserId && !m.is_read) {
                m.is_read = true;
                changed = true;
            }
        });
    }
    
    if (changed) {
        localStorage.setItem("erp_messages", JSON.stringify(messages));
        
        // Post to backend API
        const postData = {};
        if (chatType === "group") {
            postData.group_name = chatTarget;
        } else {
            postData.receiver_id = parseInt(chatTarget);
        }
        
        fetch("/erp/api/messages/read/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken")
            },
            body: JSON.stringify(postData)
        })
        .then(res => res.json())
        .then(data => {
            const user = getLoggedInUser();
            if (user) {
                renderInbox(user, false);
            }
        });
    }
    
    renderChatHistory(currentUserId, chatType, chatTarget);
}

function renderChatHistory(currentUserId, chatType, chatTarget) {
    const chatBody = document.getElementById("chat-history");
    if (!chatBody) return;
    
    const messages = JSON.parse(localStorage.getItem("erp_messages") || "[]");
    const users = JSON.parse(localStorage.getItem("erp_users") || "[]");
    
    let thread = [];
    if (chatType === "group") {
        thread = messages.filter(m => m.group_name === chatTarget);
    } else {
        const targetUserId = parseInt(chatTarget);
        thread = messages.filter(m => 
            !m.group_name && (
                (m.sender_id === currentUserId && m.receiver_id === targetUserId) ||
                (m.sender_id === targetUserId && m.receiver_id === currentUserId)
            )
        );
    }
    
    thread = thread.sort((a,b) => new Date(a.created_at) - new Date(b.created_at));
    
    chatBody.innerHTML = "";
    if (thread.length === 0) {
        chatBody.innerHTML = `<div class="text-center text-muted py-5">No correspondence history. Start the conversation below.</div>`;
        return;
    }
    
    thread.forEach(msg => {
        const bubbleContainer = document.createElement("div");
        bubbleContainer.className = "mb-3 d-flex flex-column";
        
        const isSent = msg.sender_id === currentUserId;
        
        if (isSent) {
            bubbleContainer.className += " align-items-end";
        } else {
            bubbleContainer.className += " align-items-start";
        }
        
        // Find sender details
        let senderName = "System";
        if (isSent) {
            senderName = "You";
        } else {
            const senderUser = users.find(u => u.id === msg.sender_id);
            if (senderUser) {
                senderName = senderUser.full_name || senderUser.username;
            }
        }
        
        const nameLabel = document.createElement("span");
        nameLabel.className = "text-secondary small mb-1";
        nameLabel.style.fontSize = "0.75rem";
        nameLabel.textContent = senderName;
        bubbleContainer.appendChild(nameLabel);
        
        const bubble = document.createElement("div");
        bubble.className = `chat-bubble ${isSent ? 'sent' : 'received'}`;
        bubble.textContent = msg.body;
        bubbleContainer.appendChild(bubble);
        
        chatBody.appendChild(bubbleContainer);
    });
    
    chatBody.scrollTop = chatBody.scrollHeight;
}

// Edit Profile Form Controls
function setupEditProfileForm() {
    const user = getLoggedInUser();
    if (!user) return;
    
    document.getElementById("p-fullname").value = user.full_name || "";
    document.getElementById("p-phone").value = user.phone || "";
    document.getElementById("p-bio").value = user.bio || "";
    document.getElementById("p-academic").value = user.academic_background || "";
    document.getElementById("p-skills").value = user.skills || "";
    if (document.getElementById("p-track")) {
        document.getElementById("p-track").value = user.track || "";
    }
    
    const form = document.getElementById("editProfileForm");
    form.addEventListener("submit", (e) => {
        e.preventDefault();
        
        const fullname = document.getElementById("p-fullname").value;
        const phone = document.getElementById("p-phone").value;
        const bio = document.getElementById("p-bio").value;
        const academic = document.getElementById("p-academic").value;
        const skills = document.getElementById("p-skills").value;
        const trackSelect = document.getElementById("p-track");
        
        const formData = new FormData();
        formData.append("fullname", fullname);
        formData.append("phone", phone);
        formData.append("bio", bio);
        formData.append("academic", academic);
        formData.append("skills", skills);
        if (trackSelect) {
            formData.append("track", trackSelect.value);
        }
        
        fetch("/erp/edit-profile/", {
            method: "POST",
            headers: {
                "X-CSRFToken": getCookie("csrftoken")
            },
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                const users = JSON.parse(localStorage.getItem("erp_users") || "[]");
                const idx = users.findIndex(u => u.id === user.id);
                if (idx !== -1) {
                    users[idx].full_name = fullname;
                    users[idx].phone = phone;
                    users[idx].bio = bio;
                    users[idx].academic_background = academic;
                    users[idx].skills = skills;
                    if (trackSelect) {
                        users[idx].track = trackSelect.value;
                    }
                    localStorage.setItem("erp_users", JSON.stringify(users));
                }
                
                addActivityLog(user.id, "Updated profile metrics");
                showToast("Profile settings updated successfully!", "success");
                
                setTimeout(() => window.location.href = "/erp/profile/", 1000);
            } else {
                showToast(data.message || "Failed to update profile", "danger");
            }
        })
        .catch(err => {
            showToast("Error updating profile settings", "danger");
            console.error(err);
        });
    });
}

// Render dynamic Activity Logs (Admin Panel)
function renderActivityLogs() {
    checkAuthentication("admin");
    const tbody = document.getElementById("activity-logs-tbody");
    if (!tbody) return;
    
    const logs = JSON.parse(localStorage.getItem("erp_logs") || "[]");
    const users = JSON.parse(localStorage.getItem("erp_users") || "[]");
    tbody.innerHTML = "";
    
    if (logs.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" class="text-center text-muted">No activity recorded.</td></tr>`;
        return;
    }
    
    logs.forEach(log => {
        const u = users.find(usr => usr.id === log.user_id);
        const name = u ? (u.full_name || u.username) : "Guest";
        const role = u ? u.role : "N/A";
        const formattedTime = new Date(log.timestamp).toLocaleString();
        
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${log.id}</td>
            <td><strong>${name}</strong> <span class="small text-muted">(${role})</span></td>
            <td>${log.action}</td>
            <td><code>${log.ip_address}</code></td>
            <td>${formattedTime}</td>
        `;
        tbody.appendChild(tr);
    });
}

// Settings
function setupSettings() {
    const user = getLoggedInUser();
    if (!user) return;
    
    const emailNotifCheck = document.getElementById("settings-email-notify");
    if (emailNotifCheck) {
        emailNotifCheck.checked = true;
        emailNotifCheck.addEventListener("change", () => {
            const formData = new FormData();
            formData.append("email_notifications", emailNotifCheck.checked ? "true" : "false");
            fetch("/erp/settings/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCookie("csrftoken")
                },
                body: formData
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    showToast("Email notifications preference updated", "success");
                    addActivityLog(user.id, "Changed notification preferences");
                }
            })
            .catch(err => console.error("Failed to update settings", err));
        });
    }
}

// Data Management panel backups
function setupDataManagement() {
    checkAuthentication("admin");
    
    const exportBtn = document.getElementById("export-db-btn");
    const backupBtn = document.getElementById("backup-db-btn");
    
    if (exportBtn) {
        exportBtn.addEventListener("click", () => {
            showToast("Simulating data extraction... CSV download triggered", "success");
        });
    }
    
    if (backupBtn) {
        backupBtn.addEventListener("click", () => {
            showToast("Created a complete JSON backup point in downloads", "success");
        });
    }
}

// Reports PDF / CSV Generator
function renderReportsPage() {
    const user = getLoggedInUser();
    if (!user) return;
    
    const csvBtn = document.getElementById("report-csv-btn");
    const pdfBtn = document.getElementById("report-pdf-btn");
    
    if (csvBtn) {
        csvBtn.addEventListener("click", () => {
            showToast("Downloading formatted CSV statistics report...", "success");
        });
    }
    
    if (pdfBtn) {
        pdfBtn.addEventListener("click", () => {
            showToast("Generating document layout PDF for download...", "success");
        });
    }
}

// Analytics graph generator page
function renderAnalyticsPage() {
    const user = getLoggedInUser();
    if (!user) return;
    
    const files = JSON.parse(localStorage.getItem("erp_files") || "[]");
    const users = JSON.parse(localStorage.getItem("erp_users") || "[]");
    
    const ctx = document.getElementById("analyticsReportChart");
    if (ctx) {
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Approved', 'Pending', 'Rejected'],
                datasets: [{
                    label: 'Application Statuses',
                    data: [
                        users.filter(u => u.status === 'approved').length,
                        users.filter(u => u.status === 'pending').length,
                        users.filter(u => u.status === 'rejected').length
                    ],
                    backgroundColor: ['#00e676', '#f59e0b', '#f43f5e']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }
}

// Global search results filtering simulation
function setupSearchPage() {
    const params = new URLSearchParams(window.location.search);
    const query = params.get("q") || "";
    
    document.getElementById("search-input-field").value = query;
    performSearch(query);
    
    document.getElementById("search-form").addEventListener("submit", (e) => {
        e.preventDefault();
        const val = document.getElementById("search-input-field").value;
        performSearch(val);
    });
}

function performSearch(q) {
    const resultsContainer = document.getElementById("search-results-list");
    if (!resultsContainer) return;
    
    resultsContainer.innerHTML = "";
    
    if (!q.trim()) {
        resultsContainer.innerHTML = `<div class="text-center text-muted py-5">Enter search keywords above.</div>`;
        return;
    }
    
    const query = q.toLowerCase();
    const users = JSON.parse(localStorage.getItem("erp_users") || "[]").filter(u => u.role !== "admin");
    const files = JSON.parse(localStorage.getItem("erp_files") || "[]");
    
    const filteredUsers = users.filter(u => 
        (u.full_name && u.full_name.toLowerCase().includes(query)) ||
        u.email.toLowerCase().includes(query) ||
        (u.track && u.track.toLowerCase().includes(query))
    );
    
    const filteredFiles = files.filter(f => f.file_name.toLowerCase().includes(query));
    
    if (filteredUsers.length === 0 && filteredFiles.length === 0) {
        resultsContainer.innerHTML = `<div class="text-center text-muted py-5">No records matching "${q}" found.</div>`;
        return;
    }
    
    filteredUsers.forEach(u => {
        const item = document.createElement("div");
        item.className = "p-3 mb-3 glass-panel d-flex justify-content-between align-items-center";
        item.innerHTML = `
            <div>
                <span class="badge bg-primary me-2">User Profile</span>
                <strong>${u.full_name || u.username}</strong> - ${u.email}
                <div class="small text-secondary mt-1">Track: ${u.track || "N/A"} | Status: ${u.status}</div>
            </div>
            <a href="profile.html?id=${u.id}" class="btn btn-sm btn-outline-primary">View</a>
        `;
        resultsContainer.appendChild(item);
    });
    
    filteredFiles.forEach(f => {
        const item = document.createElement("div");
        item.className = "p-3 mb-3 glass-panel d-flex justify-content-between align-items-center";
        item.innerHTML = `
            <div>
                <span class="badge bg-secondary me-2">File</span>
                <strong>${f.file_name}</strong>
                <div class="small text-secondary mt-1">Size: ${(f.file_size/1024).toFixed(0)} KB | Format: ${f.file_type}</div>
            </div>
            <button class="btn btn-sm btn-outline-info" onclick="showToast('Simulating download...', 'info')">Download</button>
        `;
        resultsContainer.appendChild(item);
    });
}

// User History Milestone Logger
function renderHistoryPage() {
    const user = getLoggedInUser();
    if (!user) return;
    
    const list = document.getElementById("milestone-list");
    if (!list) return;
    
    const history = JSON.parse(localStorage.getItem("erp_history") || "[]").filter(h => h.user_id === user.id);
    list.innerHTML = "";
    
    if (history.length === 0) {
        list.innerHTML = `<div class="text-center text-muted py-5">No achievements recorded yet.</div>`;
        return;
    }
    
    history.forEach(item => {
        const div = document.createElement("div");
        div.className = "mb-4 border-start border-3 border-primary ps-4 relative";
        const dateStr = new Date(item.achieved_at).toLocaleDateString();
        div.innerHTML = `
            <div class="fw-bold fs-5">${item.milestone_name}</div>
            <div class="small text-muted mb-2">${dateStr}</div>
            <div>${item.description}</div>
        `;
        list.appendChild(div);
    });
}

// Notifications listing page
function renderNotificationsPage() {
    const user = getLoggedInUser();
    if (!user) return;
    
    const list = document.getElementById("notifications-list");
    if (!list) return;
    
    const notifications = JSON.parse(localStorage.getItem("erp_notifications") || "[]").filter(n => n.user_id === user.id);
    list.innerHTML = "";
    
    if (notifications.length === 0) {
        list.innerHTML = `<div class="text-center text-muted py-5">No notifications.</div>`;
        return;
    }
    
    notifications.forEach(n => {
        const div = document.createElement("div");
        div.className = `p-3 mb-3 glass-panel border-start border-4 border-${n.level === 'danger' ? 'danger' : n.level === 'success' ? 'success' : n.level === 'warning' ? 'warning' : 'info'}`;
        div.innerHTML = `
            <div class="d-flex justify-content-between align-items-start">
                <div>
                    <h5 class="mb-1">${n.title}</h5>
                    <p class="mb-0 text-secondary small">${n.message}</p>
                </div>
                <button class="btn btn-sm btn-link text-muted" onclick="deleteNotification(${n.id})">Clear</button>
            </div>
        `;
        list.appendChild(div);
    });
    
    // Mark notifications as read
    const allNotifs = JSON.parse(localStorage.getItem("erp_notifications") || "[]");
    allNotifs.forEach(not => {
        if (not.user_id === user.id) not.is_read = true;
    });
    localStorage.setItem("erp_notifications", JSON.stringify(allNotifs));
    handleNotificationsBadge();
}

window.deleteNotification = function(notifId) {
    let notifications = JSON.parse(localStorage.getItem("erp_notifications") || "[]");
    notifications = notifications.filter(n => n.id !== notifId);
    localStorage.setItem("erp_notifications", JSON.stringify(notifications));
    showToast("Notification cleared", "info");
    renderNotificationsPage();
};

// User Profile display detail page
function renderProfilePage() {
    const user = getLoggedInUser();
    if (!user) return;
    
    // Detect if reading dynamic profile query or personal profile
    const params = new URLSearchParams(window.location.search);
    const requestedId = params.get("id");
    
    let profileUser = user;
    if (requestedId && user.role === "admin") {
        const users = JSON.parse(localStorage.getItem("erp_users") || "[]");
        profileUser = users.find(u => u.id === parseInt(requestedId)) || user;
    }
    
    document.getElementById("prof-name").textContent = profileUser.full_name || profileUser.username;
    document.getElementById("prof-track").textContent = profileUser.track || "N/A";
    document.getElementById("prof-status").textContent = profileUser.status;
    document.getElementById("prof-status").className = `badge-status status-${profileUser.status}`;
    document.getElementById("prof-email").textContent = profileUser.email;
    document.getElementById("prof-phone").textContent = profileUser.phone || "N/A";
    document.getElementById("prof-bio").textContent = profileUser.bio || "No biography provided yet.";
    document.getElementById("prof-academic").textContent = profileUser.academic_background || "N/A";
    document.getElementById("prof-skills").textContent = profileUser.skills || "N/A";
    
    if (profileUser.avatar) {
        document.getElementById("prof-avatar").src = profileUser.avatar;
    }
}

// User Feedback setup
function setupFeedbackForm() {
    const user = getLoggedInUser();
    if (!user) return;
    
    const form = document.getElementById("feedbackForm");
    if (!form) return;
    
    form.addEventListener("submit", (e) => {
        e.preventDefault();
        
        const subj = document.getElementById("fb-subject").value.trim();
        const msg = document.getElementById("fb-message").value.trim();
        const rating = parseInt(document.getElementById("fb-rating").value);
        
        const formData = new FormData();
        formData.append("subject", subj);
        formData.append("message", msg);
        formData.append("rating", rating);
        
        fetch("/erp/feedback/", {
            method: "POST",
            headers: {
                "X-CSRFToken": getCookie("csrftoken")
            },
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                const feedbacks = JSON.parse(localStorage.getItem("erp_feedback") || "[]");
                const newFb = {
                    id: feedbacks.length + 1,
                    user_id: user.id,
                    subject: subj,
                    message: msg,
                    rating: rating,
                    created_at: new Date().toISOString()
                };
                
                feedbacks.unshift(newFb);
                localStorage.setItem("erp_feedback", JSON.stringify(feedbacks));
                
                addActivityLog(user.id, `Submitted feedback: ${subj}`);
                showToast("Thank you for your feedback!", "success");
                form.reset();
            }
        })
        .catch(err => console.error("Failed to submit feedback", err));
    });
}

// User Help ticket system simulation
function setupHelpCenter() {
    const user = getLoggedInUser();
    if (!user) return;
    
    const form = document.getElementById("helpTicketForm");
    if (form) {
        form.addEventListener("submit", (e) => {
            e.preventDefault();
            fetch("/erp/help-center/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCookie("csrftoken")
                }
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    showToast("Troubleshoot ticket submitted to recruitment support team!", "success");
                    addActivityLog(user.id, "Logged help center request");
                    form.reset();
                }
            })
            .catch(err => console.error("Failed to log help ticket", err));
        });
    }
}

// Global Sign Out Confirmation Interceptor
document.addEventListener("click", (e) => {
    const logoutLink = e.target.closest('a[href*="/auth/logout/"]');
    if (logoutLink) {
        e.preventDefault();
        showLogoutConfirmation(logoutLink.href);
    }
});

function showLogoutConfirmation(logoutUrl) {
    let modal = document.getElementById("logout-confirm-modal");
    if (!modal) {
        modal = document.createElement("div");
        modal.id = "logout-confirm-modal";
        modal.style.cssText = "display:none; position:fixed; top:0; left:0; width:100vw; height:100vh; background:rgba(15,23,42,0.7); backdrop-filter:blur(6px); -webkit-backdrop-filter:blur(6px); z-index:99999; align-items:center; justify-content:center;";
        modal.innerHTML = `
            <div class="glass-panel text-center p-4 rounded-4 shadow-lg" style="width: 360px; max-width: 90%; border: 1px solid var(--card-border); background: rgba(30, 41, 59, 0.85); box-shadow: 0 20px 25px -5px rgb(0 0 0 / 0.5);">
                <div class="mb-3 text-center">
                    <div class="rounded-circle d-inline-flex align-items-center justify-content-center bg-danger-bg text-danger" style="width:64px; height:64px; background: rgba(244,63,94,0.15); border: 1px solid rgba(244,63,94,0.3);">
                        <i class="bi bi-box-arrow-right" style="font-size: 1.75rem;"></i>
                    </div>
                </div>
                <h4 class="text-white mb-2 fw-bold">Sign Out?</h4>
                <p class="text-secondary small mb-4" style="line-height:1.5;">Are you sure you want to end your current session and sign out of BlueNova ERP?</p>
                <div class="d-flex gap-3 justify-content-center">
                    <button id="logout-cancel-btn" class="btn btn-secondary-premium px-4 py-2" style="font-size:0.9rem;">Cancel</button>
                    <button id="logout-confirm-btn" class="btn btn-danger px-4 py-2" style="background: linear-gradient(135deg, #f43f5e 0%, #be123c 100%); border:none; font-size:0.9rem;">Sign Out</button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        
        modal.querySelector("#logout-cancel-btn").addEventListener("click", () => {
            modal.style.display = "none";
        });
        
        modal.addEventListener("click", (evt) => {
            if (evt.target === modal) {
                modal.style.display = "none";
            }
        });
    }
    
    const confirmBtn = modal.querySelector("#logout-confirm-btn");
    confirmBtn.onclick = () => {
        window.location.href = logoutUrl;
    };
    
    modal.style.display = "flex";
}
