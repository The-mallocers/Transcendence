import { tournamentData } from "../apps/game/VarGame.js"
import { navigateTo } from "../spa/spa.js"  
import { WebSocketManager } from "../websockets/websockets.js"

// Text formatting functions
const formatRoundName = (roundName) => {
    // Convert "round_1" to "Round 1", "semi_final" to "Semi Final", etc.
    return roundName
        .replace(/_/g, ' ')
        .replace(/\b\w/g, l => l.toUpperCase());
}

const formatStatus = (status) => {
    // Convert "waiting_to_start" to "Waiting to Start", "creating" to "Creating", etc.
    const statusMap = {
        'creating': 'Creating',
        'waiting_to_start': 'Waiting to Start',
        'in_progress': 'In Progress',
        'finished': 'Finished',
        'ending': 'Ending'
    };

    return statusMap[status] || status.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

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

    }else if (matchInfos.status == "finished" || matchInfos.status == "ending"){

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
                <td><span class="badge bg-success">${formatStatus(matchInfos.status)}</span></td>
                <td><span class="left-score winner">${matchInfos.winner_score}</span> - <span class="right-score loser">${matchInfos.loser_score}</span></td>
            </tr>`
}

const buildRound = (roundInfos, name) => {
    return `
    <div class="round mt-3">
        <h2>${formatRoundName(name)}</h2>
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

const buildControlsCard = (tournamentInfos) => {
    return `
    <div id="controls-card-fixed" class="controls-card mt-3">
        <div class="card-header d-flex justify-content-between align-items-center">
            <h3 class="mb-0" id="tournament-history-title">Tournament Controls</h3>
        </div>
        <div class="card-body">
            <div class="btns d-flex flex-row justify-content-between gap-3 align-items-center">
                <div id="leave-btn-tree" class="btn type-intra-white">Leave Tournament</div>
                ${tournamentData.gameIsReady ? '<div id="ready-btn" class="btn type-intra-green">Ready</div>' : ''}
            </div>
        </div>
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
    navigateTo("/pong/gamemodes/");
}

export function populateTree(tournamentInfos) {
    const treeParent = document.querySelector("#tree")
    if (treeParent == null) return;

    treeParent.innerHTML = '';

    // Add controls card at the top
    treeParent.innerHTML += buildControlsCard(tournamentInfos);

    // Add rounds
    for (const key in tournamentInfos?.scoreboard.rounds) {
        treeParent.innerHTML += buildRound(tournamentInfos?.scoreboard.rounds[key], key)
    }

    // Attach event listeners
    const leaveBtn = document.querySelector("#leave-btn-tree");
    if (leaveBtn) {
        leaveBtn.onclick = function() {
            leaveTournament();
        }
    }

    const readyBtn = document.querySelector("#ready-btn");
    if (readyBtn) {
        readyBtn.addEventListener('click', () => {
            navigateTo(`/pong/matchmaking/`);
        });
    }
}

//TOURNAMENT ROOM
export function populateTournament(tournament_data){
    const max_clients = tournament_data.max_clients;
    const btnsRoom = document.querySelector("#btnsRoom");
    const h1 = document.querySelector("#tournament-room-title");
    if (h1) {
        const parser = new DOMParser();
        const html = parser.parseFromString(tournament_data.title, "text/html");
        // h1.innerText = tournament_data.title;
        h1.innerText = html.firstChild.innerText;
    }

    if (btnsRoom) {
        btnsRoom.innerHTML = `
                    <div class="btn btn-intra type-intra-green" onclick="invite_friends()">Invite</div>
                    <div id="leave-btn" class="btn type-intra-white">Leave</div>
        `
    }

    const leave_btn = document.querySelector("#leave-btn");
    if (leave_btn == null) return ;
    leave_btn.onclick = function() {
        leaveTournament();
    }
    const clientsInTournament = document.querySelector("#clientsInTournament");
    let clientsDiv = []
    if (clientsInTournament == null) return ;
    clientsInTournament.innerHTML = ``
    for (let i = 0 ; i < max_clients ; i++){
        clientsDiv.push(`
            <div class="col p-2">
                <div class="content border p-3 d-flex justify-content-between align-items-center">
                    <div class="d-flex align-items-center justify-content-center gap-3">
                        <div class="nickname ml-3"> waiting <span class="dot-animation"></span></div>

                        </div>
                    </div>
                </div>
            </div>
            `)
        }


        tournament_data?.players_infos?.forEach((player , i)=> {
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
            clientsInTournament.appendChild(temp.firstChild);
        }
    });
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
                        ${room.players_infos.map((player, i)=>{
                            return`
                            <div class="imgContainer">
                                <img src="${player.avatar}" alt="">
                            </div>
                            `
                        }
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
            tournaments.appendChild(temp.firstChild);
        }
    });
}