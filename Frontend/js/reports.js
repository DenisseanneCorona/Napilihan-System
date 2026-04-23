const API_BASE = "http://127.0.0.1:5000/api";
let reportPreviewData = null;

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

function viewMonthlyReport() {
document.getElementById("monthlyReport").scrollIntoView({ behavior: "smooth" });
}

function viewLoanReport() {
document.getElementById("loanReport").scrollIntoView({ behavior: "smooth" });
}

function escapeHtml(value) {
return String(value ?? "")
.replace(/&/g, "&amp;")
.replace(/</g, "&lt;")
.replace(/>/g, "&gt;")
.replace(/"/g, "&quot;")
.replace(/'/g, "&#39;");
}

async function loadPaymentSummary() {
const body = document.getElementById("monthlyTableBody");
const totalEl = document.getElementById("monthlyCollectionTotal");
if (!body) return;
body.innerHTML = "";
try {
const res = await fetch(`${API_BASE}/reports/payment-summary`);
const data = await res.json();
const collections = data.collections || [];
let total = 0;
collections.forEach((c) => {
const amount = Number(c.total_collection || 0);
total += amount;
const tr = document.createElement("tr");
tr.innerHTML = `<td>${c.month}</td><td>${formatCurrency(amount)}</td><td>${c.payment_count}</td>`;
body.appendChild(tr);
});
if (totalEl) {
totalEl.innerText = formatCurrency(total);
}
if (collections.length === 0) {
body.innerHTML = `<tr><td colspan="3">No payment collections yet.</td></tr>`;
}
} catch (e) {
body.innerHTML = `<tr><td colspan="3">Failed to load monthly collections.</td></tr>`;
}
}

async function loadLoanOptions() {
const select = document.getElementById("paymentLoanId");
if (!select) return;
try {
const res = await fetch(`${API_BASE}/loans`);
const data = await res.json();
const loans = (data.loans || []).filter((loan) => loan.status === "Approved");
select.innerHTML = '<option value="">Select approved loan</option>';
loans.forEach((loan) => {
const option = document.createElement("option");
option.value = loan.id;
option.innerText = `${loan.member_username} - ${loan.loan_type} - ${formatCurrency(loan.amount)}`;
select.appendChild(option);
});
} catch (e) {
select.innerHTML = '<option value="">Failed to load approved loans</option>';
}
}

async function loadPayments() {
const body = document.getElementById("paymentTableBody");
if (!body) return;
body.innerHTML = "";
try {
const res = await fetch(`${API_BASE}/payments`);
const data = await res.json();
const payments = data.payments || [];
payments.forEach((payment) => {
const tr = document.createElement("tr");
tr.innerHTML = `<td>${formatDisplayDate(payment.payment_date)}</td><td>${payment.member_username}</td><td>${payment.loan_type}</td><td>${formatCurrency(payment.amount_paid)}</td>`;
body.appendChild(tr);
});
if (payments.length === 0) {
body.innerHTML = `<tr><td colspan="4">No payments recorded yet.</td></tr>`;
}
} catch (e) {
body.innerHTML = `<tr><td colspan="4">Failed to load payments.</td></tr>`;
}
}

async function loadLoanReport() {
const tbody = document.getElementById("loanReportTbody");
const totalLoansReleased = document.getElementById("totalLoansReleased");
if (!tbody) return;
tbody.innerHTML = "";
try {
const res = await fetch(`${API_BASE}/loans`);
const data = await res.json();
const loans = data.loans || [];
let totalReleased = 0;
loans.forEach((loan) => {
if (loan.status === "Approved") {
totalReleased += Number(loan.amount || 0);
}
let statusText = loan.status === "Approved" ? "Active" : loan.status;
const tr = document.createElement("tr");
tr.innerHTML = `<td>${loan.member_username}</td><td>${formatCurrency(loan.amount)}</td><td class="${loan.status === "Approved" ? "approved" : (loan.status === "Pending" ? "pending" : "")}">${statusText}</td>`;
tbody.appendChild(tr);
});
if (totalLoansReleased) {
totalLoansReleased.innerText = formatCurrency(totalReleased);
}
if (loans.length === 0) {
tbody.innerHTML = `<tr><td colspan="3">No loans yet.</td></tr>`;
}
} catch (e) {
tbody.innerHTML = `<tr><td colspan="3">Failed to load loan report.</td></tr>`;
}
}

async function savePayment() {
const loanId = document.getElementById("paymentLoanId")?.value || "";
const amountPaid = document.getElementById("paymentAmount")?.value || "";
const paymentDate = document.getElementById("paymentDate")?.value || new Date().toISOString().slice(0, 10);
if (!loanId || !amountPaid || Number(amountPaid) <= 0) {
alert("Please select a loan and enter a valid payment amount.");
return;
}
try {
const res = await fetch(`${API_BASE}/payments`, {
method: "POST",
headers: { "Content-Type": "application/json" },
body: JSON.stringify({ loan_id: loanId, amount_paid: amountPaid, payment_date: paymentDate })
});
const data = await res.json();
if (data.success) {
alert("Payment recorded.");
document.getElementById("paymentAmount").value = "";
await loadPaymentSummary();
await loadPayments();
await loadLoanOptions();
} else {
alert(data.message || "Failed to record payment.");
}
} catch (e) {
alert("Cannot connect to server.");
}
}

window.onload = function () {
document.getElementById("paymentDate").value = new Date().toISOString().slice(0, 10);
loadPaymentSummary();
loadLoanOptions();
loadPayments();
loadLoanReport();
};

function generatePDF() {
const previewContent = document.getElementById("reportPreviewContent");
const downloadButton = document.getElementById("downloadPdfButton");
const monthlyRows = Array.from(document.querySelectorAll("#monthlyTableBody tr"))
.map((tr) => {
const cells = tr.querySelectorAll("td");
if (cells.length < 3) return null;
return {
month: cells[0].innerText,
total: cells[1].innerText,
count: cells[2].innerText
};
})
.filter(Boolean);
const loanRows = Array.from(document.querySelectorAll("#loanReportTbody tr"))
.map((tr) => {
const cells = tr.querySelectorAll("td");
if (cells.length < 3) return null;
return {
member: cells[0].innerText,
amount: cells[1].innerText,
status: cells[2].innerText
};
})
.filter(Boolean);

reportPreviewData = {
generatedAt: new Date().toLocaleString("en-PH"),
monthlyRows,
loanRows
};

if (!previewContent) return;

previewContent.innerHTML = `
<h3 style="margin-top:0;">NAgCO Financial Report</h3>
<p><strong>Generated:</strong> ${escapeHtml(reportPreviewData.generatedAt)}</p>
<h4>Monthly Collection</h4>
${monthlyRows.length ? `
<table style="width:100%; border-collapse:collapse; margin-bottom:16px;">
<tr>
<th style="text-align:left; padding:8px; border-bottom:1px solid #ddd;">Month</th>
<th style="text-align:left; padding:8px; border-bottom:1px solid #ddd;">Total Collection</th>
<th style="text-align:left; padding:8px; border-bottom:1px solid #ddd;">Payment Count</th>
</tr>
${monthlyRows.map((row) => `
<tr>
<td style="padding:8px; border-bottom:1px solid #eee;">${escapeHtml(row.month)}</td>
<td style="padding:8px; border-bottom:1px solid #eee;">${escapeHtml(row.total)}</td>
<td style="padding:8px; border-bottom:1px solid #eee;">${escapeHtml(row.count)}</td>
</tr>
`).join("")}
</table>
` : "<p>No monthly collection data found.</p>"}
<h4>Loan Report</h4>
${loanRows.length ? `
<table style="width:100%; border-collapse:collapse;">
<tr>
<th style="text-align:left; padding:8px; border-bottom:1px solid #ddd;">Member</th>
<th style="text-align:left; padding:8px; border-bottom:1px solid #ddd;">Loan Amount</th>
<th style="text-align:left; padding:8px; border-bottom:1px solid #ddd;">Status</th>
</tr>
${loanRows.map((row) => `
<tr>
<td style="padding:8px; border-bottom:1px solid #eee;">${escapeHtml(row.member)}</td>
<td style="padding:8px; border-bottom:1px solid #eee;">${escapeHtml(row.amount)}</td>
<td style="padding:8px; border-bottom:1px solid #eee;">${escapeHtml(row.status)}</td>
</tr>
`).join("")}
</table>
` : "<p>No loan report data found.</p>"}
`;

if (downloadButton) {
downloadButton.style.display = "inline-block";
}

document.getElementById("reportPreview").scrollIntoView({ behavior: "smooth" });
}

function downloadPreviewPDF() {
if (!reportPreviewData) {
alert('Generate the report preview first.');
return;
}

const { jsPDF } = window.jspdf;
let doc = new jsPDF();
doc.setFontSize(16);
doc.text("NAgCO Financial Report", 20, 20);
doc.setFontSize(12);
doc.text(`Generated: ${reportPreviewData.generatedAt}`, 20, 30);

doc.text("Monthly Collection:", 20, 45);
let y = 55;
if (reportPreviewData.monthlyRows.length === 0) {
doc.text("No monthly collection data found.", 20, y);
y += 10;
} else {
reportPreviewData.monthlyRows.forEach((row) => {
doc.text(`${row.month} - ${row.total} (${row.count} payments)`, 20, y);
y += 10;
});
}

doc.text("Loan Report:", 20, y + 10);
let loanY = y + 20;
if (reportPreviewData.loanRows.length === 0) {
doc.text("No loan report data found.", 20, loanY);
} else {
reportPreviewData.loanRows.forEach((row) => {
doc.text(`${row.member} - ${row.amount} (${row.status})`, 20, loanY);
loanY += 10;
});
}

doc.save("NAgCO_Report.pdf");
}

function logout() {
    localStorage.clear();
    window.location.href = "login.html";
}

function goDashboard() {
    window.location.href = "admin-dashboard.html";
}

function goLoan() {
    window.location.href = "loan-management.html";
}

function goMembers() {
    window.location.href = "members.html";
}

function openProfile() {
    alert("Admin Profile");
}

function showNotifications() {
    alert("Checking new loan requests.");
}
