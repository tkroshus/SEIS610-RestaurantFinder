const API_BASE = "http://127.0.0.1:5000";
let promoIndex = 0;
let promoList = [];
let lastPromoJSON = "";

// Load promotion on page load -- added /all
window.onload = () => {
    loadPromotions();
    fetch(`${API_BASE}/check_login`, {
        credentials: "include"
    })
        .then(res => res.json())
        .then(data => {
            const userTypeDropdown = document.getElementById("userTypeContainer");
            const ownerPromoBox = document.getElementById("ownerPromoBox");
            const logoutButton = document.getElementById("logoutButton");
            const guestLoginButton = document.getElementById("guestLoginButton");

            if (!userTypeDropdown || !ownerPromoBox || !logoutButton || !guestLoginButton) {
                return; // We are on login.html, not home.html
            }

            if (data.is_owner) {
                // Owner logged in
                userTypeDropdown.style.display = "block";
                ownerPromoBox.style.display = "block";
                logoutButton.style.display = "block";
                guestLoginButton.style.display = "none";
            }
            else if (data.is_guest) {
                // Guest mode
                userTypeDropdown.style.display = "none";
                ownerPromoBox.style.display = "none";
                logoutButton.style.display = "none";
                guestLoginButton.style.display = "block";
            }
            else {
                // No session → redirect to login page
                window.location.href = "/";
            }
        });
};


// Cycle through promotions
function startPromotionCycle() {
    if (!promoList || promoList.length === 0) {
        console.log("promoList =", promoList);
        console.warn("No promotions available.");
        return;
    }

    // Show first promotion immediately
    document.getElementById("promoText").innerText = promoList[promoIndex];
    document.getElementById("promotionArea").style.display = "block";

    // Cycle every 5 seconds
    setInterval(() => {
        promoIndex = (promoIndex + 1) % promoList.length;
        document.getElementById("promoText").innerText = promoList[promoIndex];
    }, 5000);
}

// Search restaurants
function searchRestaurants() {
    const quality = document.getElementById("quality").value;
    const budget = document.getElementById("budget").value;
    const distance = document.getElementById("distance").value;

    fetch(`${API_BASE}/api/restaurants?quality=${quality}&budget=${budget}&distance=${distance}`)
        .then(res => res.json())
        .then(data => {
            console.log("API returned:", data);
            renderResults(data);
        })
        .catch(err => console.error("Search error:", err));
}

// Exploration mode
function explore() {
    fetch(`${API_BASE}/api/explore`)
        .then(res => res.json())
        .then(data => renderResults([data]))
        .catch(err => console.error("Explore error:", err));
}

// Render results
function renderResults(list) {
    const container = document.getElementById("results");
    container.innerHTML = "";

    if (list.length === 0) {
        container.innerHTML = "<p>No restaurants found.</p>";
        return;
    }

    list.forEach(r => {
        const div = document.createElement("div");
        div.className = "restaurant";
        div.innerHTML = `
                <strong>${r.name}</strong><br>
                Rating: ${r.rating}★<br>
                Price: ${r.price}<br>
                Distance: ${r.distance} miles<br>
                Address: ${r.address}<br>
                <a href="${r.url}" target="_blank">View on Yelp</a>
            `;
        container.appendChild(div);
    });
}

// Handle user type change
function handleUserTypeChange() {
    const type = document.getElementById("userType").value;

    if (type === "owner") {
        document.getElementById("ownerPromoBox").style.display = "block";
    } else {
        document.getElementById("ownerPromoBox").style.display = "none";
    }
}

// Submit promotion
function submitPromotion() {
    const text = document.getElementById("promoInput").value;

    fetch(`${API_BASE}/api/promotions/add`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ promotion: text })
    })
        .then(res => res.json())
        .then(data => {
            alert("Promotion added!");
            document.getElementById("promoInput").value = "";
        })
        .catch(err => console.error("Promotion submit error:", err));
}


function logout() {
    fetch(`${API_BASE}/logout`)
        .then(res => res.json())
        .then(data => {
            window.location.href = "/";  // back to login page
        });
}


function goToLogin() {
    window.location.href = "/";
}


function loadPromotions() {
    fetch(`${API_BASE}/api/promotions/all`)
        .then(res => res.json())
        .then(data => {
            const newPromoJSON = JSON.stringify(data.promotions);

            // Only update if promotions actually changed
            if (newPromoJSON !== lastPromoJSON) {
                console.log("Promotions updated:", data.promotions);

                promoList = data.promotions;
                lastPromoJSON = newPromoJSON;
                promoIndex = 0; // restart cycle
                startPromotionCycle();
            }
        });
}


// check login
fetch(`${API_BASE}/check_login`)
    .then(res => res.json())
    .then(data => {
        if (data.is_owner) {
            document.getElementById("logoutButton").style.display = "block";
            document.getElementById("ownerDashboardButton").style.display = "block";
            document.getElementById("guestLoginButton").style.display = "none";
        } else {
            document.getElementById("logoutButton").style.display = "none";
            document.getElementById("ownerDashboardButton").style.display = "none"
            document.getElementById("guestLoginButton").style.display = "block";
        }
    });


