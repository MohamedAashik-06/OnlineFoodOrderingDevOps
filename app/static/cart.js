
const cart = {};

const foodProducts = [
    { id: 1, name: "Classic Burger", price: 159 },
    { id: 2, name: "Italian Pizza", price: 249 },
    { id: 3, name: "Chicken Biryani", price: 220 },
    { id: 4, name: "French Fries", price: 99 },
    { id: 5, name: "Pasta", price: 189 },
    { id: 6, name: "Chocolate Brownie", price: 120 }
];

// ADD TO CART
function addToCart(id) {
    const product = foodProducts.find(item => item.id === id);

    if (!product) return;

    if (cart[id]) {
        cart[id].quantity++;
    } else {
        cart[id] = {
            ...product,
            quantity: 1
        };
    }

    renderCart();
}

// CHANGE QUANTITY
function changeQuantity(id, amount) {
    if (!cart[id]) return;

    cart[id].quantity += amount;

    if (cart[id].quantity <= 0) {
        delete cart[id];
    }

    renderCart();
}

// REMOVE ITEM
function removeItem(id) {
    delete cart[id];
    renderCart();
}

// CLEAR CART
function clearCart() {
    Object.keys(cart).forEach(id => delete cart[id]);
    renderCart();
}

// DISPLAY CART
function renderCart() {
    const cartContainer = document.getElementById("cart-items");
    const totalElement = document.getElementById("cart-total");
    const countElement = document.getElementById("nav-cart-count");

    const items = Object.values(cart);

    if (items.length === 0) {
        cartContainer.innerHTML =
            '<p class="empty-cart">Your cart is empty. Add some delicious food!</p>';
    } else {
        cartContainer.innerHTML = items.map(item => `
            <div class="cart-item">
                <div class="cart-item-info">
                    <h3>${item.name}</h3>
                    <p>₹${item.price} each</p>
                </div>

                <div class="quantity-controls">
                    <button type="button"
                        onclick="changeQuantity(${item.id}, -1)">−</button>

                    <span>${item.quantity}</span>

                    <button type="button"
                        onclick="changeQuantity(${item.id}, 1)">+</button>
                </div>

                <strong>₹${item.price * item.quantity}</strong>

                <button type="button"
                    class="remove-button"
                    onclick="removeItem(${item.id})">
                    Remove
                </button>
            </div>
        `).join("");
    }

    const total = items.reduce(
        (sum, item) => sum + item.price * item.quantity, 0
    );

    const count = items.reduce(
        (sum, item) => sum + item.quantity, 0
    );

    totalElement.textContent = total;
    countElement.textContent = count;
}

// ADD BUTTON EVENTS
document.querySelectorAll(".add-button").forEach(button => {
    button.addEventListener("click", function() {
        const id = Number(this.dataset.id);
        addToCart(id);
    });
});

// CLEAR CART BUTTON
document.getElementById("clear-cart")
    .addEventListener("click", clearCart);

// PLACE ORDER
document.getElementById("order-form")
    .addEventListener("submit", async function(event) {

        event.preventDefault();

        const messageElement = document.getElementById("order-message");

        const name = document.getElementById("customer-name").value.trim();
        const phone = document.getElementById("customer-phone").value.trim();
        const address = document.getElementById("customer-address").value.trim();

        const items = Object.values(cart).map(item => ({
            id: item.id,
            quantity: item.quantity
        }));

        if (items.length === 0) {
            messageElement.textContent =
                "Please add food items to your cart first.";

            messageElement.style.color = "#d64231";

            document.getElementById("cart").scrollIntoView({
                behavior: "smooth"
            });

            return;
        }

        if (!name || !phone || !address) {
            messageElement.textContent =
                "Please fill in all delivery details.";

            messageElement.style.color = "#d64231";
            return;
        }

        if (!/^[0-9]{10}$/.test(phone)) {
            messageElement.textContent =
                "Please enter a valid 10-digit phone number.";

            messageElement.style.color = "#d64231";
            return;
        }

        const orderData = {
            name: name,
            phone: phone,
            address: address,
            items: items
        };

        const submitButton = this.querySelector(".order-button");

        submitButton.disabled = true;
        submitButton.textContent = "Processing Order...";

        messageElement.textContent = "";

        try {
            const response = await fetch("/place-order", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(orderData)
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || "Order submission failed.");
            }

            messageElement.style.color = "#23845b";

            messageElement.innerHTML = `
                <strong>Order placed successfully!</strong><br>
                Thank you, ${result.customer}.<br><br>

                <strong style="font-size:18px;">
                    Order ID: #${result.order_id}
                </strong><br>

                Your order total is ₹${result.total}.<br><br>

                <a href="/track-order"
                   style="display:inline-block;
                          margin-top:10px;
                          padding:10px 18px;
                          background:#23845b;
                          color:white;
                          border-radius:8px;
                          text-decoration:none;">
                    Track Your Order
                </a>
            `;

            clearCart();
            this.reset();

            messageElement.scrollIntoView({
                behavior: "smooth",
                block: "center"
            });

        } catch (error) {
            messageElement.style.color = "#d64231";
            messageElement.textContent =
                error.message || "Something went wrong. Please try again.";

        } finally {
            submitButton.disabled = false;
            submitButton.textContent = "Place My Order →";
        }
    });

// INITIAL DISPLAY
renderCart();
