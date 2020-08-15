import pytest

from wonder_stats import consumers


@pytest.mark.parametrize('message_type, body', [
    ('test', {'k1': 'v1', 'k2': 'v2'}, )
])
def test_websocket_message_initialization(message_type, body):
    message = consumers.WebSocketMessage(message_type, **body)

    for body_key, body_value in body.items():
        assert getattr(message, body_key) == body_value
