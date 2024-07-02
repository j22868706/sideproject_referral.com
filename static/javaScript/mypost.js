function checkToken (){
    const checkToken = localStorage.getItem("token");
    if (!checkToken) {
        window.location.href = '/'; }
    }
    
window.addEventListener('load', checkToken);

function loadingMyPost() {
    const token = localStorage.getItem("token");

    fetch("/api/mypost", {
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
                const jobPostElement = document.createElement("div");
                jobPostElement.id = "postID";
                jobPostElement.classList.add("card");

                // Update the content of each element
                jobPostElement.innerHTML = `
                <div class="card-left blue-bg">
                <img id="applicantIcon" src="${jobPost.memberIcon}">
                </div>
            <div class="card-center">
                <h3>${jobPost.job_title}</h3>
                <p class="card-detail">${jobPost.job_description}</p>
                <p class="card-loc"><ion-icon name="location-outline"></ion-icon> Job Location:  ${jobPost.job_zipcode}<span> ${jobPost.job_city}</span></p>
                <p class="card-loc"><ion-icon name=today-outline></ion-icon> Post time: ${jobPost.post_time}</p>
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
                        const response = await fetch(`/api/applicant/${postId}`);
                    if (!response.ok) {
                        throw new Error(`HTTP error! Status: ${response.status}`);
                    }
                    const data = await response.json();
                    console.log(data);
                
                        const applicantContainer = document.getElementById("detail");
                    applicantContainer.innerHTML = '';

                

                    if (Array.isArray(data.data) && data.data.length > 0) {
                        // Assuming the response contains an array of job posts, iterate over them
                            data.data.forEach((applicant, index) => {
                        // Create elements for each applicant
                            const individualApplicantContainer = document.createElement('div');
                            individualApplicantContainer.classList.add("card");
                            individualApplicantContainer.style.marginBottom = "10px";

                            individualApplicantContainer.innerHTML = `
                                <div style="display: none;" id="applicantPostId_${index}">${applicant.postId}</div>
                                <div style="display: none;" id="applicantEmail_${index}">${applicant.applicantEmail}</div>

                                <div class="card-left blue-bg">
                                    <img id="applicantIcon" src="${applicant.memberIcon}">
                                </div>
                                <div class="card-center">
                                    <h3>Employee:</h3>
                                    <p class="card-detail" id="applicantName">${applicant.memberId}</p>
                                    <div style="color: #5f5f5f;" onclick="createMessage(${index})">
                                        <ion-icon name="chatbubbles-outline"></ion-icon>  Send a message
                                    </div>  
                                </div>
                                <div class="card-right">
                                    <button class="btn-apply" style="margin-bottom: 10px; display: ${applicant.positionStatus == 1 ? 'block' : 'none'};" onclick="confirmPosition(${index})">Agree</button>
                                    <button class="btn-apply" style="margin-bottom: 10px; display: ${applicant.positionStatus == 2 ? 'block' : 'none'};" onclick="cancelConfirmPosition(${index})">Cancel Agreement</button>
                                    <button class="btn-cancel" style="margin-bottom: 10px; display: ${applicant.positionStatus == 1 ? 'block' : 'none'};" onclick="declinePosition(${index})">Decline</button>
                                    <button class="btn-cancel" style="margin-bottom: 10px; display: ${applicant.positionStatus == 3 ? 'block' : 'none'};" onclick="cancelDeclinePosition(${index})">Withdraw Decline</button>
                                </div>
                            `;

                            applicantContainer.appendChild(individualApplicantContainer);
                        });
                    } else {
                        applicantContainer.innerHTML = '<p style="text-align: center;">No applicants have applied for this position yet.</p>'
                        }
                    } catch (error) {
                        console.error("Error fetching job details:", error.message);
                    }
                });

                            });
        } else {
// Handle the case when there are no job posts
            jobListContainer.innerHTML = '<p style="text-align: center;">No job positions have been posted yet.</p>';
        }
    })
    .catch((error) => {
        console.error("Error fetching job posts:", error.message);
    });
}
  

  function declinePosition(index) {
    const postId = document.getElementById(`applicantPostId_${index}`).textContent;
    const applicaitonEmail = document.getElementById(`applicantEmail_${index}`).textContent;

   const token = localStorage.getItem("token");  
  
   if (postId === "") {
    return;
  
    } else {        
    fetch(`/api/declinePosition/${postId}/${applicaitonEmail}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,  
        },
    })
    .then((response) => response.json())
    .then((data) => {
      console.log(data)
      if (data.error) {
        alert(data.message);

      } else {
        alert(data.message);

  
        setTimeout(function () {
                            window.location.href = '/mypost';
                        }, 3000); 
        }
    })
    .catch((error) => {
        console.error("Error:", error);
    });
  }
  }

  function cancelDeclinePosition(index) {
    const postId = document.getElementById(`applicantPostId_${index}`).textContent;
    const applicaitonEmail = document.getElementById(`applicantEmail_${index}`).textContent;

   const token = localStorage.getItem("token");  
  
   if (postId === "") {
    return;
  
    } else {        
    fetch(`/api/cancelDeclinePosition/${postId}/${applicaitonEmail}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,  
        },
    })
    .then((response) => response.json())
    .then((data) => {
      console.log(data)
      if (data.error) {
        alert(data.message);

      } else {
        alert(data.message);

  
        setTimeout(function () {
                            window.location.href = '/mypost';
                        }, 3000); 
        }
    })
    .catch((error) => {
        console.error("Error:", error);
    });
  }
}

function confirmPosition(index) {
    const postId = document.getElementById(`applicantPostId_${index}`).textContent;
    const applicaitonEmail = document.getElementById(`applicantEmail_${index}`).textContent;

   const token = localStorage.getItem("token");  
  
   if (postId === "") {
    return;
  
    } else {        
    fetch(`/api/confirmPosition/${postId}/${applicaitonEmail}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,  
        },
    })
    .then((response) => response.json())
    .then((data) => {
      console.log(data)
      if (data.error) {
        alert(data.message);

      } else {
        alert(data.message);

  
        setTimeout(function () {
                            window.location.href = '/mypost';
                        }, 3000); 
        }
    })
    .catch((error) => {
        console.error("Error:", error);
    });
  }
  }

  function cancelConfirmPosition(index) {
    const postId = document.getElementById(`applicantPostId_${index}`).textContent;
    const applicaitonEmail = document.getElementById(`applicantEmail_${index}`).textContent;

   const token = localStorage.getItem("token");  
  
   if (postId === "") {
    return;
  
    } else {        
    fetch(`/api/cancelConfirmPosition/${postId}/${applicaitonEmail}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,  
        },
    })
    .then((response) => response.json())
    .then((data) => {
      console.log(data)
      if (data.error) {
        alert(data.message);

      } else {
        alert(data.message);

  
        setTimeout(function () {
                            window.location.href = '/mypost';
                        }, 3000); 
        }
    })
    .catch((error) => {
        console.error("Error:", error);
    });
  }
}

loadingMyPost();


function createMessage(index) {
    const postId = document.getElementById(`applicantPostId_${index}`).textContent;
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
                console.log(data.error);
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

