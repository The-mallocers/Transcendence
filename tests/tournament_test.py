#!/usr/bin/env python3
"""
Tournament WebSocket Test Script

This script tests the WebSocket tournament functionality by:
1. Creating the specified number of test accounts (if they don't exist)
2. Connecting each account to the tournament WebSocket
3. Creating a tournament with the first client
4. Having all other clients join the tournament

Requirements:
- Python 3.6+
- websocket-client package (pip install websocket-client)
- Docker (to run Django management commands)

Usage:
    python tournament_test.py <number_of_clients>

Example:
    python tournament_test.py 4
"""

import argparse
import json
import signal
import ssl
import subprocess
import sys
import threading
import time

import websocket

# Global variables
client_connections = {}
tournament_code = None
ws_threads = []
stop_event = threading.Event()
num_clients = None  # Will store the number of clients from command-line argument


def run_docker_command(command):
    """Run a command in the Django Docker container"""
    full_command = f"docker exec -i django {command}"
    try:
        result = subprocess.run(
            full_command,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return None


def create_test_account(index):
    """Create a test account using Django management command"""
    username = f"test_user_{index}"
    email = f"test{index}@example.com"
    password = "Test@123"

    # Use Django management command to create account
    client_uuid = run_docker_command(
        f"python manage.py create_test_account '{username}' '{email}' '{password}'"
    )

    if not client_uuid:
        return None
    return client_uuid


def join_game(client_id, is_tournament=False):
    """Send a message to join a game"""
    if client_id not in client_connections:
        return

    ws = client_connections[client_id]
    join_msg = {
        "event": "game",
        "data": {
            "action": "join_game",
            "args": {
                "is_tournament": is_tournament
            }
        }
    }
    try:
        ws.send(json.dumps(join_msg))
    except RuntimeError:
    # La socket est fermée
        pass



def create_game_connection(client_id):
    """Create a separate game WebSocket connection"""
    url = f"wss://localhost:8000/ws/game/?id={client_id}"

    # Create WebSocket connection with SSL verification disabled
    ws = websocket.WebSocketApp(
        url,
        on_open=lambda ws: on_open(ws, f"{client_id}_game"),
        on_message=lambda ws, msg: on_message(ws, msg, f"{client_id}_game"),
        on_error=lambda ws, err: on_error(ws, err, f"{client_id}_game"),
        on_close=lambda ws, code, msg: on_close(ws, code, msg, f"{client_id}_game")
    )

    # Run the WebSocket connection with SSL context
    ws_thread = threading.Thread(
        target=ws.run_forever,
        kwargs={"sslopt": {"cert_reqs": ssl.CERT_NONE}}
    )
    ws_thread.daemon = True
    ws_thread.start()
    ws_threads.append(ws_thread)

    return ws


def on_message(ws, message, client_id):
    try:
        msg_data = json.loads(message)
        event = msg_data.get('event')
        action = msg_data.get('data', {}).get('action')
        content = msg_data.get('data', {}).get('content', {})

        # Handle TOURNAMENT events
        if event == 'TOURNAMENT':
            if action == 'TOURNAMENT_CREATED':
                global tournament_code
                tournament_code = content.get('code')
                print(f"[{client_id}] Tournament created with code: {tournament_code}\n")
            elif action == 'TOURNAMENT_JOIN':
                print(f"[{client_id}] Successfully joined the tournament\n")
            elif action == 'TOURNAMENT_PLAYER_JOIN':
                player_id = content.get('id')
                print(f"[{client_id}] Player joined tournament: {player_id}\n")
            elif action == 'TOURNAMENT_LEFT':
                print(f"[{client_id}] Successfully left the tournament\n")
            elif action == 'TOURNAMENT_WAITTING_PLAYERS':
                print(f"[{client_id}] Tournament is waiting for players\n")
            elif action == 'TOURNAMENT_PLAYERS_READY':
                print(f"[{client_id}] All players are ready, tournament can start\n")
            elif action == 'TOURNAMENT_LOSE_GAME':
                print(f"[{client_id}] Lost the tournament game - closing this tournament connection\n")
                ws.close() #TODO une fois une game perdu, si tu te deco de /tournament/ws tu peut pas te reco et tu ne peut plus voir la suite du tournois
                del client_connections[client_id]
                # Don't return here, allow the function to continue processing
            elif action == 'TOURNAMENT_GAME_FINISH':
                print(f"[{client_id}] Tournament game finished\n")
                # If this is a game websocket, close it
                if client_id.endswith('_game'):
                    print(f"[{client_id}] Closing game websocket connection\n")
                    ws.close(status=1000, reason="TOURNAMENT_GAME_FINISH") #TODO une fois qu'une game est fini, il faut retourner sur la page tournois
                    del client_connections[client_id]
                # Don't return here, allow the function to continue processing
            elif action == 'TOURNAMENT_GAME_READY': #TODO Redirige vers la page matchmaking et normalement tous ce fait tout seul
                print('Tournament is ready to start your game!')
                if not client_id.endswith('_game'):  # Prevent recursive game connections
                    base_client_id = client_id.split('_')[0]  # Get original client ID
                    game_ws = create_game_connection(base_client_id)
                    client_connections[f"{base_client_id}_game"] = game_ws


        # Handle GAME events
        elif event == 'GAME':
            if action == 'JOIN_GAME':
                print(f"[{client_id}] Successfully joined the game\n")
            elif action == 'LEFT_GAME':
                print(f"[{client_id}] Successfully left the game\n")
            elif action == 'STARTING':
                print(f"[{client_id}] Game is about to start\n")
            elif action == 'STARTED':
                print(f"[{client_id}] Game has started\n")
            elif action == 'GAME_ENDING':
                print(f"[{client_id}] Game has ended\n")

        # Handle UPDATE events
        elif event == 'UPDATE':
            if action == 'PLAYER_INFOS':
                print(f"[{client_id}] Received player information update\n")

        # Handle NOTIFICATION events
        elif event == 'NOTIFICATION':
            if action == 'ACK_SEND_FRIEND_REQUEST':
                print(f"[{client_id}] Friend request sent successfully\n")
            elif action == 'ACK_ACCEPT_FRIEND_REQUEST':
                print(f"[{client_id}] Friend request accepted\n")
            elif action == 'ACK_ACCEPT_FRIEND_REQUEST_HOST':
                print(f"[{client_id}] Your friend request was accepted\n")
            elif action == 'ACK_REFUSE_FRIEND_REQUEST':
                print(f"[{client_id}] Friend request refused\n")
            elif action == 'ACK_DELETE_FRIEND':
                print(f"[{client_id}] Friend deleted successfully\n")
            elif action == 'ACK_DELETE_FRIEND_HOST':
                print(f"[{client_id}] You were removed from someone's friend list\n")
            elif action == 'NOTIF_TEST':
                print(f"[{client_id}] Received test notification\n")

        # Handle ERROR events
        elif event == 'ERROR':
            error_msg = msg_data.get('data', {}).get('error', {})
            print(f"[{client_id}] Error received: {action}\n")
            print(f'[{client_id}] Error message: {error_msg}\n')
            stop_event.set()

        else:
            print(f"[{client_id}] Received unknown event: {event} with action: {action}")
            print(f"[{client_id}] Full message: {msg_data}")

    except json.JSONDecodeError:
        print(f"[{client_id}] Invalid JSON received: {message}")


def on_error(ws, error, client_id):
    print(f"[{client_id}] Error: {error}")
    if client_id in client_connections and client_connections[client_id] == ws:
        print(f"[{client_id}] Removing client from connections due to error")
        del client_connections[client_id]


def on_close(ws, close_status_code, close_msg, client_id):
    print(f"[{client_id}] Connection closed: {close_status_code} - {close_msg}")

    # Remove the connection from our tracking dictionary
    if client_id in client_connections and client_connections[client_id] == ws:
        print(f"[{client_id}] Removing client from connections due to closure")
        del client_connections[client_id]

        # Only set stop_event if this wasn't from a game connection or tournament loss
        # if not (client_id.endswith('_game') or (close_msg and 'TOURNAMENT_LOSE_GAME' in str(close_msg))):
        #     stop_event.set()


def on_open(ws, client_id, is_host=False):
    client_connections[client_id] = ws
    print(f"[{client_id}] Connected successfully\n")
    
    ping_msg = {
        "event": "matchmaking",
            "data": {
                "action": "ping"
            }
    }

    try:
        ws.send(json.dumps(ping_msg))
    except RuntimeError:
        # 
        print("esquiveeee")
        pass


    if is_host and not stop_event.is_set():
        global num_clients
        create_tournament(client_id, num_clients)


def websocket_client(client_id, is_host=False):
    """Start a WebSocket client for the given client ID"""
    url = f"wss://localhost:8000/ws/tournament/?id={client_id}"

    # Create WebSocket connection with SSL verification disabled
    ws = websocket.WebSocketApp(
        url,
        on_open=lambda ws: on_open(ws, client_id, is_host),
        on_message=lambda ws, msg: on_message(ws, msg, client_id),
        on_error=lambda ws, err: on_error(ws, err, client_id),
        on_close=lambda ws, code, msg: on_close(ws, code, msg, client_id)
    )

    # Run the WebSocket connection with SSL context
    ws_thread = threading.Thread(
        target=ws.run_forever,
        kwargs={"sslopt": {"cert_reqs": ssl.CERT_NONE}}
    )
    ws_thread.daemon = True
    ws_thread.start()
    ws_threads.append(ws_thread)

    return ws


def create_tournament(client_id, num_clients):
    """Send a message to create a tournament"""
    if client_id not in client_connections:
        print(f"Client {client_id} not connected")
        return

    ws = client_connections[client_id]

    # Create tournament message
    tournament_msg = {
        "event": "tournament",
        "data": {
            "action": "create_tournament",
            "args": {
                "title": "Test Tournament",
                "max_clients": num_clients,
                "is_public": True,
                "has_bots": True,
                "points_to_win": 1,
                "timer": 120
            }
        }
    }

    print(f"Creating tournament with {num_clients} players...")

    try:
        ws.send(json.dumps(tournament_msg))
    except RuntimeError:
        # La socket est fermée
        print("esquiveeee")
        pass


def join_tournament(client_id, code):
    if client_id not in client_connections:
        print(f"[{client_id}] Not connected")
        return

    ws = client_connections[client_id]
    join_msg = {
        "event": "tournament",
        "data": {
            "action": "join_tournament",
            "args": {
                "code": code
            }
        }
    }

    print(f"[{client_id}] Joining tournament {code}...")

    try:
        ws.send(json.dumps(join_msg))
    except RuntimeError:
        # La socket est fermée
        print("esquiveeee")
        pass


def close_game_connection(client_id):
    """Helper function to close game connection"""
    game_client_id = f"{client_id}_game"
    if game_client_id in client_connections:
        try:
            game_ws = client_connections[game_client_id]
            game_ws.close()
        except:
            print(f"[{game_client_id}] Error while closing game connection\n")


def cleanup():
    """Clean up resources before exiting"""
    print("Cleaning up...")

    # Close all WebSocket connections
    # Create a copy of the dictionary items to avoid "dictionary changed size during iteration" error
    for client_id, ws in list(client_connections.items()):
        try:
            ws.close()
        except:
            pass

    # Wait for all threads to finish
    for thread in ws_threads:
        if thread.is_alive():
            thread.join(timeout=1)


def signal_handler(sig, frame):
    """Handle interrupt signals"""
    print("Interrupted, cleaning up...")
    stop_event.set()
    cleanup()
    sys.exit(0)


def main():
    """Main function"""
    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)

    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Test WebSocket tournament functionality')
    parser.add_argument('num_clients', type=int, help='Number of clients to connect')
    args = parser.parse_args()

    global num_clients
    num_clients = args.num_clients
    if num_clients < 2:
        print("Error: At least 2 clients are required")
        sys.exit(1)

    # Create test accounts and get client UUIDs
    client_uuids = []
    for i in range(num_clients):
        client_uuid = create_test_account(i + 1)
        if client_uuid:
            client_uuids.append(client_uuid)

    if len(client_uuids) < num_clients:
        print(f"Error: Could only create {len(client_uuids)} out of {num_clients} accounts")
        sys.exit(1)

    # Connect clients to WebSockets
    print("Connecting clients to WebSockets...\n")
    host_client_id = client_uuids[0]

    # Connect host client first
    websocket_client(host_client_id, is_host=True)

    # Wait for tournament to be created
    timeout = 15
    start_time = time.time()
    while tournament_code is None and time.time() - start_time < timeout and not stop_event.is_set():
        time.sleep(0.5)

    if tournament_code is None:
        print("Error: Failed to create tournament")
        cleanup()
        sys.exit(1)

    # Connect other clients and have them join the tournament
    # Process clients in smaller batches to avoid overwhelming the server
    batch_size = 5  # Connect 5 clients at a time

    for batch_start in range(1, len(client_uuids), batch_size):
        batch_end = min(batch_start + batch_size, len(client_uuids))
        print(f"\nConnecting batch of clients {batch_start} to {batch_end - 1}...")

        # Connect all clients in this batch
        for i in range(batch_start, batch_end):
            client_id = client_uuids[i]
            print(f"Initiating connection for client {i}: {client_id}")
            websocket_client(client_id)
            time.sleep(1)  # Small delay between connection attempts within a batch

        # Wait for all clients in this batch to connect
        for i in range(batch_start, batch_end):
            client_id = client_uuids[i]

            # Wait for client to connect with a longer timeout
            connection_timeout = 10
            connection_start_time = time.time()
            while client_id not in client_connections and time.time() - connection_start_time < connection_timeout and not stop_event.is_set():
                time.sleep(0.5)

            if client_id not in client_connections:
                print(f"Warning: Client {i}: {client_id} failed to connect within timeout")
                continue

            # Join tournament
            join_tournament(client_id, tournament_code)

        # Wait between batches to allow the server to process the connections
        print(f"Waiting for server to process batch...")
        time.sleep(5)

        if stop_event.is_set():
            break

    # Keep the script running until interrupted
    try:
        while not stop_event.is_set():
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        cleanup()


if __name__ == "__main__":
    main()
