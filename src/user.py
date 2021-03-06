"""
user.py

This module handles user related functions for the streams web app.

Functions:
    user_profile_v1(auth_user_id, u_id) -> { user }
    user_profile_setname_v1(token, name_first, name_last) -> {}
    user_profile_setemail_v1(token, email) -> {}
    user_profile_sethandle_v1(token, handle_str) -> {}

"""

from src.data_store import data_store
from src.error import InputError, AccessError
from src.other import verify_user_id, check_valid_token, check_email_validity, search_duplicate_email, is_handle_exist, get_user_involvement_rate
from src import config
import sys
import urllib.request
import requests
from PIL import Image


def user_profile_v1(auth_user_id, u_id):
    """ For a valid user, returns information about their user_id, email, first name, last name, and handle
    
        Arguments:
            auth_user_id (int)    - The user ID of the user who is calling user_profile_v1.
            u_id (int)            - The user ID of the user who's profile is being sent.

        Exceptions:
            InputError  - u_id does not refer to a valid user,

            AccessError - the authorised user does not exist

        Return Value:
            Returns { user } on successful completion.
    """

    found = False
    target_user = {}
    store = data_store.get()
    users_store = store['users']
    for user in users_store:
        if u_id == user['u_id']:
            found = True
            target_user = user

    if not found:
        raise InputError(description="u_id does not refer to a valid user")

    return {'user' : {
            'u_id': target_user['u_id'],
            'email' : target_user['email'],
            'name_first' : target_user['name_first'],
            'name_last'  : target_user['name_last'],
            'handle_str' : target_user['handle_str'],
            'profile_img_url': target_user['profile_img_url']
        }
    }

def user_profile_setname_v1(token, name_first, name_last):
    """ Update the authorised user's first and last name
    
        Arguments:
            token (string)        - The token of the user who is calling user_profile_setname_v1.
            name_first (string)   - The new first name for this user
            name_last (string)    - The new last name for this user

        Exceptions:
            InputError  - length of name_first is not between 1 and 50 characters inclusive
                        - length of name_last is not between 1 and 50 characters inclusive

            AccessError - the authorised user does not exist

        Return Value:
            Returns { } on successful completion.
    """

    # Get the u_id from the token
    u_id = check_valid_token(token)['auth_user_id']

    length_name_first = len(name_first)
    length_name_last = len(name_last)

    # length of name_first is not between 1 and 50 characters inclusive
    if (length_name_first < 1 or length_name_first > 50):
        raise InputError(description="length of name_first is not between 1 and 50 characters inclusive")

    # length of name_last is not between 1 and 50 characters inclusive
    if (length_name_last < 1 or length_name_last > 50):
        raise InputError(description="length of name_last is not between 1 and 50 characters inclusive")

    # Get all users
    store = data_store.get()
    users = store['users']

    # Find the user to be updated
    for user in users:
        if u_id == user['u_id']:
            # Update users name
            user['name_first'] = name_first
            user['name_last'] = name_last

    data_store.save()

    return {}

def user_profile_setemail_v1(token, email):
    """ Update the authorised user's email address
    
        Arguments:
            token (string)        - The token of the user who is calling user_profile_setemail_v1.
            email (string)        - The new email the user wishes to use

        Exceptions:
            InputError  - email entered is not a valid email
                        - email address is already being used by another user

            AccessError - the authorised user does not exist

        Return Value:
            Returns { } on successful completion.
    """

    # Get the u_id from the token
    u_id = check_valid_token(token)['auth_user_id']

    # email entered is not a valid email
    check_email_validity(email)
        
    # email address is already being used by another user
    if search_duplicate_email(email):
        raise InputError(description="email address is already being used by another user")

    # Get all users
    store = data_store.get()
    users = store['users']

    # Find the user to be updated
    for user in users:
        if u_id == user['u_id']:
            # Update the authorised user's email address
            user['email'] = email

    data_store.save()

    return {}

def user_profile_sethandle_v1(token, handle_str):
    """ Update the authorised user's handle (i.e. display name)
    
        Arguments:
            token (string)        - The token of the user who is calling user_profile_sethandle_v1.
            handle_str (string)   - The new email the user wishes to use

        Exceptions:
            InputError  - length of handle_str is not between 3 and 20 characters inclusive
                        - handle_str contains characters that are not alphanumeric
                        - the handle is already used by another user

            AccessError - the authorised user does not exist

        Return Value:
            Returns { } on successful completion.
    """

    # Get the u_id from the token
    u_id = check_valid_token(token)['auth_user_id']

    # length of handle_str is not between 3 and 20 characters inclusive
    length_handle_str = len(handle_str)
    if (length_handle_str < 3 or length_handle_str > 20):
        raise InputError(description="length of handle_str is not between 3 and 20 characters inclusive")

    # handle_str contains characters that are not alphanumeric
    # i.e) a-z, A-Z, 0-9
    if not handle_str.isalnum():
        raise InputError(description="handle_str contains characters that are not alphanumeric")

    # the handle is already used by another user
    if is_handle_exist(handle_str):
        raise InputError(description="the handle is already used by another user")

    # Get all users
    store = data_store.get()
    users = store['users']

    # Find the user to be updated
    for user in users:
        if u_id == user['u_id']:
            # Update the authorised user's handle (i.e. display name)
            user['handle_str'] = handle_str

    data_store.save()

    return {}

