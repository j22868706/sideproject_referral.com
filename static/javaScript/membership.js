document.getElementById('updatePwd').addEventListener('click', function(event) {
    event.preventDefault();  // Prevent the default form submission behavior

    const token = localStorage.getItem("token");
    const previousPwd = document.getElementById('previousPwd').value;
    const newPwd = document.getElementById('newPwd').value;
    const resultMessageBox = document.querySelector(".messageBox");

    if (newPwd === "" || previousPwd === "") {
        resultMessageBox.style.display = "block";
        resultMessageBox.style.color = "red";
        resultMessageBox.textContent = "Failed to update passwords, some fields are still empty！";
    } else if(newPwd.length < 6 || newPwd.length > 12) {
        // Check if the password length is valid
        resultMessageBox.style.display = "block";
        resultMessageBox.style.color = "red";
        resultMessageBox.textContent = "Passwords must be 6 - 12 characters！";
    } else if(newPwd === previousPwd) {
        // Check if the password length is valid
        resultMessageBox.style.display = "block";
        resultMessageBox.style.color = "red";
        resultMessageBox.textContent = "New passwords connot be the same as your old password！";
    } else {
        fetch("/api/updatePwd", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`,
            },
            body: JSON.stringify({ previousPwd, newPwd }),
        })
        .then(response => {
            return response.json();
        })
        .then(data => {
            const resultMessageBox = document.querySelector(".messageBox");
            resultMessageBox.textContent = data.message;

            if (data.error) {
                resultMessageBox.style.color = "red";
                resultMessageBox.style.display = "block";
            } else {
                resultMessageBox.style.color = "green";
                resultMessageBox.style.display = "block";

                setTimeout(() => {
                    location.reload();
                }, 3000);
            }
        })
        .catch((error) => {
            console.error("Error:", error);
        });
      }
});


function loadingMemberId(){
    const token = localStorage.getItem("token");

    fetch("/api/loadingMemberId", {
        headers: {
            "Authorization": `Bearer ${token}`,
        },
    })
    .then(response => {
        return response.json();
    })
    .then(data => {
        console.log(data)
        const userId = document.getElementById("userId");
    
        // Check if data is an array and has elements
        if (Array.isArray(data.data) && data.data.length > 0) {
            userId.textContent = data.data[0]; // Assuming you want the first element
        } else {
            console.error("Data format is not as expected");
        }
    })
    .catch((error) => {
        console.error("Error:", error);
    });
}

document.getElementById('updateMemberId').addEventListener('click', function(event) {
    event.preventDefault();
    const token = localStorage.getItem("token");
    const newId = document.getElementById('newId').value;
    const resultMessageBox = document.querySelector(".messageBox");

    if (newId === "") {
        resultMessageBox.style.display = "block";
        resultMessageBox.style.color = "red";
        resultMessageBox.textContent = "Failed to update your username, some fields are still empty！";
    } else {
        fetch("/api/updateMemberId", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`,
            },
            body: JSON.stringify({ newId }),
        })
        .then(response => {
            return response.json();
        })
        .then(data => {
            const resultMessageBox = document.querySelector(".messageBox");
            resultMessageBox.textContent = data.message;

            if (data.error) {
                resultMessageBox.style.color = "red";
                resultMessageBox.style.display = "block";
            } else {
                resultMessageBox.style.color = "green";
                resultMessageBox.style.display = "block";

                setTimeout(() => {
                    location.reload();
                }, 3000);
            }
        })
        .catch((error) => {
            console.error("Error:", error);
        });
    }
});


document.getElementById('updateMemberPhoto').addEventListener('click', function(event) {
    event.preventDefault();  // Prevent the default form submission behavior

    const token = localStorage.getItem("token");
    const fileInput = document.getElementById('memberPhotoFile');
    const allowedExtensions = ['png', 'jpg', 'jpeg', 'gif'];
    const resultMessageBox = document.querySelector(".messageBox");

    // Check if a file is selected
    if (!fileInput.files[0]) {
        resultMessageBox.textContent = "You haven't selected a new profile icon！";
        resultMessageBox.style.color = "red";
        resultMessageBox.style.display = "block";
        return;
    }

    // Get the file extension
    const fileExtension = fileInput.files[0].name.split('.').pop().toLowerCase();

    // Check if the file extension is allowed
    if (!allowedExtensions.includes(fileExtension)) {
        resultMessageBox.textContent = "Profile picture does not meet file requirements!";
        resultMessageBox.style.color = "red";
        resultMessageBox.style.display = "block";
        return;
    }

    // Create a FormData object and append the file to it
    const formData = new FormData();
    formData.append('memberPhotoFile', fileInput.files[0]);

    // Make the fetch request
    fetch("/api/updatememberIdPhoto", {
        method: "POST",
        headers: {
            "Authorization": `Bearer ${token}`,
        },
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
        resultMessageBox.textContent = data.message;

        if (data.error) {
            resultMessageBox.style.color = "red";
            resultMessageBox.style.display = "block";
        } else {
            resultMessageBox.style.color = "green";
            resultMessageBox.style.display = "block";

            setTimeout(() => {
                location.reload();
            }, 3000);
        }
    })
    .catch((error) => {
        console.error("Error:", error);
    });
});


function loadingMemberIcon(){
    const token = localStorage.getItem("token");

    fetch("/api/loadingMemberIcon", {
        headers: {
            "Authorization": `Bearer ${token}`,
        },
    })
    .then(response => {
        return response.json();
    })
    .then(data => {
        const memberIcon = document.getElementById("memberIcon");
    
        // Check if data is an array and has elements
        if (Array.isArray(data.data) && data.data.length > 0) {
            memberIcon.src = data.data[0]; // Assuming you want the first element
        } else {
            console.error("Data format is not as expected");
        }
    })
    .catch((error) => {
        console.error("Error:", error);
    });
}

loadingMemberId();
loadingMemberIcon();



