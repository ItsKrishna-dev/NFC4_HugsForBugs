document.addEventListener("DOMContentLoaded", () => {
    const loginForm = document.getElementById("loginForm");

    loginForm.addEventListener("submit", async (event) => {
        event.preventDefault(); // Prevent form submission
        
        // Collect user inputs
        const email = document.getElementById("email").value.trim();
        const password = document.getElementById("password").value.trim();

        try {
            const response = await fetch('http://localhost:8000/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email: email,
                    password: password
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                // Store user data in localStorage
                localStorage.setItem('userData', JSON.stringify(data.user_data));
                alert("Login successful!");
                window.location.href = "./chat.html"; // Redirect to chat page
            } else {
                alert("Login failed: " + data.detail);
            }
        } catch (error) {
            console.error('Error:', error);
            alert("Login failed. Please try again.");
        }
    });
});
