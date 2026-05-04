const API = "http://127.0.0.1:5000";

// Load promotions on page load
window.onload = () => {
    loadRestaurants();
    loadPromotions();
    loadRestaurant();
};

// Load restaurant info
function loadRestaurant() {
    fetch(`${API}/api/restaurant`, { credentials: "include" })
        .then(r => r.json())
        .then(data => {
            document.getElementById("restName").value = data.name || "";
            document.getElementById("restAddress").value = data.address || "";
            document.getElementById("restHours").value = data.hours || "";
            document.getElementById("restImage").value = data.image_url || "";
            document.getElementById("restDescription").value = data.description || "";
        });
}


function loadRestaurants() {
    fetch(`${API}/api/owner/restaurants`, {
        credentials: "include"
    })
        .then(r => r.json())
        .then(data => {
            const list = document.getElementById("restaurantList");
            list.innerHTML = "";

            data.restaurants.forEach(r => {
                const li = document.createElement("li");
                li.innerHTML = `
                <strong>${r.name}</strong><br>
                Promotions used: ${r.promo_uses}<br>
                Traffic increase: <span style="color: green; font-weight: bold;">+${r.traffic_increase}%</span>
            `;
                list.appendChild(li);
            });
        });
}



// Save restaurant info
function saveRestaurant() {
    const body = {
        name: document.getElementById("restName").value,
        address: document.getElementById("restAddress").value,
        hours: document.getElementById("restHours").value,
        image_url: document.getElementById("restImage").value,
        description: document.getElementById("restDescription").value
    };

    fetch(`${API}/api/restaurant/save`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
    })
        .then(r => r.json())
        .then(() => alert("Restaurant info saved!"));
}

// Load promotions
function loadPromotions() {
    fetch(`${API}/api/promotions/all`)
        .then(r => r.json())
        .then(data => {
            const list = document.getElementById("promoList");
            list.innerHTML = "";
            data.promotions.forEach((p, i) => {
                const li = document.createElement("li");
                li.textContent = p;
                list.appendChild(li);
            });
        });
}

// Add promotion
function addPromotion() {
    const text = document.getElementById("promoInput").value;

    fetch(`${API}/api/promotions/add`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ promotion: text })
    })
        .then(r => r.json())
        .then(() => {
            document.getElementById("promoInput").value = "";
            loadPromotions();
        });
}

// Logout
function logout() {
    fetch(`${API}/logout`, { credentials: "include" })
        .then(() => window.location.href = "/");
}


function goHome() {
    window.location.href = "/home";
}
