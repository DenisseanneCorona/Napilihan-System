let currentUser = JSON.parse(localStorage.getItem("currentUser"));
const API_BASE = "http://127.0.0.1:5000/api";
let loanTypeMap = {};

if (currentUser) {
document.querySelector("h1").innerText = "Welcome, " + currentUser.fullname;
}

if (localStorage.getItem("loggedIn") !== "true") {
window.location.href = "login.html";
}

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

function checkPenalty(loan) {
if (!loan.dueDate) return 0;
const due = new Date(loan.dueDate);
if (Number.isNaN(due.getTime()) || new Date() <= due) return 0;
const typeConfig = loanTypeMap[loan.type];
const penaltyRate = typeConfig ? Number(typeConfig.penalty_rate || 0.03) : 0.03;
return loan.amount * penaltyRate;
}

async function loadLoanTypes() {
const select = document.getElementById("loanType");
if (!select) return;
try {
const response = await fetch(`${API_BASE}/loan-types`);
const payload = await response.json();
const loanTypes = payload.loan_types || [];
loanTypeMap = loanTypes.reduce((acc, loanType) => {
acc[loanType.code] = loanType;
return acc;
}, {});
select.innerHTML = '<option value="">Select Loan Type</option>';
loanTypes.forEach((loanType) => {
const option = document.createElement("option");
option.value = loanType.code;
option.innerText = `${loanType.code} - ${loanType.loan_name}`;
select.appendChild(option);
});
} catch (error) {
select.innerHTML = '<option value="">Failed to load loan types</option>';
}
}

async function loadAnnouncements() {
const container = document.getElementById("announcementList");
if (!container) return;
try {
const response = await fetch(`${API_BASE}/announcements?limit=3`);
const payload = await response.json();
const announcements = payload.announcements || [];
if (!announcements.length) {
container.innerHTML = "<p>No announcements yet.</p>";
return;
}
container.innerHTML = announcements.map((item) => `
<div style="margin-bottom:10px;">
<strong>${item.title}</strong><br>
<span>${item.content}</span><br>
<small>${formatDisplayDate(item.created_at)}</small>
</div>
`).join("");
} catch (error) {
container.innerHTML = "<p>Failed to load announcements.</p>";
}
}

async function loadMemberTwoFactorStatus() {
const username = localStorage.getItem("currentUsername") || "";
const statusEl = document.getElementById("memberTwoFactorStatus");
if (!username || !statusEl) return;
try {
const response = await fetch(`${API_BASE}/users/${encodeURIComponent(username)}/2fa`);
const data = await response.json();
if (data.success) {
statusEl.innerText = data.two_factor_enabled ? "Email OTP is enabled for this account." : "Email OTP is currently disabled.";
} else {
statusEl.innerText = data.message || "Failed to load OTP status.";
}
} catch (error) {
statusEl.innerText = "Failed to load OTP status.";
}
}

async function toggleMemberTwoFactor(enabled) {
const username = localStorage.getItem("currentUsername") || "";
if (!username) return;
try {
const response = await fetch(`${API_BASE}/users/${encodeURIComponent(username)}/2fa`, {
method: "PATCH",
headers: { "Content-Type": "application/json" },
body: JSON.stringify({ enabled })
});
const data = await response.json();
if (data.success) {
alert(enabled ? "Email OTP enabled." : "Email OTP disabled.");
await loadMemberTwoFactorStatus();
} else {
alert(data.message || "Failed to update OTP status.");
}
} catch (error) {
alert("Cannot connect to server.");
}
}

function openLoanForm() {
document.getElementById("loanModal").style.display = "block";
}

function closeLoanForm() {
document.getElementById("loanModal").style.display = "none";
}

