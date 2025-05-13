import { WebSocketManager } from "../websockets/websockets.js"
import { navigateTo } from "../spa/spa.js"
import { sendWhenReady } from "../utils/utils.js";

const tournamentSocket = WebSocketManager.tournamentSocket;


tournamentSocket.onmessage = ((msg)=>{
    console.log(msg);
    const message = JSON.parse(msg.data);
    
    if (message.event == "TOURNAMENT" && message.data.action == "TOURNAMENT_LIST") {
        console.log("Infos of list of tournaments", message.data);
        //Update the front to show a button of stuff here.
    }
})

const get_tournaments_info = {
    "event": "tournament",
    "data": {
        "action": "list_tournament"
    }    
}

function populateJoinTournament(max_clients){
    let clientsDiv = []
    
    for (let i = 0 ; i < max_clients ; i++){
        clientsDiv.push(`
            <div class="col room d-flex justify-content-center align-items-center">
                <div class="cardContainer">
                    <h4>{{ room.name }}</h4>


                    <div class="d-flex flex-row align-items-center justify-content-between">
                        <div class="btn joinBtn">join</div>
                        <div class="avatarsContainer mt-2">

                            <div class="imgContainer">
                                <img src="/static/img/img.png" alt="">
                            </div>
                            <div class="imgContainer">
                                <img src="/static/img/img.png" alt="">
                            </div>
                            <div class="imgContainer">
                                <img src="/static/img/img.png" alt="">
                                <div class="more">+6</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div> 
            `)
        }
}

//Otherwise if we refresh on the page we try to send a message before its open.
sendWhenReady(tournamentSocket, JSON.stringify(get_tournaments_info));



