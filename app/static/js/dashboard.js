ocument.addEventListener("DOMContentLoaded", async () => {
  const postList = document.getElementById("post-list");
  const res = await fetch("/api/post/all");
  const posts = await res.json();

  if (!posts.length) {
    postList.innerHTML = `<p>No posts found.</p>`;
    return;
  }

  posts.forEach((post) => {
    const div = document.createElement("div");
    div.className = "post-entry";
    div.innerHTML = `
      <p><strong>@${post.username}</strong> — ${post.timestamp}</p>
      <p>${post.content}</p>
      <hr />
    `;
    postList.appendChild(div);
  });
});