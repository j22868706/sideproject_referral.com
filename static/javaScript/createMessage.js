
function createMessage() {
  const postId = document.getElementById('qid').textContent;
  const token = localStorage.getItem("token");  

  if (postId === "") {
    return;

  } else {        
  fetch(`/api/createMessage/${postId}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`,  
      },
  })
  .then((response) => response.json())
  .then((data) => {
    if (data.error) {
      console.log(data.error)
      return;
    } else {
        window.location.href = '/message';
      }
  })
  .catch((error) => {
      console.error("Error:", error);
  });
}
}
