function submitPostJob(event) {
    event.preventDefault();  // Prevent the default form submission

    const token = localStorage.getItem("token");
    const jobTitle = document.getElementById("jobTitle");
    const jobDetail = document.getElementById("jobDetail");
    const numberOfJobPositions = document.getElementById("numberOfJobPositions");
    const jobDate = document.getElementById("jobDate");
    const jobStartTime = document.getElementById("jobStartTime");
    const jobEndTime = document.getElementById("jobEndTime");
    const jobLocation = document.getElementById("jobLocation");
    const jobSalary = document.getElementById("jobSalary");
    const paymentMethod = document.getElementById("paymentMethod");
    const payDate = document.getElementById("payDate");
    const jobOthers = document.getElementById("jobOthers");
    const twzipcode = document.querySelector('input[name="zipcode"]');
    const resultMessageBox = document.querySelector(".message_box");

    const today = new Date().toISOString().split('T')[0];

    const jobDateValue = new Date(jobDate.value);
    const payDateValue = new Date(payDate.value);



  
    // Check if date values are valid
    if (isNaN(jobDateValue) && isNaN(payDateValue)) {
        resultMessageBox.style.display = "block";
        resultMessageBox.style.color = "red";
        resultMessageBox.textContent = "Job Date or pay date not filled！";
        return;
    } 
    const selectedDate = jobDateValue.toISOString().split('T')[0];
    const selectedPayDate = payDateValue.toISOString().split('T')[0];

    if (
        jobTitle.value === "" ||
        jobDetail.value === "" ||
        numberOfJobPositions.value === "" ||
        jobDate.value === "" ||
        jobStartTime.value === "" ||
        jobEndTime.value === "" ||
        jobLocation.value === "" ||
        paymentMethod.value === "" ||
        jobSalary.value === "" ||
        payDate.value === "" ||
        jobOthers.value === "" ||
        twzipcode.value === ""
    ) {
        resultMessageBox.style.display = "block";
        resultMessageBox.style.color = "red";
        resultMessageBox.textContent = "Some fields are still empty！";
        return;

    } else if (selectedDate < today) {
        console.log(selectedDate)
        console.log(today)
        resultMessageBox.style.display = "block";
        resultMessageBox.style.color = "red";
        resultMessageBox.textContent = "Job date cannot in the past！";
        return;

    } else if (isNaN(jobSalary.value) || parseFloat(jobSalary.value) <= 0) {
        resultMessageBox.style.display = "block";
        resultMessageBox.style.color = "red";
        resultMessageBox.textContent = "Salary amount must ba a number greater than zero！";
        return;

    } else if (isNaN(numberOfJobPositions.value) || parseFloat(numberOfJobPositions.value) <= 0) {
        resultMessageBox.style.display = "block";
        resultMessageBox.style.color = "red";
        resultMessageBox.textContent = "Number of job positions must ba a number greater than zero！";
        return;

    } else if (selectedPayDate < today) {

        resultMessageBox.style.display = "block";
        resultMessageBox.style.color = "red";
        resultMessageBox.textContent = "Pay date connot be in the past！";
        return;

    } else {
        // Proceed with the fetch request
        fetch("/api/jobPost", {
            method: "POST",
            body: new FormData(document.getElementById("postJob")),
            headers: {
                "Authorization": `Bearer ${token}`,
            },
        })
        .then((response) => response.json())
        .then((data) => {
            console.log(data);
            resultMessageBox.textContent = data.message;

            if (data.error) {
                resultMessageBox.style.color = "red";
                resultMessageBox.style.display = "block";
            } else {
                console.log(data.message)
                resultMessageBox.style.color = "green";
                resultMessageBox.style.display = "block";
                setTimeout(function () {
                    window.location.href = "/application";
                }, 3000); // 3000 milliseconds = 3 seconds
            }
        })
        .catch((error) => {
            console.error("Error:", error);
        });
    }
}

      

function checkToken (){
    const checkToken = localStorage.getItem("token");
    if (!checkToken) {
        window.location.href = '/'; }
    }
    
    window.addEventListener('load', checkToken);


$("#twzipcode").twzipcode();

