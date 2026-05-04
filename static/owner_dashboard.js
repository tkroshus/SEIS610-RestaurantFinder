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

                <input type="number" id="diners-${r.id}" placeholder="Add additional promotion uses">
                <button onclick="saveDiners(${r.id})">Save</button>
            `;
                list.appendChild(li);
            });
        });
}



// Save restaurant info
function saveRestaurant() {
    const payload = {
        name: document.getElementById("restName").value,
        address: document.getElementById("restAddress").value,
    };

    fetch(`${API}/api/owner/restaurant`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify(payload)
    })
    .then(r => r.json())
    .then(data => {
        console.log("Saved:", data);

        // ⭐ THIS IS THE IMPORTANT PART
        loadRestaurants();

        // Optional: clear form
        document.getElementById("restName").value = "";
        document.getElementById("restAddress").value = "";
        document.getElementById("restHours").value = "";
        document.getElementById("restImage").value = "";
        document.getElementById("restDescription").value = "";
    });
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


// Save diners count for a restaurant
function saveDiners(id) {
    const value = document.getElementById(`diners-${id}`).value;

    fetch(`${API}/api/owner/restaurant/diners`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ id: id, diners: Number(value) })
    })
    .then(r => r.json())
    .then(data => {
        console.log("Updated promotions used:", data);
        loadRestaurants(); // refresh UI
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
