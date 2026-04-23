const API_BASE = "http://127.0.0.1:5000/api";

if (localStorage.getItem("role") !== "admin") {
alert("Admin access only!");
window.location.href = "../pages/login.html";
}

document.addEventListener("DOMContentLoaded", function () {
loadUsers();
loadLoans();
loadAnnouncements();
});

function formatCurrency(value) {
return `PHP ${Number(value || 0).toLocaleString("en-PH", {
minimumFractionDigits: 2,
maximumFractionDigits: 2
})}`;
}

function formatDisplayDate(value) {
if (!value) return "N/A";
const date = new Date(value);
if (Number.isNaN(date.getTime())) return value;
return date.toLocaleDateString("en-PH");
}

function showToast(message, isError = false) {
let toast = document.getElementById("adminToast");
if (!toast) {
toast = document.createElement("div");
toast.id = "adminToast";
toast.style.position = "fixed";
toast.style.right = "20px";
toast.style.bottom = "20px";
toast.style.padding = "10px 14px";
toast.style.borderRadius = "8px";
toast.style.color = "#fff";
toast.style.fontSize = "14px";
toast.style.zIndex = "9999";
toast.style.boxShadow = "0 4px 12px rgba(0,0,0,0.2)";
document.body.appendChild(toast);
}
toast.style.backgroundColor = isError ? "#c62828" : "#2e7d32";
toast.innerText = message;
toast.style.display = "block";
clearTimeout(showToast._timer);
showToast._timer = setTimeout(() => {
toast.style.display = "none";
}, 1800);
}

async function loadUsers() {
let table = document.getElementById("memberTable");
if (!table) return;
let users = [];
try {
const response = await fetch(`${API_BASE}/users`);
const data = await response.json();
users = data.users || [];
} catch (error) {
    table.innerHTML = "<tr><td colspan='5'>Failed to load users.</td></tr>";
    return;
}

    table.innerHTML = `
<tr>
<th>Name</th>
<th>Email</th>
<th>Status</th>
<th>Role</th>
<th>Action</th>
</tr>
`;

users.forEach((user) => {
    let displayName = user.fullname || user.username || "N/A";
    let role = (user.role || "member").toLowerCase();
    let status = (user.status || "").toLowerCase();
    table.innerHTML += `
<tr>
<td>${displayName}</td>
<td>${user.email || "N/A"}</td>
<td class="${status}">${status.toUpperCase()}</td>
<td class="role-cell">${role.toUpperCase()}</td>
<td>
${status === "pending" ? `<button onclick="approveUser('${user.username}')">Approve</button>` : "Approved"}
<button onclick="editUserRole('${user.username}', '${role}')">Edit Role</button>
<button onclick="deleteUser('${user.username}')">Delete</button>
</td>
</tr>
`;
});
}

async function approveUser(username) {
try {
const response = await fetch(`${API_BASE}/users/${encodeURIComponent(username)}`, {
method: "PATCH",
headers: { "Content-Type": "application/json" },
body: JSON.stringify({ status: "approved" })
});
const data = await response.json();
if (data.success) {
showToast("User approved.");
loadUsers();
} else {
showToast(data.message || "Failed to approve user", true);
}
} catch (error) {
showToast("Cannot connect to server.", true);
}
}

async function deleteUser(username) {
try {
const response = await fetch(`${API_BASE}/users/${encodeURIComponent(username)}`, {
method: "DELETE"
});
const data = await response.json();
if (data.success) {
showToast("User deleted.");
loadUsers();
} else {
showToast(data.message || "Failed to delete user", true);
}
} catch (error) {
showToast("Cannot connect to server.", true);
}
}

let editingUsername = null;

function editUserRole(username, currentRole) {
    editingUsername = username;
    document.getElementById("editRoleUsername").innerText = `User: ${username}`;
    document.getElementById("roleSelect").value = currentRole;
    document.getElementById("editRoleModal").style.display = "block";
}

function closeEditRoleModal() {
    document.getElementById("editRoleModal").style.display = "none";
    editingUsername = null;
}

async function saveUserRole() {
    if (!editingUsername) return;
    const newRole = document.getElementById("roleSelect").value;
    try {
        const response = await fetch(`${API_BASE}/users/${encodeURIComponent(editingUsername)}`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ role: newRole })
        });
        const data = await response.json();
        if (data.success) {
            showToast("Role updated.");
            closeEditRoleModal();
            loadUsers();
        } else {
            showToast(data.message || "Failed to update role", true);
        }
    } catch (error) {
        showToast("Cannot connect to server.", true);
    }
}

async function loadAnnouncements() {
let table = document.getElementById("announcementTable");
if (!table) return;
try {
const response = await fetch(`${API_BASE}/announcements`);
const data = await response.json();
const announcements = data.announcements || [];
table.innerHTML = `
<tr>
<th>Date</th>
<th>Title</th>
<th>Content</th>
</tr>
`;
announcements.forEach((item) => {
let row = table.insertRow();
row.insertCell(0).innerText = formatDisplayDate(item.created_at);
row.insertCell(1).innerText = item.title;
row.insertCell(2).innerText = item.content;
});
if (!announcements.length) {
let row = table.insertRow();
let cell = row.insertCell(0);
cell.colSpan = 3;
cell.innerText = "No announcements yet.";
}
} catch (error) {
table.innerHTML = "<tr><td colspan='3'>Failed to load announcements.</td></tr>";
}
}

