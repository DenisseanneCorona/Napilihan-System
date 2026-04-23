let pendingOtpChallenge = null;
const API_BASE = "http://127.0.0.1:5000/api";

function finishLogin(data) {
    localStorage.setItem("loggedIn", "true");
    localStorage.setItem("role", data.role || "member");
    localStorage.setItem("currentUsername", data.username);
    localStorage.setItem("currentUser", JSON.stringify({
        fullname: data.fullname || data.username,
        role: data.role || "member"
    }));
    if ((data.role || "member") === "admin") {
        window.location.href = "../pages/admin-dashboard.html";
    } else {
        window.location.href = "../pages/member-dashboard.html";
    }
}

function openTwoFactorModal(challengeId) {
pendingOtpChallenge = challengeId;
document.getElementById("twoFactorCode").value = "";
document.getElementById("twoFactorStatus").innerText = "";
document.getElementById("twoFactorStatus").style.color = "#c62828";
document.getElementById("twoFactorModal").style.display = "block";
}

function closeTwoFactorModal() {
pendingOtpChallenge = null;
document.getElementById("twoFactorModal").style.display = "none";
}

async function submitTwoFactorCode() {
const statusEl = document.getElementById("twoFactorStatus");
const code = document.getElementById("twoFactorCode").value.trim();
if (!pendingOtpChallenge) {
statusEl.innerText = "OTP request expired. Please log in again.";
return;
}
if (!/^\d{6}$/.test(code)) {
statusEl.innerText = "Enter a valid 6-digit OTP.";
return;
}
statusEl.style.color = "#2e7d32";
statusEl.innerText = "Verifying OTP...";
try {
const response = await fetch(`${API_BASE}/login/verify-otp`, {
method: "POST",
headers: { "Content-Type": "application/json" },
body: JSON.stringify({
challenge_id: pendingOtpChallenge,
code: code
})
});
        const data = await response.json();
        if (data.success) {
            closeTwoFactorModal();
            finishLogin(data);
        } else {
statusEl.style.color = "#c62828";
statusEl.innerText = data.message || "Invalid OTP code.";
}
} catch (error) {
statusEl.style.color = "#c62828";
statusEl.innerText = "Cannot connect to server.";
}
}

document.getElementById("loginForm").addEventListener("submit", async function (event) {
event.preventDefault();
const statusEl = document.getElementById("statusMessage");
if (statusEl) statusEl.innerText = "Submitting login...";

const username = document.getElementById("email").value.trim().toLowerCase();
const password = document.getElementById("password").value;

try {
if (statusEl) statusEl.innerText = "Connecting to server...";
const response = await fetch(`${API_BASE}/login`, {
method: "POST",
headers: { "Content-Type": "application/json" },
body: JSON.stringify({ username, password })
});

let data = {};
try {
data = await response.json();
} catch (jsonError) {
data = {};
}

        if (data.success) {
            if (data.requires_otp) {
                if (statusEl) statusEl.innerText = "Password verified. Check your email for the OTP code.";
                openTwoFactorModal(data.challenge_id);
            } else {
                if (statusEl) statusEl.innerText = "Login success. Redirecting...";
                finishLogin(data);
            }
} else if (response.status === 401) {
if (statusEl) statusEl.innerText = data.message || "Invalid login credentials";
alert(data.message || "Invalid login credentials");
} else {
if (statusEl) statusEl.innerText = data.message || "Login failed";
alert(data.message || "Login failed");
}
} catch (error) {
if (statusEl) statusEl.innerText = "Cannot connect to server.";
alert("Cannot connect to server. Make sure backend is running.");
}
});
