function checkToken (){
    const checkToken = localStorage.getItem("token");
    if (!checkToken) {
        window.location.href = '/'; }
    }
    
window.addEventListener('load', checkToken);

function loadingFav() {
    const token = localStorage.getItem("token");              

    fetch("/api/saveposition", {
        headers: {
            "Authorization": `Bearer ${token}`,  
        },
    })
    .then((response) => {
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
    })
    .then((data) => {
        console.log(data);

        const jobListContainer = document.getElementById("fav_list");

        // Check if data is an array and not empty
        if (Array.isArray(data) && data.length > 0) {
            // Iterate over the array of saved job posts
            data.forEach((jobPost) => {
                // Create elements for each saved job post
                const jobPostElement = document.createElement("div");
                jobPostElement.id = "postID";
                jobPostElement.classList.add("card");

                // Update the content of each element
                jobPostElement.innerHTML = `
                <div class="card-left blue-bg">
                <img src="${jobPost.memberIcon}">
            </div>
            <div class="card-center">
                <h3>${jobPost.job_title}</h3>
                <p class="card-detail">${jobPost.job_description}</p>
                <p class="card-loc"><ion-icon name="location-outline"></ion-icon> Job Location:  ${jobPost.job_zipcode}<span> ${jobPost.job_city}</span></p>
                <p class="card-loc"><ion-icon name=today-outline></ion-icon> Post Time: ${jobPost.post_time}</p>
            </div>
            <div class="card-right">
                <div class="card-tag">
                    <h5>Job Date</h5>
                    <p id="job_date"><ion-icon name=today-outline></ion-icon>${jobPost.job_date}</p>
                    <p><ion-icon name="briefcase-outline"></ion-icon>${jobPost.job_start_time} - ${jobPost.job_end_time}</p>
                </div>
                <div class="card-salary">
                    <p><b>Salary Amount</b><span class="card-salary-font">  ${jobPost.job_salary}  </span></p>
                </div>
            </div>
                `;
                jobListContainer.appendChild(jobPostElement);

                jobPostElement.addEventListener("click", async function () {
                    const postId = jobPost.post_id;
  
                    try {
                      const response = await fetch(`/api/jobPost/${postId}`);
                        if (!response.ok) {
                            throw new Error(`HTTP error! Status: ${response.status}`);
                        }
                        const data = await response.json();
                        console.log(data);
                        const qid = document.getElementById("qid");
                        const qTitle = document.getElementById("qTitle");
                        const qContent = document.getElementById("qContent");
                        const qLocation = document.getElementById("qLocation");
                        const qPayMethod = document.getElementById("qPayMethod");
                        const qPayDate = document.getElementById("qPayDate");
                        const qWorkingDate = document.getElementById("qWorkingDate");
                        const qWorkingHour = document.getElementById("qWorkingHour");
                        const qNumPosition = document.getElementById("qNumPosition");
                        const qOthers = document.getElementById("qOthers");
                        const employeeName = document.getElementById("employeeName")

                        employeeName.textContent = data.data.memberID;
                        qid.textContent = data.data.postId;
                        qTitle.textContent = data.data.job_title;
                        qContent.textContent = data.data.job_description;
                        qLocation.textContent = `${data.data.job_zipcode}    ${data.data.job_city}   ${data.data.job_location}`;
                        qPayMethod.textContent = data.data.pay_method;
                        qPayDate.textContent = data.data.pay_date;
                        qWorkingDate.textContent = data.data.job_date;
                        qWorkingHour.textContent = `${data.data.job_start_time}  -   ${data.data.job_end_time}`;
                        qNumPosition.textContent = data.data.number_of_job_positions;
                        qOthers.textContent = data.data.job_others; 
                    } catch (error) {
                        console.error("Error fetching job details:", error.message);
                    }
                });
            });
        } else {
            // Handle the case when there are no job posts
            jobListContainer.innerHTML = '<p style="text-align: center;">No jobs saved yet</p>'
        }
    })
    .catch((error) => {
        console.error("Error fetching job posts:", error.message);
    });
  }


  document.getElementById('applyBtn').addEventListener('click', applyPosition);
  function applyPosition() {
    const postId = document.getElementById('qid').textContent;
    const token = localStorage.getItem("token");

    if (postId === "" ) {
      return;
    } else {fetch(`/api/jobApply/${postId}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,  
        },
    })
    .then((response) => response.json())
    .then((data) => {
      console.log(data)
      const messageBox = document.querySelector(".message_box");
      messageBox.textContent = data.message;
      if (data.error) {
        messageBox.style.color = "red";
        messageBox.style.display = "block";
      } else {
        messageBox.style.color = "green";
        messageBox.style.display = "block";
  
        // Wait for 3 seconds and then redirect to the homepage
        setTimeout(function () {
            window.location.href = '/';
        }, 3000); // 3000 milliseconds = 3 seconds
    }
    })
    .catch((error) => {
        console.error("Error:", error);
    });
  }}

  document.getElementById('cancelBtn').addEventListener('click', cancelSavePosition);
  function cancelSavePosition() {
    const postId = document.getElementById('qid').textContent;
    const token = localStorage.getItem("token");
    
    if (postId === "" ) {
        return;
    } else { fetch(`/api/jobPost/${postId}`, {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,  
        },
    })
    .then((response) => response.json())
    .then((data) => {
      console.log(data)
      const messageBox = document.querySelector(".message_box");
      messageBox.textContent = data.message;
      if (data.error) {
        messageBox.style.color = "red";
        messageBox.style.display = "block";
      } else {
        messageBox.style.color = "green";
        messageBox.style.display = "block";

        // Wait for 3 seconds and then redirect to the homepage
        setTimeout(function () {
            window.location.href = '/favorite';
        }, 3000); // 3000 milliseconds = 3 seconds
    }
    })
    .catch((error) => {
        console.error("Error:", error);
    });
}}

loadingFav();

