import { sendWhenReady } from "../utils/utils.js";

const get_tournament_info = {
    "event": "tournament",
    "data": {
        "action": "tournament_info"
    }
}
sendWhenReady(tournamentSocket, JSON.stringify(get_tournament_info));

