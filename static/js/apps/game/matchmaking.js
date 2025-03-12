console.log("coucou je suis matchmaking")

//Fetch pour dire au serveur qu'on veut join la queue
const element  = document.querySelector("#clientID");
const clientId = element.dataset.clientId

const gameStatusDiv = document.querySelector("#gameStatus")
// Get individual data attributes
// const username = element.dataset.username;
console.log(element.dataset.clientId)

let connectToMMPool = (client_id) =>{

    let socket = new WebSocket('ws://' + window.location.host + '/ws/game/?id=' + client_id);
    
    const message = {
        "event": "matchmaking",
        "data": {
            "action": "join_queue"
        }
    }
    socket.onopen = () => {
        socket.send(JSON.stringify(message));
    }
    socket.onclose = () => {
        console.log("You disconnected your matchmaking socket");
    }
    
    socket.onmessage =  (e)=> {
        const jsonData =  JSON.parse(e.data)

        if (jsonData.data.action)
            gameStatusDiv.innerHTML = jsonData.data.content
        console.log(jsonData, gameStatusDiv)
        console.log(jsonData.data.action)
        //We should only get the response that a match was found
    }
    console.log(socket)
}

connectToMMPool(clientId);