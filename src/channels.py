"""
channels.py

This module handles the creation and listing of channels for Streams.

Functions:
    channels_list_v1(auth_user_id) -> { channels }
    channels_listall_v1(auth_user_id) -> { channels }
    channels_create_v1(auth_user_id, name, is_public) -> { channel_id }
"""

from src.data_store import data_store
from src.error import InputError
from src.other import check_valid_token, update_user_stats_channel_join, update_users_stats_channels_exist
import datetime

def channels_list_v1(auth_user_id):
    """ Lists all channels that the given user id is a member of.

        Arguments:
            auth_user_id (int)    - The user id of the user whose channel membership
                                    is being listed.

        Exceptions:
            AccessError - Occurs when the user's id does not exist in the data store.

        Return Value:
            Returns { channels } on successful completion.
    """

    # Iterates through the list of channels and
    # returns the subset that the given user is a member of.
    store = data_store.get()
    channel_store = store['channels']
    channels = []
    for chan in channel_store:
        if auth_user_id in chan['all_members']:
            channels.append({'channel_id' : chan['id'], 'name' : chan['name']})
    return {
        'channels' : channels
    }

def channels_listall_v1(token):

    """ Lists all channels that exist including public and private channels.

        Arguments:
            token (int)    - The token of the user.

        Exceptions:
            AccessError - Occurs when the token is not valid.

        Return Value:
            Returns { channels } on successful completion.
    """

    # Verifies the token
    check_valid_token(token)['auth_user_id']

    # Iterates through the list of channels and adds them to channels list.
    store = data_store.get()
    channel_store = store['channels']
    channels = []

    for chan in channel_store:
        channels.append({'channel_id' : chan['id'], 'name' : chan['name']})

    # Return the channels list as a value of key channels in a dictionary.
    return {
        'channels' : channels
    }

def channels_create_v1(auth_user_id, name, is_public):
    """ Creates a channel as specified by the parameters.

    Arguments:
        auth_user_id (int)    - The user id of the calling user.
        name (string)         - The name of the channel to be created.
        is_public (boolean)   - Determines whether the channel is public
        ...

    Exceptions:
        InputError  - Occurs when length of name is less than 1 or more than 20 characters.
        AccessError - Occurs when the user's id does not exist in the data store.

    Return Value:
        Returns { channel_id } on successful completion.
    """

    # Verifies that the channel name is of correct length, raises an InputError otherwise.
    if len(name) < 1 or len(name) > 20:
        raise InputError(description="Name needs to be between 1 and 20 characters long.")

    # Creates the channel if call is valid
    # Channel dictionary entry is as follows:
    #     'id'            :   integer type - assigned sequentially
    #     'name'          :   string type
    #     'is_public'     :   boolean
    #     'owner_members' :   list of user ids - creator made an owner
    #     'all_members'   :   list of user ids - creator made a member
    #     'messages'      :   list of dictionaries for message details i.e.
    #                         { message_id, u_id, message, time_created }
    #     'standup'       :   Stores the currently running standup
    store = data_store.get()
    channels = store['channels']
    new_channel = {
        'id': len(channels) + 1,
        'name' : name,
        'is_public' : is_public,
        'owner_members' : [auth_user_id],
        'all_members' : [auth_user_id],
        'messages' :[],
        'standup' : {}
        }
    channels.append(new_channel)
    time_stamp = int(datetime.datetime.utcnow().replace(tzinfo= datetime.timezone.utc).timestamp())
    data_store.set(store)
    update_user_stats_channel_join(auth_user_id, time_stamp)
    update_users_stats_channels_exist(int(1), time_stamp)
    return {
        'channel_id' : new_channel['id']
    }
