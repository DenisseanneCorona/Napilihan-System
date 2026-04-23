
function register(){

    let name = document.getElementById("fullname").value;
    let email = document.getElementById("email").value;
    let password = document.getElementById("password").value;

    if(name || email || password){
        alert("Fill all fields");
        return;
    }

    // CREATE REQUEST OBJECT (ITO ANG KULANG MO)
    let newRequest = {
        name: name,
        email: email,
        password: password,
        status: "pending"
    };

    // SAVE TO REQUESTS (ITO LANG MUNA, HINDI SA USERS)
    let requests = JSON.parse(localStorage.getItem("requests")) || [];
    requests.push(newRequest);
    localStorage.setItem("requests", JSON.stringify(requests));

    alert("Registered! Wait for admin approval.");

    window.location.href = "../pages/login.html";
}