const API_BASE = "http://127.0.0.1:5000";

function login() {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    fetch(`${API_BASE}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
    })
        .then(res => res.json())
        .then(data => {
            if (data.status === "logged_in") {
                window.location.href = "/home";
            } else {
                alert("Invalid login");
            }
        });
}


function continueAsGuest() {
    fetch(`${API_BASE}/guest`, {
        credentials: "include"
    })
        .then(() => {
            window.location.href = "/home";
        });
}