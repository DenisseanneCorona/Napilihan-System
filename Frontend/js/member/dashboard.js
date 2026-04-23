if(localStorage.getItem("role") !== "member"){
    alert("Member access only!");
    window.location.href = "login.html";
}