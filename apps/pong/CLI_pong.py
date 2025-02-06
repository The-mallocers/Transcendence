import asyncio
import websockets
import json
import curses
import sys
from asyncio import Queue

class PongCLI:
    def __init__(self, websocket_url):
        self.websocket_url = websocket_url
        self.game_state = None
        self.message_queue = Queue()
        
    async def connect(self):
        try:
            self.websocket = await websockets.connect(self.websocket_url)
            print("Connected to Pong server!")
            return True
        except Exception as e:
            print(f"Failed to connect: {e}")
            return False

    def draw_game(self, stdscr):
        if not self.game_state:
            return

        try:
            # Clear screen
            stdscr.clear()
            
            height, width = stdscr.getmaxyx()
            
            # Draw top and bottom borders (avoiding bottom-right corner)
            stdscr.addstr(0, 0, '+' + '-' * (width-3) + '+')
            if height > 1:
                stdscr.addstr(height-2, 0, '+' + '-' * (width-3) + '+')
            
            # Draw scores
            if height > 3:
                stdscr.addstr(1, min(width//4, width-3), f"Player 1: {self.game_state['left_score']}")
                stdscr.addstr(1, min(3*width//4, width-3), f"Player 2: {self.game_state['right_score']}")
            
            # Draw paddles (scaled to terminal size)
            left_y = int(self.game_state['left_paddle_y'] * (height-6) / 600) + 2
            right_y = int(self.game_state['right_paddle_y'] * (height-6) / 600) + 2
            
            for i in range(5):  # Paddle height
                if 2 <= left_y + i < height-2:
                    stdscr.addstr(left_y + i, 2, '█')
                if 2 <= right_y + i < height-2:
                    stdscr.addstr(right_y + i, min(width-3, width-1), '█')
            
            # Draw ball (scaled to terminal size)
            ball_x = int(self.game_state['ball_x'] * (width-6) / 800) + 2
            ball_y = int(self.game_state['ball_y'] * (height-6) / 600) + 2
            
            if 1 < ball_x < width-2 and 1 < ball_y < height-2:
                stdscr.addstr(ball_y, ball_x, '●')
            
            # Draw controls info
            if height > 4:
                controls = "Controls: A/D - Left Paddle, J/L - Right Paddle, Q - Quit"
                if len(controls) < width-4:
                    stdscr.addstr(height-3, 2, controls)
            
            stdscr.refresh()
        except curses.error:
            # Ignore curses errors related to terminal size
            pass

    async def handle_input(self, stdscr):
        while True:
            try:
                key = stdscr.getch()
                if key == ord('q'):
                    return False
                
                # Handle paddle movements
                if key == ord('a'):
                    await self.message_queue.put({
                        'type': 'paddle_move',
                        'paddle': 'left',
                        'direction': 'up'
                    })
                elif key == ord('d'):
                    await self.message_queue.put({
                        'type': 'paddle_move',
                        'paddle': 'left',
                        'direction': 'down'
                    })
                elif key == ord('j'):
                    await self.message_queue.put({
                        'type': 'paddle_move',
                        'paddle': 'right',
                        'direction': 'down'
                    })
                elif key == ord('l'):
                    await self.message_queue.put({
                        'type': 'paddle_move',
                        'paddle': 'right',
                        'direction': 'up'
                    })
                
                await asyncio.sleep(0.01)
            except Exception as e:
                print(f"Input error: {e}")
                return False
        
    async def handle_websocket(self):
        try:
            while True:
                # Send any queued messages
                while not self.message_queue.empty():
                    message = await self.message_queue.get()
                    await self.websocket.send(json.dumps(message))
                
                # Receive game state
                message = await self.websocket.recv()
                data = json.loads(message)
                
                if data['type'] == 'game_state_update':
                    self.game_state = data['state']
                
                await asyncio.sleep(0.01)
        except Exception as e:
            print(f"WebSocket error: {e}")
            return False

    async def run(self, stdscr):
        # Check terminal size
        height, width = stdscr.getmaxyx()
        if height < 10 or width < 40:
            stdscr.addstr(0, 0, "Terminal window too small. Please resize to at least 40x10 characters.")
            stdscr.refresh()
            stdscr.getch()
            return

        # Set up curses
        curses.curs_set(0)  # Hide cursor
        stdscr.nodelay(1)   # Non-blocking input
        
        if not await self.connect():
            return
        
        # Create tasks for input handling and websocket communication
        input_task = asyncio.create_task(self.handle_input(stdscr))
        websocket_task = asyncio.create_task(self.handle_websocket())
        
        # Main game loop
        try:
            while True:
                if input_task.done() or websocket_task.done():
                    break
                    
                self.draw_game(stdscr)
                await asyncio.sleep(1/30)  # 30 FPS
        finally:
            # Clean up
            if not input_task.done():
                input_task.cancel()
            if not websocket_task.done():
                websocket_task.cancel()
            
            await self.websocket.close()

def main():
    # Default to localhost if no argument provided
    url = sys.argv[1] if len(sys.argv) > 1 else 'ws://localhost:8000/ws/somepath/'
    
    client = PongCLI(url)
    curses.wrapper(lambda stdscr: asyncio.run(client.run(stdscr)))

if __name__ == "__main__":
    main()