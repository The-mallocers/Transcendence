from channels.layers import get_channel_layer

from utils.pong.enums import ResponseError, EventType, ResponseAction


async def send_player_error(player_id, error_type: ResponseError):
    channel_layer = get_channel_layer()
    await channel_layer.group_send(
        f'player_{player_id}',
        {
            'type': 'player_send',
            'message': {
                'event': EventType.ERROR,
                'data': {
                    'action': error_type.name,
                    'content': error_type.value,
                 }
            }
        }
    )

async def send_player(player_id, event_type: EventType, msg_type: ResponseAction):
    channel_layer = get_channel_layer()
    await channel_layer.group_send(
        f'player_{player_id}',
        {
            'type': 'player_send',
            'message': {
                'event': event_type,
                'data': {
                    'action': msg_type.name,
                    'content': msg_type.value,
                 }
            }
        }
    )

async def send_game(game_id, event_type: EventType, msg_type: ResponseAction):
    channel_layer = get_channel_layer()
    await channel_layer.group_send(
        f'game_{game_id}',
        {
            'type': 'game_send',
            'message': {
                'event': event_type,
                'data': {
                    'action': msg_type.name,
                    'content': msg_type.value,
                 }
            }
        }
    )

async def send_game_error(game_id, error_type: ResponseError):
    channel_layer = get_channel_layer()
    await channel_layer.group_send(
        f'game_{game_id}',
        {
            'type': 'game_send',
            'message': {
                'event': EventType.ERROR,
                'data': {
                    'action': error_type.name,
                    'content': error_type.value,
                }
            }
        }
    )