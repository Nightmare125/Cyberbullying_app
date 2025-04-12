document.addEventListener("DOMContentLoaded", () => {
  const postForm = document.getElementById("post-form");
  const feedback = document.getElementById("post-feedback");

  if (!postForm) return;

  postForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const content = new FormData(postForm).get("content");
    const username = localStorage.getItem("username");

    if (!username) {
      feedback.innerHTML = "<p style='color:red'>Please log in to post.</p>";
      return;
    }

    const res = await fetch("/api/post", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ Username: username, Content: content })
    });

    const result = await res.json();

    if (res.ok && result.is_abusive) {
      feedback.innerHTML = `<p style='color:red'><strong>${result.message}</strong></p>`;
    } else if (res.ok) {
      feedback.innerHTML = `<p style='color:green'><strong>${username}:</strong> ${result.message}</p>`;
      setTimeout(() => (window.location.href = "/posts"), 1500);
    } else {
      feedback.innerHTML = `<p style='color:red'>${result.detail || "Submission failed."}</p>`;
    }
  });
});
