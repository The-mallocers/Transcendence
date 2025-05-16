import { sendWhenReady } from "../utils/utils.js";
import { WebSocketManager } from "../websockets/websockets.js";

const get_tournament_info = {
    "event": "tournament",
    "data": {
        "action": "tournament_info"
    }
}

sendWhenReady(WebSocketManager.tournamentSocket, JSON.stringify(get_tournament_info));