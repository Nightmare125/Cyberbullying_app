document.addEventListener("DOMContentLoaded", () => {
  const postList = document.getElementById("post-list");

  async function loadPosts() {
    const res = await fetch("/api/post/all");
    const data = await res.json();
    const posts = data.posts;

    if (!posts.length) {
      postList.innerHTML = "<p>No posts found.</p>";
      return;
    }

    postList.innerHTML = posts.map((post) => `
  <div class="post-card" data-id="${post.post_id}">
    <p><strong>@${post.username}</strong> — ${post.timestamp}</p>
    <p>${post.content}</p>
    <div class="post-actions text-center">
      <button class="btn-report small-report-btn" onclick="reportPost(${post.post_id})">Report</button>
    </div>
    <hr>
  </div>
`).join('');

  }

  // Define the report action
  window.reportPost = async function(postId) {
    const confirmed = confirm("Report this post?");
    if (!confirmed) return;
  
    const res = await fetch(`/api/report/${postId}`, { method: "POST" });
    const json = await res.json();
  
    if (res.ok) {
      alert("Post reported.");
      const postElement = document.querySelector(`.post-card[data-id="${postId}"]`);
      if (postElement) {
        postElement.classList.add("reported-post");
      }
    } else {
      alert(json.detail || "Error reporting post.");
    }
  }

  loadPosts();
});