function calculateLoan() {
const type = document.getElementById("loanType").value;
const amount = parseFloat(document.getElementById("loanAmount").value);
const config = loanTypeMap[type];
if (!config || Number.isNaN(amount) || amount <= 0) {
alert("Please select loan type and enter a valid amount.");
return;
}
if (amount > Number(config.max_amount)) {
alert(`Maximum amount for ${type} is ${formatCurrency(config.max_amount)}.`);
return;
}
const serviceFee = amount * Number(config.service_fee_rate || 0);
const cbu = Number(config.cbu || 0);
const interest = amount * Number(config.interest_rate || 0) * Number(config.term_months || 0);
const totalDeduction = serviceFee + cbu + interest;
const netRelease = amount - totalDeduction;
document.getElementById("loanSummary").innerHTML = `
<h3>Loan Summary</h3>
<p>Loan Type: ${config.loan_name}</p>
<p>Loan Amount: ${formatCurrency(amount)}</p>
<p>Service Fee: ${formatCurrency(serviceFee)}</p>
<p>CBU: ${formatCurrency(cbu)}</p>
<p>Interest: ${formatCurrency(interest)}</p>
<p>Term: ${config.term_months} months</p>
<h4>Total Deduction: ${formatCurrency(totalDeduction)}</h4>
<h4>Net Release: ${formatCurrency(netRelease)}</h4>
`;
}

async function submitLoan() {
const type = document.getElementById("loanType").value;
const amount = parseFloat(document.getElementById("loanAmount").value);
const config = loanTypeMap[type];
if (!config || Number.isNaN(amount) || amount <= 0) {
alert("Complete loan details.");
return;
}
if (amount > Number(config.max_amount)) {
alert(`Maximum amount for ${type} is ${formatCurrency(config.max_amount)}.`);
return;
}
const memberKey = localStorage.getItem("currentUsername") || "";
if (!memberKey) {
alert("Please log in again.");
return;
}
try {
const response = await fetch(`${API_BASE}/loans`, {
method: "POST",
headers: { "Content-Type": "application/json" },
body: JSON.stringify({
member_username: memberKey,
loan_type: type,
amount: amount,
months: config.term_months,
date_created: new Date().toISOString().split("T")[0]
})
});
const data = await response.json();
if (data.success) {
alert("Loan submitted and sent to management for approval.");
closeLoanForm();
document.getElementById("loanType").value = "";
document.getElementById("loanAmount").value = "";
document.getElementById("loanSummary").innerHTML = "";
window.location.reload();
} else {
alert(data.message || "Failed to submit loan.");
}
} catch (error) {
alert("Cannot connect to server.");
}
}

window.onload = async function () {
await loadLoanTypes();
await loadAnnouncements();
await loadMemberTwoFactorStatus();

const memberKey = localStorage.getItem("currentUsername") || "";
if (!memberKey) return;
let payload;
try {
const response = await fetch(`${API_BASE}/loans?member_username=${encodeURIComponent(memberKey)}`);
payload = await response.json();
} catch (error) {
alert("Cannot load loan data from server.");
return;
}
const loans = (payload.loans || []).map((loan) => ({
id: loan.id,
date: loan.date_created,
type: loan.loan_type,
amount: Number(loan.amount || 0),
status: loan.status,
dueDate: loan.due_date
}));
const loanStatusEl = document.getElementById("loanStatus");
const nextPaymentEl = document.getElementById("nextPayment");
const table = document.getElementById("transactionTable");
loans.forEach((loan) => {
const penalty = checkPenalty(loan);
const row = table.insertRow();
row.insertCell(0).innerText = formatDisplayDate(loan.date);
row.insertCell(1).innerText = loan.type;
row.insertCell(2).innerText = formatCurrency(loan.amount);
row.insertCell(3).innerText = loan.status;
row.insertCell(4).innerText = formatDisplayDate(loan.dueDate);
row.insertCell(5).innerText = formatCurrency(penalty);
row.insertCell(6).innerText = loan.status === "Pending" ? "Waiting for management" : "Processed";
});
if (loans.length > 0) {
const latestLoan = loans[0];
if (loanStatusEl) loanStatusEl.innerText = `Loan ${latestLoan.status}: ${formatCurrency(latestLoan.amount)}`;
if (nextPaymentEl) {
if (latestLoan.status === "Approved" && latestLoan.dueDate) {
nextPaymentEl.innerText = `Due Date: ${formatDisplayDate(latestLoan.dueDate)}`;
} else if (latestLoan.status === "Rejected") {
nextPaymentEl.innerText = "Loan request was rejected";
} else {
nextPaymentEl.innerText = "Waiting for management approval";
}
}
} else {
if (loanStatusEl) loanStatusEl.innerText = "No Active Loan";
if (nextPaymentEl) nextPaymentEl.innerText = "None";
}
};

function logout() {
localStorage.removeItem("loggedIn");
localStorage.removeItem("role");
localStorage.removeItem("currentUsername");
localStorage.removeItem("currentUser");
window.location.href = "login.html";
}
