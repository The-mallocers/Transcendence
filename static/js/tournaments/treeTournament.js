import { WebSocketManager } from "../websockets/websockets.js";
import { navigateTo } from "../spa/spa.js";
import { sendWhenReady } from "../utils/utils.js";

//In veut faire une requete a la websocket de l'etat actuel du tournoi.
//L'etat idealement, nous rend toute les infos qu'on va render sur la page.
//Comme ca, si jamais une update, on pourra juste tout reload la nouvelle tournament comme on le fait dans le lobby.

const tournamentSocket = WebSocketManager.tournamentSocket;


const tournamentInfos =  {
        "roomInfos": {
            "title":"aaaaa",
            "max_clients": 4,
            "players_infos":[
                {
                    "id":"8d32bb8e-0c88-4e5f-956c-59fdd8a28edf",
                    "nickname":"miaou",
                    "avatar":"/media/profile/default.png",
                    "trophee":"/media/rank_icon/bronze.png",
                    "mmr":75
                }
            ],
            "code":"CJVLK",
            "scoreboard":{
                "num_rounds":2,
                "current_round":1,
                "rounds":{
                    "round_1":{
                        "matches_total":2,
                        "matches_completed":0,
                        "games":{
                        "r1m1":{
                            "game_code":"VY8K8",
                            "status":"creating",
                            "winner_username":"None",
                            "loser_username":"None",
                            "loser_score":0,
                            "winner_score":0
                        },
                        "r1m2":{
                            "game_code":"9GFAQ",
                            "status":"creating",
                            "winner_username":"None",
                            "loser_username":"None",
                            "loser_score":0,
                            "winner_score":0
                        }
                        }
                    },
                    "round_2":{
                        "matches_total":1,
                        "matches_completed":0,
                        "games":{
                        "r2m1":{
                            "game_code":"4HJQE",
                            "status":"creating",
                            "winner_username":"None",
                            "loser_username":"None",
                            "loser_score":0,
                            "winner_score":0
                        }
                        }
                    }
                }
            }
        }
    }

    // scoreboard.rounds

// let tournamentInfosJson = JSON.parse(tournamentInfos)

console.log(tournamentInfos.roomInfos)

tournamentSocket.onmessage = ((msg)=>{
    console.log("TOURNAMENT ROOM RECEIVES THIS MESSAGE");
    console.log(msg);
    const message = JSON.parse(msg.data);
    
    // if (message.event == "ERROR"){
    //     console.log("Error message: ", message.data.error)
    //     navigateTo("/pong/gamemodes/");
    //     // errDiv.innerHTML = message.data.error
    //     return
    // }
    // console.log("BONJOUR:", message.data);
    if (message.event == "TOURNAMENT" && message.data.action == "TOURNAMENT_INFO") {
        console.log("tournament info is :", message.data.action);
        tournament_data = message.data.content;
        populateTree(tournament_data.max_clients);
    }
})

const get_tournament_info = {
    "event": "tournament",
    "data": {
        "action": "tournament_info"
    }
}





