console.log("coucou je suis matchmaking")

//Fetch pour dire au serveur qu'on veut join la queue
const element  = document.querySelector("#clientID");
const clientId = element.dataset.clientId
// Get individual data attributes
// const username = element.dataset.username;
console.log(element.dataset.clientId)

let connectToMMPool = async (client_id)=>{

    let socket =  new WebSocket('ws://' + window.location.host + '/ws/game/?id=' + client_id);


    console.log(socket)
}


connectToMMPool(clientId);