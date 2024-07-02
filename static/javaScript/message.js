function checkToken (){
    const checkToken = localStorage.getItem("token");
    if (!checkToken) {
        window.location.href = '/'; }
    }
    
window.addEventListener('load', checkToken);

const socket = io({ autoConnect: false });

let username;
let roomId;

function messageMemberId() {
    const token = localStorage.getItem("token");

    fetch("/api/loadingMemberId", {
        headers: {
            "Authorization": `Bearer ${token}`,
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.ok && data.data) {
            username = data.data[0];

            // Connect to Socket.IO server
            socket.connect();

            socket.on("connect", function() {
            socket.emit("user_join", username);
            });
        } else {
            console.error("Invalid data format or missing member ID");
        }
    })
    .catch((error) => {
        console.error("Error:", error);
    });
}

messageMemberId();


function loadingMessageBox() {
    const token = localStorage.getItem("token");
    const messageListContainer = document.getElementById("messageList");

    fetch("/api/loadingMessageBox", {
        method: "GET",
        headers: {
            "Content-Type": "application/json",
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
        console.log(data)
        if (Array.isArray(data.data) && data.data.length > 0) {
            data.data.forEach((myMessageBox) => {
                const myMessageBoxElement = document.createElement("div");
                myMessageBoxElement.classList.add("card");

                myMessageBoxElement.innerHTML = `
                    <div class="card-left blue-bg">
                        <img src="${myMessageBox.memberIcon}">
                    </div>
                    <div class="card-center">
                        <h3>${myMessageBox.memberId}</h3>
                    </div>
                `;

                messageListContainer.appendChild(myMessageBoxElement);

                myMessageBoxElement.addEventListener("click", async function (event) {
                    event.preventDefault();
                    const messageRoomId = myMessageBox.roomId;


                    socket.emit('leave_room', { roomId: roomId, username: username });

                    try {
                        const response = await fetch(`/api/loadingMessageRoomId/${messageRoomId}`, {
                            method: "GET",
                            headers: {
                                "Content-Type": "application/json",
                                "Authorization": `Bearer ${token}`,
                            },
                        });

                        if (!response.ok) {
                            throw new Error(`HTTP error! Status: ${response.status}`);
                        }
                        const data = await response.json();
                        roomId = data.data.messageRoomId;
                        userEmail = data.data.userEmail;
                        const userId = data.data.memberId;
                        socket.emit('join_room', { roomId, userId });

                        document.getElementById("message").addEventListener("keyup", async function (event) {
                            if (event.key === "Enter") {
                                let message = document.getElementById("message").value;
                                socket.emit("new_message", message, roomId, userId, userEmail);
                                document.getElementById("message").value = "";
    }
                        });

                        const contentResponse = await fetch(`/api/loadingMessageContent/${messageRoomId}`, {
                            method: "GET",
                        });

                        if (!contentResponse.ok) {
                            throw new Error(`HTTP error! Status: ${contentResponse.status}`);
                        }

                        const contentData = await contentResponse.json();

                        let messageContent = document.getElementById("messageContent");
                        messageContent.innerHTML = "";

                        contentData.data.forEach(item => {
                            const messageElement = document.createElement("p");
                            messageElement.textContent = `${item.username}: ${item.message}`;
                            messageContent.appendChild(messageElement);
                        });

                                            } catch (error) {
                        console.error("Error:", error.message);
                    }
                });
            });
        } else {
            messageListContainer.innerHTML = '<p style="text-align: center;">No messages avaliable yet.</p>';
        }
    })
    .catch((error) => {
        console.error("Error fetching messages:", error.message);
    });
}

socket.on('new_message', function(data) {

        const messageContent = document.getElementById("messageContent");
        const messageElement = document.createElement("p");
        messageElement.textContent = `${data.username}: ${data.message}`;
        messageContent.appendChild(messageElement);
    
});




loadingMessageBox();


