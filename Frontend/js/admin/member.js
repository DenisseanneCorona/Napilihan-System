window.onload = function(){

let users = JSON.parse(localStorage.getItem("users")) || [];

let table = document.getElementById("memberTable");

users.forEach((user, index) => {

let row = table.insertRow();

row.insertCell(0).innerText = user.fullname;
row.insertCell(1).innerText = user.email;
row.insertCell(2).innerText = user.status;

row.insertCell(3).innerHTML = `
<button onclick="approve(${index})">Approve</button>
<button onclick="deleteUser(${index})">Delete</button>
`;

});

}
// LOAD MEMBERS
function loadMembers() {
    let users = JSON.parse(localStorage.getItem("users")) || [];

    const table = document.getElementById("membersTableBody");
    table.innerHTML = "";

    users.forEach((user, index) => {
        const row = `
            <tr>
                <td>${user.name}</td>
                <td>${user.email}</td>
                <td style="color: green;">Approved</td>
                <td>—</td>
            </tr>
        `;
        table.innerHTML += row;
    });
}

window.onload = loadMembers;

// ✅ APPROVE USER
function approve(index){

let users = JSON.parse(localStorage.getItem("users"));

users[index].status = "Approved";

localStorage.setItem("users", JSON.stringify(users));

alert("Member Approved");

location.reload();

}

// ❌ DELETE USER
function deleteUser(index){

let users = JSON.parse(localStorage.getItem("users"));

users.splice(index,1);

localStorage.setItem("users", JSON.stringify(users));

alert("Member Deleted");

location.reload();

}