async function postAnnouncement() {
const title = document.getElementById("announcementTitle")?.value.trim() || "";
const content = document.getElementById("announcementContent")?.value.trim() || "";
if (!title || !content) {
showToast("Title and content are required.", true);
return;
}
try {
const response = await fetch(`${API_BASE}/announcements`, {
method: "POST",
headers: { "Content-Type": "application/json" },
body: JSON.stringify({ title, content })
});
const data = await response.json();
if (data.success) {
showToast("Announcement posted.");
document.getElementById("announcementTitle").value = "";
document.getElementById("announcementContent").value = "";
loadAnnouncements();
} else {
showToast(data.message || "Failed to post announcement", true);
}
} catch (error) {
showToast("Cannot connect to server.", true);
}
}

async function approveLoan(loanId, months) {
let dueDate = new Date();
dueDate.setMonth(dueDate.getMonth() + Number(months || 0));
try {
let response = await fetch(`${API_BASE}/loans/${loanId}`, {
method: "PATCH",
headers: { "Content-Type": "application/json" },
body: JSON.stringify({ status: "Approved", due_date: dueDate.toISOString().split("T")[0] })
});
let data = await response.json();
if (data.success) {
showToast("Loan approved.");
loadLoans();
} else {
showToast(data.message || "Failed to approve loan", true);
}
} catch (error) {
showToast("Cannot connect to server.", true);
}
}

async function rejectLoan(loanId) {
try {
let response = await fetch(`${API_BASE}/loans/${loanId}`, {
method: "PATCH",
headers: { "Content-Type": "application/json" },
body: JSON.stringify({ status: "Rejected", due_date: null })
});
let data = await response.json();
if (data.success) {
showToast("Loan rejected.");
loadLoans();
} else {
showToast(data.message || "Failed to reject loan", true);
}
} catch (error) {
showToast("Cannot connect to server.", true);
}
}

function searchTable() {
let input = document.getElementById("searchMember");
if (!input) return;
let filter = input.value.toLowerCase();
let table = document.getElementById("loanTable");
if (!table) return;
let rows = table.getElementsByTagName("tr");
let matches = 0;
for (let i = 1; i < rows.length; i++) {
let cells = rows[i].getElementsByTagName("td");
if (!cells.length) continue;
let rowText = Array.from(cells).map((cell) => (cell.textContent || cell.innerText || "").toLowerCase()).join(" ");
let isMatch = rowText.includes(filter);
rows[i].style.display = isMatch ? "" : "none";
if (isMatch) matches += 1;
}
let emptyRow = document.getElementById("loanSearchEmptyRow");
if (emptyRow) emptyRow.remove();
if (filter && matches === 0) {
let row = table.insertRow();
row.id = "loanSearchEmptyRow";
let cell = row.insertCell(0);
cell.colSpan = 6;
cell.innerText = "No matching member or loan record found.";
}
}

function showNotifications() {
showToast("Checking new loan requests.");
}

function openProfile() {
alert("Admin Profile");
}

function goDashboard() {
window.location.href = "../pages/admin-dashboard.html";
}

function goLoan() {
window.location.href = "../pages/loan-management.html";
}

function goReports() {
window.location.href = "../pages/reports.html";
}

function goMembers() {
window.location.href = "../pages/members.html";
}

async function loadLoans() {
let table = document.getElementById("loanTable");
if (!table) return;
let loans = [];
try {
let response = await fetch(`${API_BASE}/loans`);
let payload = await response.json();
loans = payload.loans || [];
} catch (error) {
table.innerHTML = "<tr><td colspan='6'>Failed to load loan requests.</td></tr>";
return;
}

table.innerHTML = `
<tr>
<th>Member</th>
<th>Loan Type</th>
<th>Amount</th>
<th>Status</th>
<th>Date</th>
<th>Action</th>
</tr>
`;

loans.forEach((loan) => {
let row = table.insertRow();
row.insertCell(0).innerText = loan.member_username || "Member";
row.insertCell(1).innerText = loan.loan_type;
row.insertCell(2).innerText = formatCurrency(loan.amount);
row.insertCell(3).innerText = loan.status;
row.insertCell(4).innerText = formatDisplayDate(loan.date_created);
if (loan.status === "Pending") {
row.insertCell(5).innerHTML = `
<button onclick="approveLoan(${loan.id}, ${loan.months})">Approve</button>
<button onclick="rejectLoan(${loan.id})">Reject</button>
`;
} else if (loan.status === "Approved" && loan.due_date) {
row.insertCell(5).innerText = `Due ${formatDisplayDate(loan.due_date)}`;
} else {
row.insertCell(5).innerText = "Processed";
}
});

if (loans.length === 0) {
let row = table.insertRow();
let cell = row.insertCell(0);
cell.colSpan = 6;
cell.innerText = "No loan requests yet.";
}
searchTable();
}

function logout() {
localStorage.clear();
window.location.href = "../pages/login.html";
}
