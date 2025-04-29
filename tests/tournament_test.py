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
        print(f"Error executing command: {e}")
        print(f"Error output: {e.stderr}")
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
        print(f"Failed to create account for {username}")
        return None

    print(f"Account created with email: {email}")
    return client_uuid


def on_message(ws, message, client_id):
    # Parse the message
    try:
        msg_data = json.loads(message)
        event = msg_data.get('event')
        action = msg_data.get('data', {}).get('action')
        content = msg_data.get('data', {}).get('content', {})

        # print(f"Client {client_id} received: {event} - {action}")

        # Handle TOURNAMENT events
        if event == 'TOURNAMENT':
            if action == 'TOURNAMENT_CREATED':
                global tournament_code
                tournament_code = content.get('code')
                print(f"Tournament created with code: {tournament_code}\n")
            elif action == 'TOURNAMENT_JOIN':
                print(f"Client {client_id} successfully joined the tournament\n")
            elif action == 'TOURNAMENT_PLAYER_JOIN':
                player_id = content.get('id')
                print(f"Player joined tournament: {player_id}\n")
            elif action == 'TOURNAMENT_LEFT':
                print(f"Client {client_id} successfully left the tournament\n")
            elif action == 'TOURNAMENT_WAITTING_PLAYERS':
                print(f"Tournament is waiting for players\n")
            elif action == 'TOURNAMENT_PLAYERS_READY':
                print(f"All players are ready, tournament can start\n")
            elif action == 'TOURNAMENT_GAME_READY':
                print('Tournament is ready to start your game!\n')

        # Handle GAME events
        elif event == 'GAME':
            if action == 'JOIN_GAME':
                print(f"Client {client_id} successfully joined the game\n")
            elif action == 'LEFT_GAME':
                print(f"Client {client_id} successfully left the game\n")
            elif action == 'STARTING':
                print(f"Game is about to start\n")
            elif action == 'STARTED':
                print(f"Game has started\n")
            elif action == 'GAME_ENDING':
                print(f"Game has ended\n")

        # Handle UPDATE events
        elif event == 'UPDATE':
            if action == 'PLAYER_INFOS':
                print(f"Received player information update\n")
            elif action == 'BALL_UPDATE':
                print(f"Received ball position update\n")
            elif action == 'PADDLE_LEFT_UPDATE':
                print(f"Received left paddle update\n")
            elif action == 'PADDLE_RIGHT_UPDATE':
                print(f"Received right paddle update\n")
            elif action == 'SCORE_LEFT_UPDATE':
                score = content.get('score', 0)
                print(f"Left player score updated: {score}\n")
            elif action == 'SCORE_RIGHT_UPDATE':
                score = content.get('score', 0)
                print(f"Right player score updated: {score}\n")

        # Handle CHAT events
        elif event == 'CHAT':
            if action == 'ROOM_CREATED':
                print(f"Chat room created successfully\n")
            elif action == 'MESSAGE_RECEIVED':
                sender = content.get('sender', 'Unknown')
                message_text = content.get('message', '')
                print(f"New message from {sender}: {message_text}\n")
            elif action == 'HISTORY_RECEIVED':
                print(f"Received chat history\n")
            elif action == 'ALL_ROOM_RECEIVED':
                print(f"Received list of all chat rooms\n")

        # Handle NOTIFICATION events
        elif event == 'NOTIFICATION':
            if action == 'ACK_SEND_FRIEND_REQUEST':
                print(f"Friend request sent successfully\n")
            elif action == 'ACK_ACCEPT_FRIEND_REQUEST':
                print(f"Friend request accepted\n")
            elif action == 'ACK_ACCEPT_FRIEND_REQUEST_HOST':
                print(f"Your friend request was accepted\n")
            elif action == 'ACK_REFUSE_FRIEND_REQUEST':
                print(f"Friend request refused\n")
            elif action == 'ACK_DELETE_FRIEND':
                print(f"Friend deleted successfully\n")
            elif action == 'ACK_DELETE_FRIEND_HOST':
                print(f"You were removed from someone's friend list\n")
            elif action == 'NOTIF_TEST':
                print(f"Received test notification\n")

        # Handle ERROR events
        elif event == 'ERROR':
            error_msg = content
            print(f"Error received: {error_msg}\n")
            stop_event.set()  # Signal to stop all threads

        # Handle unknown events
        else:
            print(f"Received unknown event: {event} with action: {action}")
            print(f"Full message: {msg_data}")

    except json.JSONDecodeError:
        print(f"Invalid JSON received: {message}")


def on_error(ws, error, client_id):
    """Handle WebSocket errors"""
    print(f"Client {client_id} error: {error}")
    # Remove client from connections if it's there but errored
    if client_id in client_connections and client_connections[client_id] == ws:
        print(f"Removing client {client_id} from connections due to error")
        del client_connections[client_id]


def on_close(ws, close_status_code, close_msg, client_id):
    """Handle WebSocket connection close"""
    print(f"Client {client_id} connection closed: {close_status_code} - {close_msg}")
    # Remove client from connections if it's there but closed
    if client_id in client_connections and client_connections[client_id] == ws:
        print(f"Removing client {client_id} from connections due to closure")
        del client_connections[client_id]


def on_open(ws, client_id, is_host=False):
    """Handle WebSocket connection open"""
    client_connections[client_id] = ws
    print(f"Client {client_id} connected successfully\n")

    # If this is the host client, create a tournament
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
                "max_players": num_clients,
                "public": True,
                "bots": True,
                "points_to_win": 11,
                "timer": 120
            }
        }
    }

    print(f"Creating tournament with {num_clients} players...")
    ws.send(json.dumps(tournament_msg))


def join_tournament(client_id, code):
    """Send a message to join a tournament"""
    if client_id not in client_connections:
        print(f"Client {client_id} not connected")
        return

    ws = client_connections[client_id]

    # Join tournament message
    join_msg = {
        "event": "tournament",
        "data": {
            "action": "join_tournament",
            "args": {
                "code": code
            }
        }
    }

    print(f"Client {client_id} joining tournament {code}...")
    ws.send(json.dumps(join_msg))


def cleanup():
    """Clean up resources before exiting"""
    print("Cleaning up...")

    # Close all WebSocket connections
    for client_id, ws in client_connections.items():
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
