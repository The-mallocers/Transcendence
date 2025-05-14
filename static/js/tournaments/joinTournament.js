import { WebSocketManager } from "../websockets/websockets.js"
import { navigateTo } from "../spa/spa.js"
import { sendWhenReady } from "../utils/utils.js";

const tournamentSocket = WebSocketManager.tournamentSocket;

const tournaments = document.querySelector("#tournaments");
/*{
    "event": "TOURNAMENT",
    "data": {
        "action": "TOURNAMENT_JOIN",
        "content": "You have successfully joined the tournament"
    }
}*/
tournamentSocket.onmessage = ((msg)=>{
    console.log("zebiiii" + msg);
    const message = JSON.parse(msg.data);   
    
    if (message.event == "TOURNAMENT" && message.data.action == "TOURNAMENT_JOIN") {
        console.log("data of tournament join", message.data);
        navigateTo(`/pong/tournament/?code=${message.data.content}`);
    }
    // else if (message.event == "TOURNAMENT" && message.data.action == "TOURNAMENT_CREATED"){
    //     console.log("tungtungtung sahur")
    //     tournamentSocket.send(JSON.stringify(get_tournaments_info));
    // }
    else if (message.event == "TOURNAMENT" && message.data.action == "TOURNAMENT_LIST") {
        console.log("Infos of list of tournaments", message.data);
        populateJoinTournament(message.data.content);
        //Update the front to show a button of stuff here.
    }

})


// [
//             {
//                 max_clients : 8,
//                 code : "blabla",
//                 name: "meowmeow",
//                 players_infos: [
//                     {
//                         avatar: "/static/img/img.png"
//                     },            
//                     {
//                         avatar: "/static/img/img.png"
//                     },                   
//                     {
//                         avatar: "/static/img/img.png"
//                     }
//                 ]
//             },
//             {
//                 max_clients : 16,
//                 code : "bloblo",

//                 name : "tralalerotralala",
//                 players_infos: [
//                     {
//                         avatar: "/static/img/img.png"
//                     },            
//                     {
//                         avatar: "/static/img/img.png"
//                     },                   
//                     {
//                         avatar: "/static/img/img.png"
//                     }
//                 ]
//             },
//             {
//                 max_clients : 32,
//                 code : "blublu",

//                 name : "brrbrr patapim",
//                 players_infos: [
//                     {
//                         avatar: "/static/img/img.png"
//                     },            
//                     {
//                         avatar: "/static/img/img.png"
//                     },                   
//                     {
//                         avatar: "/static/img/img.png"
//                     }
//                 ]
//             }
//   ]
const get_tournaments_info = {
    "event": "tournament",
    "data": {
        "action": "list_tournament"
    }    
}


// {'title': 'awdawd', 'max_clients': 8, 
//     'players_infos': [
//         {'id': '4c357984-3b63-4adb-9c53-4476a6b59ea8', 
//         'nickname': 'miaou', 
//         'avatar': '/media/profile/default.png', 
//         'trophee': '/media/rank_icon/bronze.png', 
//         'mmr': 50}
//     ]
//     , 'code': 'EMS3J'}
function populateJoinTournament(tournamentList){
    let clientsDiv = []
    tournaments.innerHTML = ``
    
    tournamentList.forEach((room)=>{
        clientsDiv.push(`
        <div class="col room d-flex justify-content-center align-items-center" data-code="${room.code}" >
            <div class="cardContainer">
                <h4>${room.title}</h4>


                <div class="d-flex flex-row align-items-center justify-content-between">
                    <div class="btn joinTournamentBtn">join</div>
                    <div class="avatarsContainer mt-2">
                        ${room.players_infos.map((player, i)=>
                            `
                            <div class="imgContainer">
                                <img src="${player.avatar}" alt="">
                                ${(i == 2) ? `<div class="more">+${room.max_clients - (i + 1)}</div>`: ''}
                            </div>
                            `

                        ).join('')}


                    </div>
                </div>
            </div>
        </div> 
        `)
    })

                            // <div class="imgContainer">
                        //     <img src="/static/img/img.png" alt="">
                        // </div>
                        // <div class="imgContainer">
                        //     <img src="/static/img/img.png" alt="">
                        //     <div class="more">+6</div>
                        // </div>
       
    clientsDiv.forEach(htmlString => {
        const temp = document.createElement("div");
        temp.innerHTML = htmlString; 

        while (temp.firstChild) {
            console.log(temp.firstChild)
            tournaments.appendChild(temp.firstChild);
        }
    });
}

//Otherwise if we refresh on the page we try to send a message before its open.

function joinTournament(code) {
    const message = {
        "event": "tournament",
        "data": {
            "action": "join_tournament",
            "args": {
                "code": code
            }
        }
    }
    tournamentSocket.send(JSON.stringify(message));
}

//Need to do this so that the event listerner also listens to the dynamic html
document.addEventListener('click', async (e) => {
    const joinBtn = e.target.closest('.joinTournamentBtn');
    if (joinBtn) {
        const parentRoom = joinBtn.closest('.room');
        const code = parentRoom.dataset.code ;
        console.log(code)
        joinTournament(code);
    }
});


sendWhenReady(tournamentSocket, JSON.stringify(get_tournaments_info));


let meowInterval = setInterval(() => {
    console.log("meowwowow")
    sendWhenReady(tournamentSocket, JSON.stringify(get_tournaments_info));

    // tournamentSocket.send(JSON.stringify(get_tournament_info));
    
}, 3000);


