import pytest
import requests
from src import config

BASE_URL = config.url

@pytest.fixture(autouse=True)
def clear():

    '''
    A fixture to clear the state for each test
    '''

    response = requests.delete(f"{BASE_URL}clear/v1")
    assert response.status_code == 200
    assert response.json() == {}

def register_user(email, password, name_first, name_last):

    '''
    Registers a new user with given parameters and returns the users token
    '''

    response = requests.post(f"{BASE_URL}auth/register/v2",json={
        'email' : email,
        'password' : password,
        'name_first' : name_first,
        'name_last' : name_last
    })

    assert response.status_code == 200
    response_data = response.json()
    assert isinstance(response_data['token'],str)
    assert isinstance(response_data['auth_user_id'],int)
    return response_data

def channels_create(token, name, is_public):

    '''
    Creates a channel for user with given token and returns the channel ID
    '''

    response = requests.post(f"{BASE_URL}channels/create/v2", json={
        'token' : token,
        'name' : name,
        'is_public' : is_public
    })

    assert response.status_code == 200
    response_data = response.json()
    return response_data

def dm_create(token, u_ids):

    '''
    Creates a dm for user with given token and other's u_ids returns the dm ID
    '''

    response = requests.post(f"{BASE_URL}dm/create/v1", json={
        'token' : token,
        'u_ids' : u_ids,
    })

    assert response.status_code == 200
    response_data = response.json()
    return response_data

def invite(token, channel_id, u_id):
    response = requests.post(f"{BASE_URL}channel/invite/v2", json={
        'token' : token,
        'channel_id' : channel_id,
        'u_id' : u_id
    })

    assert response.status_code == 200
    response_data = response.json()
    return response_data

def get_notifications(token):
    response = requests.get(f"{BASE_URL}notifications/get/v1?token={token}")
    assert response.status_code == 200
    response_data = response.json()
    return response_data

def test_invite_notification():
    owner = register_user('a@email.com', 'Pass123456!', 'Jade', 'Painter')
    user = register_user('b@email.com', 'Pass123456!', 'Kayla', 'Monk')
    channel = channels_create(owner['token'], 'My Channel', True)
    _ = invite(owner['token'], channel['channel_id'], user['auth_user_id'])
    # List of dictionaries
    notifications = get_notifications(user['token'])['notifications']
    assert {
        'channel_id' : channel['channel_id'],
        'dm_id' : -1,
        'notification_message' : "jadepainter added you to My Channel"
        } in notifications

def test_dm_creation_notification():
    owner = register_user('a@email.com', 'Pass123456!', 'Jade', 'Painter')
    user = register_user('b@email.com', 'Pass123456!', 'Kayla', 'Monk')
    dm = dm_create(owner['token'], [user['auth_user_id']])
    # List of dictionaries
    notifications = get_notifications(user['token'])['notifications']
    assert {
        'channel_id' : -1,
        'dm_id' : dm['dm_id'],
        'notification_message' : "jadepainter added you to jadepainter, kaylamonk"
        } in notifications