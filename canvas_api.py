# Super hacky API Client for Canvas
import requests
import re

class CanvasAPI(object):
    def __init__(self, instance_address, access_token):
        self.instance_address = instance_address
        self.access_token = access_token

        self.session = requests.Session()
        self.session.headers.update({'Authorization': 'Bearer {}'.format(self.access_token)})

        self.rel_matcher = re.compile(r' ?rel="([a-z]+)"')


    def uri_for(self, a):
        return self.instance_address + a

    def extract_pagination_links(self, wrapped_response):
        '''Given a wrapped_response from a Canvas API endpoint,
        extract the pagination links from the response headers'''
        response = wrapped_response['response']
        try:
            link_header = response.headers['Link']
        except KeyError:
            return None

        split_header = link_header.split(',')
        exploded_split_header = [i.split(';') for i in split_header]

        pagination_links = {}
        for h in exploded_split_header:
            link = h[0]
            rel = h[1]
            # Check that the link format is what we expect
            if link.startswith('<') and link.endswith('>'):
                link = link[1:-1]
            else:
                continue
            # Extract the rel argument
            m = self.rel_matcher.match(rel)
            try:
                rel = m.groups()[0]
            except AttributeError:
                # Match returned None, just skip.
                continue
            except IndexError:
                # Matched but no groups returned
                continue

            pagination_links[rel] = link
        return pagination_links


    def retrieve_pages(self, wrapped_response):
        '''Given a wrapped response , request and collate all of the pages'''
        data = []
        pagination_links = self.extract_pagination_links(wrapped_response)
        if pagination_links is None:
            return data
        else:
            while 'next' in pagination_links.keys():
                wrapped_response = self.generic_get(pagination_links['next'])
                data.extend(wrapped_response['data'])
                pagination_links = self.extract_pagination_links(wrapped_response)
            return data


    def generic_get(self, uri, all_pages=False, **kwargs):
        if not uri.startswith('http'):
            uri = self.uri_for(uri)
        response = self.session.get(uri, **kwargs)

        if response.status_code != 200:
            raise CanvasAPIError(response)

        data = response.json()

        if all_pages:
            unwrapped_data = self.retrieve_pages({'response': response})
            data.extend(unwrapped_data)
            pagination_links = None
        else:
            pagination_links = self.extract_pagination_links({'response': response})

        wrapped_response = {
            'data': data,
            'response': response,
            'pagination': pagination_links,
        }
        return wrapped_response

    def generic_post(self, uri, **kwargs):
        if not uri.startswith('http'):
            uri = self.uri_for(uri)
        response = self.session.post(uri, **kwargs)

        if response.status_code != 200:
            raise CanvasAPIError(response)

        data = response.json()

        wrapped_response = {
            'data': data,
            'response': response,
            'pagination': None,
        }
        return wrapped_response

    def list_roles(self, account_id=1):
        '''Get all of the defined roles for the given account_id.
        account_id defaults to the root account'''
        return self.generic_get('/api/v1/accounts/{}/roles'.format(account_id), all_pages=True)


    def list_child_accounts(self, account_id):
        '''Given a parent account_id retrieve all child accounts'''
        return self.generic_get('/api/v1/accounts/{}/sub_accounts'.format(account_id), all_pages=True)


    def list_root_accounts(self):
        '''Get the Canvas root accounts that I can see'''
        return self.generic_get('/api/v1/accounts', params={'page_size': 30})  # Root Account


    def recursive_accounts(self, account_id):
        accounts = []
        data = self.list_child_accounts(account_id)['data']
        for account in data:
            accounts.append(account)
            accounts.extend(self.recursive_accounts(account['id']))
        return accounts


    def list_all_accounts(self):
        '''Get all accounts recursivly'''
        account_data = []
        data = self.list_root_accounts()['data']
        for root_account in data:
            account_data.append(root_account)
            account_data.extend(self.recursive_accounts(root_account['id']))
        return account_data


    def list_roles_for_account(self, account_id, show_inherited=False, state=None):
        '''Get all roles for the given account'''
        assert state in [None, 'active', 'inactive']
        assert show_inherited in [False, True]
        params = {'show_inherited': show_inherited}
        if state is not None:
            params['state'] = state
        return self.generic_get('/api/v1/accounts/{}/roles'.format(account_id), params=params)


    def list_all_roles(self):
        '''list all roles for all accounts'''
        accounts = self.list_all_accounts()
        roles = {}
        for account in accounts:
            account_roles = self.list_roles_for_account(account['id'])
            for account_role in account_roles:
                roles[account_role['id']] = account_role
        return roles.values()


    def list_terms_for_account(self, account_id, state='all'):
        assert state in ['all', 'active', 'deleted']
        params = {'workflow_state': state}
        return self.generic_get('/api/v1/accounts/{}/terms'.format(account_id), params=params)


    # def list_all_terms():
    #     '''list all terms for all accounts'''
    #     # I am going to assume that all of the terms are created in the base account
    #     base_account = 1


    def list_courses_in_account(self,
                                account_id,
                                with_enrollments=None,
                                enrollment_type=None,
                                published=None,
                                completed=None,
                                by_teachers=None,
                                state=None,
                                enrollment_term_id=None,
                                search_term=None,
                                include=None):
        '''List courses attached to the given account_id'''
        # Sanity Checks
        assert with_enrollments in [None, True, False]
        if enrollment_type is not None:
            for i in enrollment_type:
                assert i in ['teacher', 'student', 'ta', 'observer', 'designer']
        assert published in [None, True, False]
        assert completed in [None, True, False]
        if by_teachers is not None:
            for i in by_teachers:
                assert type(i) == int
        if state is not None:
            for i in state:
                assert i in ['created', 'claimed', 'available', 'completed', 'deleted', 'all']
        if enrollment_term_id is not None: assert type(enrollment_term_id) == int
        if include is not None:
            for i in include:
                assert i in ['syllabus_body', 'term', 'course_progress', 'storage_quota_used_mb', 'total_students', 'teachers']
        params = {}
        for pk, pv in (('with_enrollments', with_enrollments),
                       ('enrollment_type', enrollment_type),
                       ('published', published),
                       ('completed', completed),
                       ('by_teachers', by_teachers),
                       ('state', state),
                       ('enrollment_term_id', enrollment_term_id),
                       ('search_term', search_term),
                       ('include', include)):
            if pv is None:
                continue
            else:
                params[pk] = pv
        return self.generic_get('/api/v1/accounts/{}/courses'.format(account_id), all_pages=True, params=params)


    def list_sections_in_course(self, course_id, include=None):
        params = {}
        if include is not None:
            # assert include is iterable
            for i in include:
                assert i in ['students', 'avatar_url', 'enrollments', 'total_students', 'passback_status']
            params['include'] = include
        return self.generic_get('/api/v1/courses/{}/sections'.format(course_id), params=params, all_pages=True)


    def list_users_in_account(self, account_id, search_term=None, include=[]):
        params = {}
        if search_term is not None:
            params = {'search_term': search_term}
        if include != []:
            for i in include:
                params['include[{}]'.format(i)] = True
        return self.generic_get('/api/v1/accounts/{}/users'.format(account_id), params=params, all_pages=True)


    def list_enrollments_in_course(self, course_id, type=None, role=None, state=None, user_id=None, grading_period_id=None):
        params = {}
        # Fix params
        return self.generic_get('/api/v1/courses/{}/enrollments'.format(course_id), all_pages=True, params=params)

    def upload_sis_import_file(self,
                               account_id,
                               file_path,
                               import_type='instructure_csv',
                               batch_mode=None,
                               batch_mode_term_id=None,
                               override_sis_stickiness=None,
                               add_sis_stickiness=None,
                               clear_sis_stickiness=None,
                               diffing_data_set_identifier=None,
                               diffing_remaster_data_set=None):
        data = {'import_type': import_type}
        if batch_mode is not None:
            assert type(batch_mode) == bool
            data['batch_mode'] = batch_mode
        if batch_mode_term_id is not None:
            data['batch_mode_term_id'] = batch_mode_term_id
        if override_sis_stickiness is not None:
            assert type(override_sis_stickiness) == bool
            data['override_sis_stickiness'] = override_sis_stickiness
        if add_sis_stickiness is not None:
            assert type(add_sis_stickiness) == bool
            data['add_sis_stickiness'] = add_sis_stickiness
        if clear_sis_stickiness is not None:
            assert type(clear_sis_stickiness) == bool
            data['clear_sis_stickiness'] = clear_sis_stickiness
        if diffing_data_set_identifier is not None:
            data['diffing_data_set_identifier'] = diffing_data_set_identifier
        if diffing_remaster_data_set is not None:
            assert type(diffing_remaster_data_set) == bool
            data['diffing_remaster_data_set'] = diffing_remaster_data_set
        with open(file_path, 'rb') as f:
            return self.generic_post('/api/v1/accounts/{}/sis_imports'.format(account_id), data=data, files={'attachment': ('data.zip', f)})

    def list_sis_imports(self, account_id, created_since=None):
        params = {}
        if created_since is not None:
            params['created_since'] = created_since
        return self.generic_get('/api/v1/accounts/{}/sis_imports'.format(account_id), params=params)



class CanvasAPIError(Exception):
    def init(self, response):
        self.code = response.status_code
        self.reason = response.reason
        self.response = response

    def __unicode__(self):
        return u'API Request Failed. Response Status was {}, reason was {}'.format(self.code, self.reason)


