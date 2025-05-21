import { tournamentData } from "../apps/game/VarGame.js"
import { navigateTo } from "../spa/spa.js"  
import { addReadyButton } from "./tournamentsSocketHandlers.js"
// import { leaveTournament } from "./tournamentRoom.js"

import { WebSocketManager } from "../websockets/websockets.js"
// import { WebSocketManager } from ""

//Build TREE
const buildTr = (matchInfos) => {
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
            ${`<img src="${matchInfos.playerR_picture}" alt="">`}
            <div>${matchInfos.playerR_username}</div>
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

const buildRound = (roundInfos, name)=> {

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

const leave_tournament = {
    "event": "tournament",
    "data": {
        "action": "leave_tournament"
    }
}

function leaveTournament() {
    WebSocketManager.tournamentSocket.send(JSON.stringify(leave_tournament))
    // WebSocketManager.closeTournamentSocket();
    navigateTo("/pong/gamemodes/");
}



export function populateTree(tournamentInfos) {
        let meow = null
        // const btnsRoom = document.querySelector("#btnsRoom")

        // if (btnsRoom) {
        //     btnsRoom.innerHTML = `
        //                 <div id="leave-btn" class="btn btn-intra-outlined">Leave</div>
        //     `
        // }
        meow = document.querySelector("#tree")
        if (meow == null) return ;
        meow.innerHTML = '';
        for (const key in tournamentInfos?.scoreboard.rounds) {
            meow.innerHTML += buildRound(tournamentInfos?.scoreboard.rounds[key], key)
        }
        
        meow.innerHTML += `<div class="btns d-flex flex-row justify-content-between gap-3 align-items-center mt-3"></div>`


        let leaveBtn = document.createElement("div")
        leaveBtn.innerText = "leave"
        leaveBtn.classList.add('btn','btn-intra-outlined')
        leaveBtn.onclick = function() {
            leaveTournament();
        }

        let btns = document.querySelector(".btns")
        btns.appendChild(leaveBtn)
        console.log(leaveBtn, meow)
        if (tournamentData.gameIsReady) {
            // const parrent = document.querySelector('#tree')
            // console.log("data of tournament join", parrent);
            // if (parrent){
                let btn = document.createElement('div')
                btn.classList.add('btn', 'intra-btn');
                btn.innerText = 'Ready';
                btn.addEventListener('click', ()=>{navigateTo(`/pong/matchmaking/`);})
                btns.appendChild(btn)
            // }
        }
}


//TOURNAMENT ROOM
export function populateTournament(tournament_data){
    const max_clients = tournament_data.max_clients
    const btnsRoom = document.querySelector("#btnsRoom")
    const h1 = document.querySelector("h1")

    h1.innerText = tournament_data.title
    
    if (btnsRoom) {
        btnsRoom.innerHTML = `
                    <div class="btn btn-intra">Invite</div>
                    <div id="leave-btn" class="btn btn-intra-outlined">Leave</div>
        `
    }
    console.log("jhdcv§zfXVZÈVÈD§FVTÈZFVIÈZTDFVÈFVÈFVTÈFV",tournament_data)
    const clientsInTournament = document.querySelector("#clientsInTournament");
    let clientsDiv = []
    if (clientsInTournament == null) return ;
    clientsInTournament.innerHTML = ``
    for (let i = 0 ; i < max_clients ; i++){
        clientsDiv.push(`
            <div class="col p-2">
            <div class="content border p-3 d-flex justify-content-between align-items-center">
            <div class="d-flex align-items-center justify-content-center gap-3">
            <div class="nickname ml-3"> waiting</div>
            <div>(add bpoyer's animation with the li dots)</div>
            </div>
            </div>
            </div>
            </div>
            `)
        }
        
        
        tournament_data?.players_infos?.forEach((player , i)=> {
            console.log(tournament_data.host , player ,player.id, )
            clientsDiv[i] = `
            <div class="position-relative col p-2">
            <div class="content border p-3 d-flex justify-content-between align-items-center">
                            <div class="d-flex align-items-center justify-content-center gap-3">
                            <div class="avatarContainer">
                                    <img class="avata" src="${player.avatar}" alt="">
                            </div>
                                <div class="position-relative nickname ml-3">
                                    ${tournament_data.host == player.id ? (`<img class="star" src="/static/img/star.png" alt="">`):''}
                                    ${ player.nickname }
                                </div>
                            </div>

                            <div class="d-flex justify-content-center align-items-center gap-1 flex-column">
                            <img class="tropheeImg" src="${player.trophee}" alt="">
                            <div>mmr: ${ player.mmr }</div>
                            </div>

                        </div>
                        </div>
                        `
            });
    clientsDiv.forEach(htmlString => {
        const temp = document.createElement("div");
        temp.innerHTML = htmlString; 

        while (temp.firstChild) {
            console.log(temp.firstChild)
            clientsInTournament.appendChild(temp.firstChild);
        }
    });
    addReadyButton(tournamentData.gameIsReady);
}

///JOIN TOURNAMENT
export function populateJoinTournament(tournamentList){
    const tournaments = document.querySelector("#tournaments");
    let clientsDiv = []
    if (tournaments == null) return ;
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
    clientsDiv.forEach(htmlString => {
        const temp = document.createElement("div");
        temp.innerHTML = htmlString; 

        while (temp.firstChild) {
            console.log(temp.firstChild)
            tournaments.appendChild(temp.firstChild);
        }
    });
}