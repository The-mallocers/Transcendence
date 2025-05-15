import { WebSocketManager } from "../websockets/websockets.js";
import { navigateTo } from "../spa/spa.js";
import { sendWhenReady } from "../utils/utils.js";

//In veut faire une requete a la websocket de l'etat actuel du tournoi.
//L'etat idealement, nous rend toute les infos qu'on va render sur la page.
//Comme ca, si jamais une update, on pourra juste tout reload la nouvelle tournament comme on le fait dans le lobby.

const tournamentSocket = WebSocketManager.tournamentSocket;

// const tournamentInfos =  {
//    "title":"aaaa",
//    "max_clients":4,
//    "players_infos":[
//       {
//          "id":"7db871a6-5a1a-4e0f-9ae7-a64a2def5539",
//          "nickname":"theo",
//          "avatar":"/media/profile/default.png",
//          "trophee":"/media/rank_icon/bronze.png",
//          "mmr":66
//       },
//       {
//          "id":"8d32bb8e-0c88-4e5f-956c-59fdd8a28edf",
//          "nickname":"miaou",
//          "avatar":"/media/profile/default.png",
//          "trophee":"/media/rank_icon/bronze.png",
//          "mmr":94
//       }
//    ],
//    "code":"KW91H",
//    "scoreboard":{
//       "num_rounds":2,
//       "current_round":2,
//       "rounds":{
//          "round_1":{
//             "matches_total":2,
//             "matches_completed":2,
//             "games":{
//                "r1m1":{
//                   "game_code":"Z8LGR",
//                   "status":"finished",
//                   "winner_username":"miaou",
//                   "loser_username":"test2",
//                   "loser_score":0,
//                   "winner_score":1,
//                   "playerL_username":"test2",
//                   "playerR_username":"miaou",
//                   "playerR_picture":"/media/profile/default.png",
//                   "playerL_picture":"/media/profile/default.png",
//                },
//                "r1m2":{
//                   "game_code":"QCA0A",
//                   "status":"finished",
//                   "winner_username":"theo",
//                   "loser_username":"test1",
//                   "loser_score":0,
//                   "winner_score":1,
//                   "playerL_username":"theo",
//                   "playerR_username":"test1",
//                   "playerR_picture":"/media/profile/default.png",
//                   "playerL_picture":"/media/profile/default.png"
//                }
//             }
//          },
//          "round_2":{
//             "matches_total":1,
//             "matches_completed":0,
//             "games":{
//                "r2m1":{
//                   "game_code":"HE4M1",
//                   "status":"creating",
//                   "winner_username":"None",
//                   "loser_username":"None",
//                   "loser_score":0,
//                   "winner_score":0,
//                   "playerL_username":"miaou",
//                   "playerR_username":"theo",
//                   "playerR_picture":"/media/profile/default.png",
//                   "playerL_picture":"/media/profile/default.png"
//                }
//             }
//          }
//       }
//    }
// }

    // scoreboard.rounds

// let tournamentInfosJson = JSON.parse(tournamentInfos)

// console.log(tournamentInfos.roomInfos)

tournamentSocket.onmessage = ((msg)=>{
    console.log("TOURNAMENT ROOM RECEIVES THIS MESSAGE");
    const message = JSON.parse(msg.data);
    console.log(message);
    
    // // if (message.event == "ERROR"){
    // //     console.log("Error message: ", message.data.error)
    // //     navigateTo("/pong/gamemodes/");
    // //     // errDiv.innerHTML = message.data.error
    // //     return
    // // }
    if (message.event == "TOURNAMENT" && message.data.action == "TOURNAMENT_INFO") {
        console.log("tournament info is :", message.data.content);
        const tournament_data = message.data.content;
        populateTree(tournament_data);
    }
    else if (message.event == "TOURNAMENT" && message.data.action == "TOURNAMENT_UPDATE") {
        console.log("Im told theres been an update, so now Im asking for it !");
        tournamentSocket.send(JSON.stringify(get_tournament_info));
    }
})

const get_tournament_info = {
    "event": "tournament",
    "data": {
        "action": "tournament_info"
    }
}


const buildTr = (matchInfos)=>{
    let left, right = ``

    if (matchInfos.status == "creating"){
        left = `
                <img src="/static/img/huh.webp" alt="">
                <div>-- tbd --</div>
        `
        right = `
                <img src="/static/img/huh.webp" alt="">
                <div>-- tbd --</div>
        `

    }else if (matchInfos.status == "finished"){

        left = `
                <img src="${matchInfos.winner_picture}" alt="">
                <div>${matchInfos.winner_username}</div>
        `

        right = `
                <img src="${matchInfos.loser_picture}" alt="">
                <div>${matchInfos.loser_username}</div>
        `
    }else {
        left = `
            ${`<img src="${matchInfos.playerL_picture}" alt="">`}
            <div>${matchInfos.playerL_username}</div>
        `

        right = `
            ${`<img src="${matchInfos.playerL_picture}" alt="">`}
            <div>${matchInfos.playerL_username}</div>
        `
    }
    return `<tr>
                <td class="players">
                    <div class="left">
                        ${left}
                    </div>
                    <div class="vs">VS</div>
                    <div class="right">
                        ${right}
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
function populateTree(tournamentInfos) {

        meow.innerHTML = '';
        for (const key in tournamentInfos?.scoreboard.rounds) {
            meow.innerHTML += buildRound(tournamentInfos?.scoreboard.rounds[key], key)
        }
}

sendWhenReady(tournamentSocket, JSON.stringify(get_tournament_info));


// populateTree(tournamentInfos);

