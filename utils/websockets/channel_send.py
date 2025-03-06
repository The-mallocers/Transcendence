from channels.layers import get_channel_layer
from django.conf import settings
from redis.asyncio import Redis
from redis.commands.json.path import Path

from utils.pong.enums import ResponseError, EventType, ResponseAction

async def send_group(channel_name, event_type: EventType, msg_type: ResponseAction, content=None, close=False):
    """
    Send formated message to channel group when with specifique channel_name
    Args:
        channel_name: Name of channel who want to send
        event_type:
        msg_type:
        content: When content is None, the content send is msg_type value
        close:
    """
    channel_layer = get_channel_layer()
    await channel_layer.group_send(
        str(channel_name),
        {
            'type': 'send_channel',
            'close': close,
            'message': {
                'event': event_type.name,
                'data': {
                    'action': msg_type.name,
                    'content': content if content is not None else msg_type.value,
                }
            }
        }
    )

async def send_group_error(channel_name, error_type: ResponseError, content=None, close=False):
    channel_layer = get_channel_layer()
    await channel_layer.group_send(
        str(channel_name),
        {
            'type': 'send_channel',
            'close': close,
            'message': {
                'event': EventType.ERROR.name,
                'data': {
                    'action': error_type.name,
                    'content': content if content is not None else error_type.value,
                }
            }
        }
    )

# async def send_player(player_id, event_type: EventType, msg_type: ResponseAction, content=None, close=False):
#     if close:
#         redis = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)
#         await redis.hdel('player_chan', str(player_id))
#     channel_layer = get_channel_layer()
#     await channel_layer.group_send(
#         f'player_{player_id}',
#         {
#             'type': 'player_send',
#             'close': close,
#             'message': {
#                 'event': event_type.name,
#                 'data': {
#                     'action': msg_type.name,
#                     'content': content if content is not None else msg_type.value,
#                 }
#             }
#         }
#     )
#
# async def send_player_error(player_id, error_type: ResponseError, content=None, close=False):
#     if close:
#         redis = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)
#         await redis.hdel('player_chan', str(player_id))
#     channel_layer = get_channel_layer()
#     await channel_layer.group_send(
#         f'player_{player_id}',
#         {
#             'type': 'player_send',
#             'close': close,
#             'message': {
#                 'event': EventType.ERROR.name,
#                 'data': {
#                     'action': error_type.name,
#                     'content': content if content is not None else error_type.value,
#                 }
#             }
#         }
#     )
#
#
# async def send_game(game_id, event_type: EventType, msg_type: ResponseAction, content=None, close=False):
#     if close:
#         redis = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)
#         players = await redis.json().get(f'game:{game_id}', Path("players"))
#         player_ids = [player["id"] for player in players]
#         for p in player_ids:
#             await redis.hdel('player_chan', str(p))
#     channel_layer = get_channel_layer()
#     await channel_layer.group_send(
#         f'game_{game_id}',
#         {
#             'type': 'game_send',
#             'close': close,
#             'message': {
#                 'event': event_type.name,
#                 'data': {
#                     'action': msg_type.name,
#                     'content': content if content is not None else msg_type.value,
#                 }
#             }
#         }
#     )
#
#
# async def send_game_error(game_id, error_type: ResponseError, content=None, close=False):
#     if close:
#         redis = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)
#         players = await redis.json().get(f'game:{game_id}', Path("players"))
#         player_ids = [player["id"] for player in players]
#         for p in player_ids:
#             await redis.hdel('player_chan', str(p))
#             await redis.hdel('player_game', str(p))
#     channel_layer = get_channel_layer()
#     await channel_layer.group_send(
#         f'game_{game_id}',
#         {
#             'type': 'game_send',
#             'close': close,
#             'message': {
#                 'event': EventType.ERROR.name,
#                 'data': {
#                     'action': error_type.name,
#                     'content': content if content is not None else error_type.value,
#                 }
#             }
#         }
#     )
