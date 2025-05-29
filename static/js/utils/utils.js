export async function getClientId() {
    try {
        const response = await fetch("/api/auth/getId/", {
            method: "GET",
            credentials: "include",
        });
        const data = await response.json();
        if (!response.ok) {
            return null;
        }
        if (data.client_id) {
            return data.client_id;
        } else {
            throw new Error(data.error);
        }
    } catch (error) {
        console.error("Erreur lors de la récupération de l'ID :", error);
        return null;
    }
}

export function sendWhenReady(socket, message) {
    if (socket.readyState === WebSocket.OPEN) {
        socket.send(message);
    } else {
        socket?.addEventListener('open', () => socket.send(message), { once: true });
    }
}

export function create_front_chat_room(room, username, usernameId, status, profilePicture = null){
    const newChat = document.querySelector('.chatRooms');
    if(newChat)
    {
        const imgSrc = profilePicture;

        const parser = new DOMParser();
        const htmlChat = 
        `<div class="roomroom container d-flex flex-wrap align-items-center justify-content-between">
            <div class="chat-${username} chat-button btn d-flex align-items-center gap-3">
                <img src="${imgSrc}" alt="${username}'s profile picture">
                <div>${username}</div>
            </div>
            
            <div class="dropdown">
                <button class="btn btn-secondary dropdown-toggle no-caret rounded-circle" type="button" id="dropdownMenu-${room}" data-bs-toggle="dropdown" aria-expanded="false">
                    ...
                </button>
                <ul class="dropdown-menu">
                    <li><button class="dropdown-item chat-profile" type="button">Profil</button></li>
                    <li><button class="dropdown-item chat-block" type="button">${status}</button></li>
                    <li><button class="dropdown-item chat-duel" type="button">Duel</button></li>
                </ul>
            </div>
        </div>`
        const doc = parser.parseFromString(htmlChat, "text/html");
        const chatElement = doc.body.firstChild;
        // const chatButton = chatElement.querySelector(`.chat-${username}`)
        // const roomroom = chatElement.querySelector(".roomroom")
        const chatProfile = chatElement.querySelector(`.chat-profile`);
        const chatBlock = chatElement.querySelector(`.chat-block`);
        const chatDuel = chatElement.querySelector(`.chat-duel`);
        // console.log(roomroom);
        console.log(chatElement)
        chatElement?.addEventListener('click', function() {
            // const roomroomDiv = this.closest('.roomroom');
            console.log("je clique");
            this.classList.add('active-room');
            
            document.querySelectorAll('.roomroom.active-room').forEach(div => {
                if (div !== this) {
                    div.classList.remove('active-room');
                }
            });
            clickRoom(room)
        })
        chatProfile?.addEventListener('click', function(event){
            event.stopPropagation();
            handleChatProfile(username);
        })
        chatBlock?.addEventListener('click', function(event){
            event.stopPropagation();
            if(this.innerHTML == "Block"){
                this.innerHTML = "Unblock"
                handleChatBlock(username);
            }
            else{
                this.innerHTML = "Block"
                handleChatUnblock(username);
            }
            
        })
        chatDuel?.addEventListener('click', function(event){
            event.stopPropagation();
            handleChatDuel(usernameId);
        })
        chatElement.querySelector('.dropdown').addEventListener('click', function(event) {
            event.stopPropagation();
        });
        newChat.appendChild(chatElement);
    }
}

const isDevelopment = window.print;

export const logger = {
    log: (...args) => isDevelopment && console.log(...args),
    warn: (...args) => isDevelopment && console.warn(...args),
    error: (...args) => console.error(...args),
    debug: (...args) => isDevelopment && console.debug(...args),
};

export const sanitizeHTML = function (str) {
	return str.replace(/[^\w. ]/gi, function (c) {
		return '&#' + c.charCodeAt(0) + ';';
	});
};