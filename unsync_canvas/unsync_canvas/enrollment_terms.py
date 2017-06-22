import unsync
import petl

from pycanvas.apis.enrollment_terms import EnrollmentTermsAPI


@unsync.command()
@unsync.option('--url', required=True, help='Canvas instance to use. Usually something like <schoolname>.instructure.com.')
@unsync.option('--api-key', required=True, help='API Key to use when accessing the Canvas instance. Can be generated in your profile section.')
@unsync.option('--account-id', default=1, help='The Canvas account to access. This is usually the main account.')
@unsync.option('--state', default="all", type=unsync.Choice(["active", "deleted", "all"]), help='Only list Terms with the given state.')
@unsync.option('--destination', '-d', required=True, help='The destination table to store the list of terms.')
def get_enrollment_terms(data, url, api_key, account_id, state, destination):
    if not url.startswith('http') or not url.startswith('https'):
        url = 'https://' + url

    term_data = []

    client = EnrollmentTermsAPI(url, api_key)
    r = client.list_enrollment_terms(account_id, state)
    for term in r:
        term_data.append(term)

    term_data = petl.fromdicts(term_data)
    data.cat(destination, term_data)