def notifications_get(token):
    """ Return the user's most recent 20 notifications, ordered from most recent to least recent.
    
        Arguments:
            token (string)  - The token of the user who is calling notifications_get_v1.

        Exceptions:
            AccessError     - the authorised user does not exist

        Return Value:
            Returns { notifications } on successful completion.
    """

    # Get the u_id from the token
    u_id = check_valid_token(token)['auth_user_id']

    # Get data store
    store = data_store.get()
    users = store['users']

    # Find the last 20 notifications for the authorised user
    for user in users:
        if (u_id == user['u_id']):
            user_notifications = user['notifications'][-20:][::-1]

    return {'notifications' : user_notifications}

def user_stats_v1(token):
    """ Return the user's statistics in channels_joined, dms_joined, messages_sent and involvement_rate with time stamps for every changes they made
    
        Arguments:
            token (string)  - The token of the user who is calling notifications_get_v1.


        Return Value:
            Returns { user_stats }
    """
    auth_user_id = check_valid_token(token)['auth_user_id']
    
    store = data_store.get()
    user_store = store['users']

    for user in user_store:
        if user['u_id'] == auth_user_id:
            channels_joined = user['user_stats']['channels_joined']
            dms_joined = user['user_stats']['dms_joined']
            messages_sent = user['user_stats']['messages_sent']
            involvement_rate = get_user_involvement_rate(auth_user_id)
    print(channels_joined)
    print(dms_joined)
    print(messages_sent)
    
    return {'user_stats':{'channels_joined': channels_joined,
                           'dms_joined': dms_joined,
                           'messages_sent': messages_sent,
                           'involvement_rate': involvement_rate
                          }       
            }

def user_profile_uploadphoto_v1(token, img_url, x_start, y_start, x_end, y_end):
    """ Download the photo from url into local file, corp the photo within bounds, and upload the local image url to user profile
    
        Arguments:
            token (string)  - The token of the user who is calling notifications_get_v1.
            img_url (string) - The url of an image on the internet
            x_start (int) - bound
            y_statr (int) - bound
            x_end (int) - bound
            y_end (int) - bound

        Exceptions:
            Inputerror - img_url returns an HTTP status other than 200
                       - any of x_start, y_start, x_end, y_end are not within the dimensions of the image at the URL
                       - x_end is less than x_start or y_end is less that y_start
                       - image uploaded is not a JPG

        Return Value:
            Returns {}
    """
    auth_user_id = check_valid_token(token)['auth_user_id']

    store = data_store.get()
    user_store = store['users']

    #check whether the img_url returns an HTTP status other than 200 or not
    check_status = requests.head(img_url)
    if check_status.status_code != 200:
        raise InputError(description = "img_url returns an HTTP status other than 200")

    #check whether the image is not a jpg or not
    if '.jpg' not in img_url:
        raise InputError(description = "image uploaded is not a JPG") 

    #check whether x_end is less than x_start or y_end is less than y_start or not 
    if x_end < x_start:
        raise InputError(description = "x_end less than x_start")
    elif y_end < y_start:
        raise InputError(description = "y_end less than y_start")

    #count number of times change
    for user in user_store:
        if user['u_id'] == auth_user_id:
            change_times = user['upload_photo_time']
            change_times += 1
            user['upload_photo_time'] = change_times
    
    #download image by given url
    directory = 'src/static/' + str(auth_user_id) + '_' + str(change_times) +'.jpg'
    urllib.request.urlretrieve(img_url, directory)

    #check whether x_start, y_start, x_end, y_end are within the dimensions of the image at the URL or not
    imageObject = Image.open(directory)
    width, height = imageObject.size
    if x_start not in range(0,width) or x_end not in range(0,width):
        raise InputError(description = "x_start or x_end not within image dimensions")
    if y_start not in range(0,height) or y_end not in range(0,height):
        raise InputError(description = "y_start or y_end not within image dimensions")

    #crop image
    cropped = imageObject.crop((x_start, y_start, x_end, y_end))
    cropped.save(directory)

    local_img_url = config.url + 'static/' + str(auth_user_id) + '_' + str(change_times) + '.jpg'
    #update user profile
    for user in user_store:
        if user['u_id'] == auth_user_id:
            user['profile_img_url'] = local_img_url
    
    data_store.save()

    return {}
