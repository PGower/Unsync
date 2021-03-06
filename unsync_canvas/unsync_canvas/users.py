import unsync
import petl

from pycanvas.apis.users import UsersAPI


@unsync.command()
@unsync.option('--url', required=True, help='Canvas instance to use. Usually something like <schoolname>.instructure.com.')
@unsync.option('--api-key', required=True, help='API Key to use when accessing the Canvas instance. Can be generated in your profile section.')
@unsync.option('--user-data', required=True, help='Name of a data table containing Canvas user IDs')
@unsync.option('--user-id-field', required=True, default='id', help='Name of the column that contains Canvas user IDs')
@unsync.option('--destination', '-d', required=True, help='The destination table for all retrieved data.')
def get_user_profiles(data, url, api_key, user_data, user_id_field, destination):

    if not url.startswith('http') or not url.startswith('https'):
        url = 'https://' + url

    user_data = data.get(user_data)
    user_data = user_data.dicts()

    profile_data = []

    debug = data.config.debug

    client = UsersAPI(url, api_key)
    for user in user_data:
        try:
            r = client.get_user_profile(user[user_id_field])
            profile_data.append(r)
            if debug:
                unsync.secho('Retrieved Profile for Canvas User ID: {}'.format(len(r), user[user_id_field]), fg='green')
        except CanvasAPIError as e:
            unsync.secho('Unable to retrieve Profile for Canvas User ID: {}'.format(user[user_id_field]), fg='red')

    profile_data = petl.fromdicts(profile_data)
    data.set(destination, profile_data)


@unsync.command()
@unsync.option('--url', required=True, help='Canvas instance to use. Usually something like <schoolname>.instructure.com.')
@unsync.option('--api-key', required=True, help='API Key to use when accessing the Canvas instance. Can be generated in your profile section.')
@unsync.option('--account-id', default=1, help='The Canvas account to access. This is usually the main account.')
@unsync.option('--search-term', help='If provided narrow returned results using the search-term.')
@unsync.option('--destination', '-d', required=True, help='Table to store retrieved data in.')
def list_account_users(data, url, api_key, account_id, search_term, destination):
    if not url.startswith('http') or not url.startswith('https'):
        url = 'https://' + url

    client = UsersAPI(url, api_key)
    r = client.list_users_in_account(account_id, search_term)
    data.cat(destination, petl.fromdicts(r))