# channel_join_v1_test.py
# pytest file to test the implementation of channel_join_v2
import pytest
import requests
import json
from src import config

@pytest.fixture
def setup():
    '''
    Clears the server data and creates some users and channels.
    '''
    user = []
    channels = []
    requests.delete(config.url + 'clear/v1')
    resp = requests.post(config.url + f"auth/register/v2", json={
        'email' : 'validemail@gmail.com',
        'password' : '123abc!@#',
        'name_first' : 'Hayden',
        'name_last' : 'Everest'
    })
    user.append(json.loads(resp.text))
    resp = requests.post(config.url + f"auth/register/v2", json={
        'email' : 'validemail1@gmail.com',
        'password' : '123abc!@#',
        'name_first' : 'John',
        'name_last' : 'Smith'
    })
    user.append(json.loads(resp.text))
    resp = requests.post(config.url + f"auth/register/v2", json={
        'email' : 'validemail2@gmail.com',
        'password' : '123abc!@#',
        'name_first' : 'Jade',
        'name_last' : 'Painter'
    })
    user.append(json.loads(resp.text))
    channels.append(requests.post(config.url + 'channels/create/v2', json={'token': user[0]['token'], 'name': 'My channel', 'is_public': 'True'}))
    channels.append(requests.post(config.url + 'channels/create/v2', json={'token': user[1]['token'], 'name': 'My private channel', 'is_public': 'False'}))
    return (user, channels)

def test_invalid_channel_id(setup):
    users, _ = setup
    resp = requests.post(config.url + 'channel/join/v2', json={'token': users[0]['token'], 'channel_id': 1234})
    assert resp.status_code == 400
        
def test_invalid_token(setup):
    _, channels = setup
    resp = requests.post(config.url + 'channel/join/v2', json={'token': "", 'channel_id': channels[0]["channel_id"]})
    assert resp.status_code == 403
        
def test_already_joined(setup):
    users, channels = setup
    resp = requests.post(config.url + 'channel/join/v2', json={'token': users[1]['token'], 'channel_id': channels[0]["channel_id"]})
    assert resp.status_code == 403

def test_join_private_channel(setup):
    users, channels = setup
    resp = requests.post(config.url + 'channel/join/v2', json={'token': users[2]['token'], 'channel_id': channels[1]["channel_id"]})
    assert resp.status_code == 400

def test_join_public_channel(setup):
    users, channels = setup
    _ = requests.post(config.url + 'channel/join/v2', json={'token': users[1]['token'], 'channel_id': channels[0]["channel_id"]})
    channel_details = requests.get(config.url + 'channel/details/v2', params={'token': users[1]['token'], 'channel_id': channels[0]["channel_id"]})
    assert channel_details.status_code == 200

def test_global_owner_join_private_channel(setup):
    users, channels = setup
    _ = requests.post(config.url + 'channel/join/v2', json={'token': users[0]['token'], 'channel_id': channels[1]["channel_id"]})
    channel_details = requests.get(config.url + 'channel/details/v2', params={'token': users[0]['token'], 'channel_id': channels[1]["channel_id"]})
    assert channel_details.status_code == 200