// <h1>{{ tournamentInfos. }}</h1>
//     <div class="round mt-5">
//         <h2>Round 1</h2>
//         <table class="table mt-2">
//             <thead>
//             <tr>
//                 <th scope="col">Players</th>
//                 <th scope="col">Status</th>
//                 <th scope="col">Scores</th>
//             </tr>
//             </thead>
//             <tbody>
//             <tr>
//                 <td class="players">
//                     <div class="left">
//                         <img src="/static/img/img.png" alt="">
//                         <div>meow</div>
//                     </div>
//                     <div class="vs">VS</div>
//                     <div class="right">
//                         <img src="/static/img/img.png" alt="">
//                         <div>meow</div>
//                     </div>
//                 </td>
//                 <td><span class="badge bg-success">Played</span></td>
//                 <td><span class="left-score winner">5</span> - <span class="right-score loser">0</span></td>
//             </tr>
//             <tr>
//                 <td class="players">
//                     <div class="left">
//                         <img src="/static/img/img.png" alt="">
//                         <div>meow</div>
//                     </div>
//                     <div class="vs">VS</div>
//                     <div class="right">
//                         <img src="/static/img/img.png" alt="">
//                         <div>meow</div>
//                     </div>
//                 </td>
//                 <td><span class="badge bg-success">Played</span></td>
//                 <td><span class="left-score winner">5</span> - <span class="right-score loser">0</span></td>
//             </tr>
//             <tr>
//                 <td class="players">
//                     <div class="left">
//                         <img src="/static/img/img.png" alt="">
//                         <div>brrbrrpatapim</div>
//                     </div>
//                     <div class="vs">VS</div>
//                     <div class="right">
//                         <img src="/static/img/img.png" alt="">
//                         <div>trallalerotralala</div>
//                     </div>
//                 </td>
//                 <td><span class="badge bg-success">Played</span></td>
//                 <td><span class="left-score winner">5</span> - <span class="right-score loser">0</span></td>
//             </tr>
//             <tr>
//                 <td class="players">
//                     <div class="left">
//                         <img src="/static/img/img.png" alt="">
//                         <div>brrbrrpatapim</div>
//                     </div>
//                     <div class="vs">VS</div>
//                     <div class="right">
//                         <img src="/static/img/img.png" alt="">
//                         <div>trallalerotralala</div>
//                     </div>
//                 </td>
//                 <td><span class="badge bg-success">Played</span></td>
//                 <td><span class="left-score winner">5</span> - <span class="right-score loser">0</span></td>
//             </tr>
//             <tr>
//                 <td class="players">
//                     <div class="left">
//                         <img src="/static/img/img.png" alt="">
//                         <div>brrbrrpatapim</div>
//                     </div>
//                     <div class="vs">VS</div>
//                     <div class="right">
//                         <img src="/static/img/img.png" alt="">
//                         <div>trallalerotralala</div>
//                     </div>
//                 </td>
//                 <td><span class="badge bg-success">Played</span></td>
//                 <td><span class="left-score winner">5</span> - <span class="right-score loser">0</span></td>
//             </tr>
//             <!-- we can add a tr for every competitor of the tournament for each round  -->
//             <!-- should dynamicaly do so when socket updates with atresall -->
//             </tbody>
//         </table>
//     </div>


const buildTr = (matchInfos)=>{

    return `<tr>
                <td class="players">
                    <div class="left">
                        <img src="/static/img/img.png" alt="">
                        <div>${matchInfos.winner_username}</div>
                    </div>
                    <div class="vs">VS</div>
                    <div class="right">
                        <img src="/static/img/img.png" alt="">
                        <div>${matchInfos.loser_username}</div>
                    </div>
                </td>
                <td><span class="badge bg-success">${matchInfos.status}</span></td>
                <td><span class="left-score winner">${matchInfos.winner_score}</span> - <span class="right-score loser">${matchInfos.loser_score}</span></td>
            </tr>`
}

const buildRound = (roundInfos, name)=>{

    console.log(roundInfos)
    return `
    <div class="round mt-5">
        <h2>${name}</h2>
        <table class="table mt-2">
            <thead>
            <tr>
                <th scope="col">Players</th>
                <th scope="col">Status</th>
                <th scope="col">Scores</th>
            </tr>
            </thead>
            <tbody>

    ${Object.entries(roundInfos.games)
        .map(([key, round]) => buildTr(round, key))
        .join("")}
            </tbody>
        </table>
    </div>
    `
}



let meow = document.querySelector("#tree")
function populateTree() {

        meow.innerHTML = ''



    

        for (const key in tournamentInfos?.roomInfos.scoreboard.rounds) {
            meow.innerHTML += buildRound(tournamentInfos?.roomInfos.scoreboard.rounds[key], key)
        }
        
    
    //matboyer a l'aide
}


populateTree()
sendWhenReady(tournamentSocket, JSON.stringify(get_tournament_info));
