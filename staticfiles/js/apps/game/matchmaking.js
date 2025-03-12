console.log("coucou je suis matchmaking")

//Fetch pour dire au serveur qu'on veut join la queue
const id = document.querySelector("[client-id]")
console.log(id)

let connectToMMPool = async (client_id)=>{

    let response =  new WebSocket('ws://' + window.location.host + '/ws/game/matchmaking/?id=' + client_id)


    console.log(response)
}
