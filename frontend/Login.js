document.addEventListener("DOMContentLoaded", () => {
    const loginForm = document.querySelector("form");

    // Spoof credentials
    const dummyUsers = [
        { username: "admin", password: "admin123" },
        { username: "testuser", password: "test123" },
    ];

    loginForm.addEventListener("submit", (event) => {
        event.preventDefault(); // Prevent form submission
        
        // Collect user inputs
        const username = loginForm.querySelector("input[type='text']").value.trim();
        const password = loginForm.querySelector("input[type='password']").value.trim();

        // Check credentials against dummy users
        const user = dummyUsers.find(u => u.username === username && u.password === password);

        if (user) {
            // Simulate successful login
            alert("Login successful!");
            window.location.href = "./HomePage.html"; // Redirect to homepage
        } else {
            // Show error message for invalid credentials
            alert("Invalid username or password. Please try again.");
        }
    });
});
