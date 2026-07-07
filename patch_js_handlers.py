import os

paths = [
    r'c:\Users\Win11\Downloads\erp\erp\backend\static\js\app.js',
    r'c:\Users\Win11\Downloads\erp\erp\frontend\js\app.js'
]

# 1. Define addActivityLog
def_add_activity_log = """// Core ERP Utility and Interaction Layer
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

function getCookie(name) {"""

# 2. handleFilesUpload
old_handle_files_upload = """function handleFilesUpload(filesList, userId) {
    if (filesList.length === 0) return;
    
    const files = JSON.parse(localStorage.getItem("erp_files") || "[]");
    
    for (let i = 0; i < filesList.length; i++) {
        const file = filesList[i];
        
        // Validation: PDF, DOCX, Images, ZIP. Limit size to 10MB (10485760 bytes)
        const allowedTypes = ["pdf", "docx", "zip", "png", "jpg", "jpeg"];
        const ext = file.name.split(".").pop().toLowerCase();
        
        if (!allowedTypes.includes(ext)) {
            showToast(`Extension .${ext} is not allowed. Upload PDF, DOCX, ZIP, or Images.`, "danger");
            continue;
        }
        
        if (file.size > 10485760) {
            showToast(`File ${file.name} is too large. Limit is 10MB.`, "danger");
            continue;
        }
        
        const newFile = {
            id: files.length + 1,
            user_id: userId,
            file_name: file.name,
            file_size: file.size,
            file_type: ext,
            uploaded_at: new Date().toISOString()
        };
        
        files.push(newFile);
        addActivityLog(userId, `Uploaded document ${file.name}`);
        showToast(`File ${file.name} uploaded successfully!`, "success");
    }
    
    localStorage.setItem("erp_files", JSON.stringify(files));
    renderFilesList(userId);
}"""

new_handle_files_upload = """function handleFilesUpload(filesList, userId) {
    if (filesList.length === 0) return;
    
    const allowedTypes = ["pdf", "docx", "zip", "png", "jpg", "jpeg"];
    
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
        
        const formData = new FormData();
        formData.append("file", file);
        
        fetch("/erp/upload-files/", {
            method: "POST",
            headers: {
                "X-CSRFToken": getCookie("csrftoken")
            },
            body: formData
        })
        .then(res => {
            if (!res.ok) {
                return res.json().then(err => { throw new Error(err.message || "Upload failed"); });
            }
            return res.json();
        })
        .then(data => {
            if (data.success) {
                showToast(`File ${file.name} uploaded successfully!`, "success");
                addActivityLog(userId, `Uploaded document ${file.name}`);
                
                const localFiles = JSON.parse(localStorage.getItem("erp_files") || "[]");
                localFiles.push(data.file);
                localStorage.setItem("erp_files", JSON.stringify(localFiles));
                
                renderFilesList(userId);
            } else {
                showToast(data.message || "Failed to upload file", "danger");
            }
        })
        .catch(err => {
            showToast(err.message || "Error uploading file to server", "danger");
            console.error(err);
        });
    }
}"""

# 3. deleteUserFile
old_delete_user_file = """window.deleteUserFile = function(fileId, userId) {
    if (confirm("Are you sure you want to delete this file?")) {
        let files = JSON.parse(localStorage.getItem("erp_files") || "[]");
        const file = files.find(f => f.id === fileId);
        files = files.filter(f => f.id !== fileId);
        localStorage.setItem("erp_files", JSON.stringify(files));
        
        if (file) addActivityLog(userId, `Deleted document ${file.file_name}`);
        showToast("File deleted", "success");
        renderFilesList(userId);
    }
};"""

new_delete_user_file = """window.deleteUserFile = function(fileId, userId) {
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
                
                if (file) addActivityLog(userId, `Deleted document ${file.file_name}`);
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
};"""

# 4. editProfileForm
old_edit_profile = """    const form = document.getElementById("editProfileForm");
    form.addEventListener("submit", (e) => {
        e.preventDefault();
        
        const users = JSON.parse(localStorage.getItem("erp_users") || "[]");
        const idx = users.findIndex(u => u.id === user.id);
        
        if (idx !== -1) {
            users[idx].full_name = document.getElementById("p-fullname").value;
            users[idx].phone = document.getElementById("p-phone").value;
            users[idx].bio = document.getElementById("p-bio").value;
            users[idx].academic_background = document.getElementById("p-academic").value;
            users[idx].skills = document.getElementById("p-skills").value;
            if (document.getElementById("p-track")) {
                users[idx].track = document.getElementById("p-track").value;
            }
            
            localStorage.setItem("erp_users", JSON.stringify(users));
            addActivityLog(user.id, "Updated profile metrics");
            showToast("Profile settings updated successfully!", "success");
            
            setTimeout(() => window.location.href = "profile.html", 1000);
        }
    });"""

new_edit_profile = """    const form = document.getElementById("editProfileForm");
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
    });"""

# 5. setupSettings
old_setup_settings = """function setupSettings() {
    const user = getLoggedInUser();
    if (!user) return;
    
    const emailNotifCheck = document.getElementById("settings-email-notify");
    if (emailNotifCheck) {
        emailNotifCheck.checked = true;
        emailNotifCheck.addEventListener("change", () => {
            showToast("Email notifications preference updated", "success");
            addActivityLog(user.id, "Changed notification preferences");
        });
    }
}"""

new_setup_settings = """function setupSettings() {
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
}"""

# 6. setupFeedbackForm
old_setup_feedback = """function setupFeedbackForm() {
    const user = getLoggedInUser();
    if (!user) return;
    
    const form = document.getElementById("feedbackForm");
    form.addEventListener("submit", (e) => {
        e.preventDefault();
        
        const subj = document.getElementById("fb-subject").value;
        const msg = document.getElementById("fb-message").value;
        const rating = parseInt(document.getElementById("fb-rating").value);
        
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
    });
}"""

new_setup_feedback = """function setupFeedbackForm() {
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
}"""

# 7. setupHelpCenter
old_setup_help = """function setupHelpCenter() {
    const user = getLoggedInUser();
    if (!user) return;
    
    const form = document.getElementById("helpTicketForm");
    if (form) {
        form.addEventListener("submit", (e) => {
            e.preventDefault();
            showToast("Troubleshoot ticket submitted to recruitment support team!", "success");
            addActivityLog(user.id, "Logged help center request");
            form.reset();
        });
    }
}"""

new_setup_help = """function setupHelpCenter() {
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
}"""

for path in paths:
    if not os.path.exists(path):
        print("Path not found:", path)
        continue
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Define addActivityLog
    if "window.addActivityLog" not in content:
        content = content.replace("// Core ERP Utility and Interaction Layer\nfunction getCookie(name) {", def_add_activity_log)
        content = content.replace("function getCookie(name) {", "window.addActivityLog = function(userId, action) { ... };\n\nfunction getCookie(name) {") # Fallback
        
    # 2. handleFilesUpload
    content = content.replace(old_handle_files_upload, new_handle_files_upload)
    
    # 3. deleteUserFile
    content = content.replace(old_delete_user_file, new_delete_user_file)
    
    # 4. editProfile
    content = content.replace(old_edit_profile, new_edit_profile)
    
    # 5. setupSettings
    content = content.replace(old_setup_settings, new_setup_settings)
    
    # 6. setupFeedback
    content = content.replace(old_setup_feedback, new_setup_feedback)
    
    # 7. setupHelp
    content = content.replace(old_setup_help, new_setup_help)
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Patched:", path)
