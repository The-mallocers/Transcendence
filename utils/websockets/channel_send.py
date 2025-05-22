from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from utils.enums import ResponseError, EventType, ResponseAction


async def asend_group(channel_name, event_type: EventType, msg_type: ResponseAction, content=None, close=False):
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


def send_group(channel_name: object, event_type: EventType, msg_type: ResponseAction, content: object = None, close: object = False) -> None:
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
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


async def asend_group_error(channel_name, error_type: ResponseError, content=None, close=False):
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
                    'error': content if content is not None else error_type.value,
                }
            }
        }
    )


def send_group_error(channel_name, error_type: ResponseError, content=None, close=False):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
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
