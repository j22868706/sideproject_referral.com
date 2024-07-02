window.addEventListener('load', checkUserStatus);

function checkUserStatus() {
    const token = localStorage.getItem("token");
    const headers = token
      ? { Authorization: `Bearer ${token}` }
      : {}; 
  
    fetch('/api/user/auth', {
      method: 'GET',
      headers: headers
    })
      .then(response => {
        if (response.status === 200) {
          return response.json();
        } else {
          throw new Error('请求失败');
        }
      })
      .then(data => {
        let menuSignin = document.querySelector(".menu_signin");
        let menuFanpage = document.querySelector(".menu_fanpage");
        let menuMessage = document.querySelector(".menu_message");
        let menuSchedule = document.querySelector(".menu_schedule");
        let menuMypost = document.querySelector(".menu_mypost");
        let menuFavorite = document.querySelector(".menu_favorite");
        let menuLogout = document.querySelector(".menu_logout")
  
        if (data && data.data !== null) {
            menuSignin.style.display = "none";
            menuFanpage.style.display = "block";
            menuMessage.style.display = "block";
            menuSchedule.style.display = "block";
            menuMypost.style.display = "block";
            menuFavorite.style.display = "block";
            menuLogout.style.display = "block";
        } else {
            menuSignin.style.display = "block";
            menuFanpage.style.display = "none";
            menuMessage.style.display = "none";
            menuSchedule.style.display = "none";
            menuMypost.style.display = "none";
            menuFavorite.style.display = "none";
            menuLogout.style.display = "none";
        }
      })
      .catch(error => {
        console.error('獲取用戶時出現錯誤：', error);
      });
  }

// redirect to register.html
const registerPage = document.getElementById('registerPage');

// type /register for redircting to the register.html
registerPage.addEventListener("click", function() {
    window.location.href = '/register';
});
// Function to load job posts
function loadingJob() {
  // Proceed with the fetch request
  fetch("/api/jobPost", {
      method: "GET",
  })
  .then((response) => {
      if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
      }
      return response.json();
  })
  .then((data) => {
      // Assuming you have a container element with the ID "job_list"
      const jobListContainer = document.getElementById("job_list");

      // Check if data is an array and not empty
      if (Array.isArray(data) && data.length > 0) {
          // Iterate over the array of job posts
          data.forEach((jobPost) => {
              // Create elements for each job post
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
              <p class="card-loc"><ion-icon name="location-outline"></ion-icon> Job Location: ${jobPost.job_zipcode}<span> ${jobPost.job_city}</span></p>
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

              // Append the job post element to the main job list container
              jobListContainer.appendChild(jobPostElement);

              jobPostElement.addEventListener("click", async function () {
                  const postId = jobPost.post_id;

                  try {

                    const response = await fetch(`/api/jobPost/${postId}`);
                      if (!response.ok) {
                          throw new Error(`HTTP error! Status: ${response.status}`);
                      }
                      const data = await response.json();
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
          jobListContainer.innerHTML = '<p>No job posts available.</p>';
      }
  })
  .catch((error) => {
      console.error("Error fetching job posts:", error.message);
  });
}


document.getElementById('saveBtn').addEventListener('click', savePosition);
function savePosition() {
    const postId = document.getElementById('qid').textContent;
  const token = localStorage.getItem("token");              


  if (postId === "") {
    return;

  } else { 
  fetch(`/api/jobPost/${postId}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`,  
      },
      // body: JSON.stringify({ postId: postId }),
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

    setTimeout(function () {
        window.location.href = '/';
    }, 5000); 

        }
  })
  .catch((error) => {
      console.error("Error:", error);
  });
}
}

document.getElementById('applyBtn').addEventListener('click', applyPosition);
function applyPosition() {
  const postId = document.getElementById('qid').textContent;
  const token = localStorage.getItem("token");  

  if (postId === "") {
    return;

  } else {        
  fetch(`/api/jobApply/${postId}`, {
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

      setTimeout(function () {
                          window.location.href = '/';
                      }, 5000); 
      }
  })
  .catch((error) => {
      console.error("Error:", error);
  });
}
}

function performSearch() {

  let keyword = document.getElementById('jobSearchInput').value;
  let postalCode = document.querySelector('input[name="zipcode"]').value;

  if (keyword === "" && postalCode === "") {
    return;

  } else { 
    // Proceed with the fetch request
    fetch(`/api/jobPost?keyword=${keyword}&postalCode=${postalCode}`, {
      method: "GET",
    })
    .then((response) => {
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
    })
    .then((data) => {
        // Handle the data received from the server
        console.log(data);

        // Assuming you have a container element with the ID "job_list"
        const jobListContainer = document.getElementById("job_list");

        jobListContainer.innerHTML = '';

        // Check if data is an array and not empty
        if (Array.isArray(data) && data.length > 0) {
            // Iterate over the array of job posts
            data.forEach((jobPost) => {
                // Create elements for each job post
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

                // Append the job post element to the main job list container
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
            jobListContainer.innerHTML = '<p>No job posts available.</p>';
        }
    })
    .catch((error) => {
        console.error("Error fetching job posts:", error.message);
    });
  }
}


// Call the loadingJob function to initiate the process when the page loads
document.addEventListener('DOMContentLoaded', function () {
  loadingJob();
});

const searchButton = document.getElementById('searchBtn'); 
searchButton.addEventListener('click', function () {
  performSearch();
});

$("#twzipcode").twzipcode();


