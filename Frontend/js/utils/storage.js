// storage.js

export function saveUser(user){
    localStorage.setItem("user", JSON.stringify(user));
}

export function getUser(){
    return JSON.parse(localStorage.getItem("user"));
}

export function setSession(role){
    localStorage.setItem("loggedIn", "true");
    localStorage.setItem("role", role);
}

export function logout(){
    localStorage.clear();
}