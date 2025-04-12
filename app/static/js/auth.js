// static/js/auth.js
const loginForm = document.getElementById("login-form");
const registerForm = document.getElementById("register-form");
const loginFeedback = document.getElementById("login-feedback");



if (registerForm) {
  registerForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const isAdminCheckbox = document.getElementById("register-is-admin");
    const isAdmin = isAdminCheckbox && isAdminCheckbox.checked;

    // ✅ Log to confirm value (you can remove this after testing)
    console.log("🧠 is_admin:", isAdmin);
    const data = Object.fromEntries(new FormData(registerForm));
    data.is_admin = isAdmin; // Add is_admin to the data object
    const res = await fetch("/api/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    });
    const json = await res.json();
    alert(json.message || json.detail);
    if (res.ok) {
      localStorage.setItem("username", json.username);
      localStorage.setItem("is_admin", json.is_admin);
      if (json.is_admin) {
        window.location.href = "/reports";
      } 
      else {
        window.location.href = "/posts/create";
      }
    }
    else {
      alert(json.detail || "Registration failed");
    }
  });
}

if (loginForm) {
  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const data = Object.fromEntries(new FormData(loginForm));
    console.log("Submitting login:", data);
    const res = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    });
    const json = await res.json();
    console.log("Login response:", json);

    if (res.ok) {
      localStorage.setItem("username", json.username);
      localStorage.setItem("is_admin", json.is_admin);
      if (json.is_admin) {
        window.location.href = "/reports";
      } else {
        window.location.href = "/posts/create";
      }
    } else {
      loginFeedback.innerHTML = `<p style="color:red">${json.detail || "Login failed"}</p>`;
    }
  });
};
