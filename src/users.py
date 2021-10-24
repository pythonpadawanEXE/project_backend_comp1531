from src.data_store import data_store

def users_all_v1():
    store = data_store.get()
    users_store = store['users']
    users = {'users' : []}
    for user in users_store:
        if user['name_first'] == "Removed":
            continue
        
        users['users'].append({
            'u_id': user['u_id'],
            'email' : user['email'],
            'name_first' : user['name_first'],
            'name_last'  : user['name_last'],
            'handle_str' : user['handle_str']
        })

    return users
