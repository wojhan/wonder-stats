from enum import Enum


class MessageType(Enum):
    GAME_INFO_REQUEST = 'game_info_request'
    GAME_INFO_RESPONSE = 'game_info_response'
    GAME_INFO = 'game_info'
    PLAYER_JOINED_REQUEST = 'player_joined_request'
    PLAYER_JOINED_RESPONSE = 'player_joined_response'
    PLAYER_LEFT_REQUEST = 'player_left_request'
    PLAYER_LEFT_RESPONSE = 'player_left_response'
    POINT_UPDATE_REQUEST = 'update_point_request'
    POINT_UPDATE_RESPONSE = 'update_point_response'
    GET_POINTS_REQUEST = 'get_points_request'
    GET_POINTS_RESPONSE = 'get_points_response'
    POINT_UPDATE = 'point_update'
    FINISH_GAME_REQUEST = 'finish_game_request'
    FINISH_GAME_RESPONSE = 'finish_game_response'
    FINISH_GAME = 'finish_game'
    CREATE_GAME_REQUEST = 'create_game_request'
    CREATE_GAME_RESPONSE = 'create_game_response'
