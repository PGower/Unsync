# # Super hacky API Client for Canvas
# import requests
# import re
# import urllib
# import logging

# logger = logging.getLogger('canvas.api')

# class CanvasAPI(object):
#     def __init__(self, instance_address, access_token):
#         self.instance_address = instance_address
#         self.access_token = access_token
#         logger.debug('Created new CanvasAPI client for instance: {}.'.format('self.instance_address'))

#         self.session = requests.Session()
#         self.session.headers.update({'Authorization': 'Bearer {}'.format(self.access_token)})
#         logger.debug('Using Authorization Token authentication method. Added token to headers: {}'.format('Authorization: Bearer {}'.format(self.access_token)))

#         self.rel_matcher = re.compile(r' ?rel="([a-z]+)"')

#     def uri_for(self, a):
#         return self.instance_address + a

#     def extract_data_from_response(self, response, data_key=None):
#         """Given a response and an optional data_key should return a dictionary of data returned as part of the response."""
#         response_json_data = response.json()
#         # Seems to be two types of response, a dict with keys and then lists of data or a flat list data with no key.
#         if type(response_json_data) == list:
#             # Return the data
#             return response_json_data
#         elif type(response_json_data) == dict:
#             if data_key is None:
#                 return response_json_data
#             else:
#                 return response_json_data[data_key]
#         else:
#             raise CanvasAPIError(response)

#     def extract_pagination_links(self, response):
#         '''Given a wrapped_response from a Canvas API endpoint,
#         extract the pagination links from the response headers'''
#         try:
#             link_header = response.headers['Link']
#         except KeyError:
#             logger.warn('Unable to find the Link header. Unable to continue with pagination.')
#             return None

#         split_header = link_header.split(',')
#         exploded_split_header = [i.split(';') for i in split_header]

#         pagination_links = {}
#         for h in exploded_split_header:
#             link = h[0]
#             rel = h[1]
#             # Check that the link format is what we expect
#             if link.startswith('<') and link.endswith('>'):
#                 link = link[1:-1]
#             else:
#                 continue
#             # Extract the rel argument
#             m = self.rel_matcher.match(rel)
#             try:
#                 rel = m.groups()[0]
#             except AttributeError:
#                 # Match returned None, just skip.
#                 continue
#             except IndexError:
#                 # Matched but no groups returned
#                 continue

#             pagination_links[rel] = link
#         return pagination_links

#     def has_pagination_links(self, response):
#         return 'Link' in response.headers


#     # def retrieve_pages(self, wrapped_response):
#     #     '''Given a wrapped response , request and collate all of the pages'''
#     #     data = []
#     #     import pdb;pdb.set_trace()
#     #     pagination_links = self.extract_pagination_links(wrapped_response)
#     #     if pagination_links is None:
#     #         return data
#     #     else:
#     #         while 'next' in pagination_links.keys():
#     #             wrapped_response = self.generic_get(pagination_links['next'])
#     #             data.extend(wrapped_response['data'])
#     #             pagination_links = self.extract_pagination_links(wrapped_response)
#     #         return data

#     def depaginate(self, response, data_key=None):
#         logging.debug('Attempting to depaginate response from {}'.format(response.url))
#         all_data = []
#         this_data = self.extract_data_from_response(response, data_key=data_key)
#         if this_data is not None:
#             if type(this_data) == list:
#                 all_data += this_data
#             else:
#                 all_data.append(this_data)

#         if self.has_pagination_links(response):
#             pagination_links = self.extract_pagination_links(response)
#             while 'next' in pagination_links:
#                 response = self.session.get(pagination_links['next'])
#                 pagination_links = self.extract_pagination_links(response)
#                 this_data = self.extract_data_from_response(response, data_key=data_key)
#                 if this_data is not None:
#                     if type(this_data) == list:
#                         all_data += this_data
#                     else:
#                         all_data.append(this_data)
#         else:
#             logging.warn('Response from {} has no pagination links.'.format(response.url))
#         return all_data

#     def generic_get(self, uri, all_pages=False, data_key=None, **kwargs):
#         if not uri.startswith('http'):
#             uri = self.uri_for(uri)
#         response = self.session.get(uri, **kwargs)
#         if response.status_code != 200:
#             raise CanvasAPIError(response)

#         data = self.depaginate(response)

#         return data

#     def generic_put(self, uri, all_pages=False, data_key=None, **kwargs):
#         if not uri.startswith('http'):
#             uri = self.uri_for(uri)
#         response = self.session.put(uri, **kwargs)
#         if response.status_code != 200:
#             raise CanvasAPIError(response)

#         data = self.depaginate(response)

#         return data

#     def generic_post(self, uri, **kwargs):
#         if not uri.startswith('http'):
#             uri = self.uri_for(uri)
#         response = self.session.post(uri, **kwargs)

#         if response.status_code != 200:
#             raise CanvasAPIError(response)

#         data = response.json()

#         wrapped_response = {
#             'data': data,
#             'response': response,
#             'pagination': None,
#         }
#         return wrapped_response

#     def generic_request(self, method, uri, all_pages=False, data_key=None, no_data=False, accepted_response_codes=[200], **kwargs):
#         if not uri.startswith('http'):
#             uri = self.uri_for(uri)

#         assert method in ['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS']

#         if method == 'GET':
#             response = self.session.get(uri, **kwargs)
#         elif method == 'POST':
#             response = self.session.post(uri, **kwargs)
#         elif method == 'PUT':
#             response = self.session.put(uri, **kwargs)
#         elif method == 'DELETE':
#             response = self.session.delete(uri, **kwargs)
#         elif method == 'HEAD':
#             response = self.session.head(uri, **kwargs)
#         elif method == 'OPTIONS':
#             response = self.session.options(uri, **kwargs)

#         if response.status_code not in accepted_response_codes:
#             raise CanvasAPIError(response)

#         if no_data:
#             return response.status_code
#         else:
#             return self.depaginate(response, data_key)


#     def list_roles(self, account_id=1):
#         '''Get all of the defined roles for the given account_id.
#         account_id defaults to the root account'''
#         return self.generic_get('/api/v1/accounts/{}/roles'.format(account_id), all_pages=True)


#     def list_child_accounts(self, account_id):
#         '''Given a parent account_id retrieve all child accounts'''
#         return self.generic_get('/api/v1/accounts/{}/sub_accounts'.format(account_id), all_pages=True)


#     def list_root_accounts(self):
#         '''Get the Canvas root accounts that I can see'''
#         return self.generic_get('/api/v1/accounts', params={'page_size': 30})  # Root Account


#     def recursive_accounts(self, account_id):
#         accounts = []
#         data = self.list_child_accounts(account_id)['data']
#         for account in data:
#             accounts.append(account)
#             accounts.extend(self.recursive_accounts(account['id']))
#         return accounts


#     def list_all_accounts(self):
#         '''Get all accounts recursivly'''
#         account_data = []
#         data = self.list_root_accounts()['data']
#         for root_account in data:
#             account_data.append(root_account)
#             account_data.extend(self.recursive_accounts(root_account['id']))
#         return account_data


#     def list_roles_for_account(self, account_id, show_inherited=False, state=None):
#         '''Get all roles for the given account'''
#         assert state in [None, 'active', 'inactive']
#         assert show_inherited in [False, True]
#         params = {'show_inherited': show_inherited}
#         if state is not None:
#             params['state'] = state
#         return self.generic_get('/api/v1/accounts/{}/roles'.format(account_id), params=params)


#     def list_all_roles(self):
#         '''list all roles for all accounts'''
#         accounts = self.list_all_accounts()
#         roles = {}
#         for account in accounts:
#             account_roles = self.list_roles_for_account(account['id'])
#             for account_role in account_roles:
#                 roles[account_role['id']] = account_role
#         return roles.values()


#     def list_terms_for_account(self, account_id, state='all'):
#         assert state in ['all', 'active', 'deleted']
#         params = {'workflow_state': state}
#         return self.generic_request('GET', '/api/v1/accounts/{}/terms'.format(account_id), params=params, all_pages=True, data_key='enrollment_terms')


#     # def list_all_terms():
#     #     '''list all terms for all accounts'''
#     #     # I am going to assume that all of the terms are created in the base account
#     #     base_account = 1


#     def list_courses_in_account(self,
#                                 account_id,
#                                 with_enrollments=None,
#                                 enrollment_type=None,
#                                 published=None,
#                                 completed=None,
#                                 by_teachers=None,
#                                 state=None,
#                                 enrollment_term_id=None,
#                                 search_term=None,
#                                 include=None):
#         '''List courses attached to the given account_id'''
#         # Sanity Checks
#         assert with_enrollments in [None, True, False]
#         if enrollment_type is not None:
#             for i in enrollment_type:
#                 assert i in ['teacher', 'student', 'ta', 'observer', 'designer']
#         assert published in [None, True, False]
#         assert completed in [None, True, False]
#         if by_teachers is not None:
#             for i in by_teachers:
#                 assert type(i) == int
#         if state is not None:
#             for i in state:
#                 assert i in ['created', 'claimed', 'available', 'completed', 'deleted', 'all']
#         if enrollment_term_id is not None: assert type(enrollment_term_id) == int
#         if include is not None:
#             for i in include:
#                 assert i in ['syllabus_body', 'term', 'course_progress', 'storage_quota_used_mb', 'total_students', 'teachers']
#         params = {}
#         for pk, pv in (('with_enrollments', with_enrollments),
#                        ('enrollment_type', enrollment_type),
#                        ('published', published),
#                        ('completed', completed),
#                        ('by_teachers', by_teachers),
#                        ('state', state),
#                        ('enrollment_term_id', enrollment_term_id),
#                        ('search_term', search_term),
#                        ('include', include)):
#             if pv is None:
#                 continue
#             else:
#                 params[pk] = pv
#         return self.generic_get('/api/v1/accounts/{}/courses'.format(account_id), all_pages=True, params=params)


#     def list_sections_in_course(self, course_id, include=None):
#         params = {}
#         if include is not None:
#             # assert include is iterable
#             for i in include:
#                 assert i in ['students', 'avatar_url', 'enrollments', 'total_students', 'passback_status']
#             params['include'] = include
#         return self.generic_get('/api/v1/courses/{}/sections'.format(course_id), params=params, all_pages=True)


#     def list_users_in_account(self, account_id, search_term=None, include=[]):
#         params = {}
#         if search_term is not None:
#             params = {'search_term': search_term}
#         if include != []:
#             for i in include:
#                 params['include[{}]'.format(i)] = True
#         return self.generic_get('/api/v1/accounts/{}/users'.format(account_id), params=params, all_pages=True)


#     def list_enrollments_in_course(self, course_id, type=None, role=None, state=None, user_id=None, grading_period_id=None):
#         params = {}
#         # Fix params
#         return self.generic_get('/api/v1/courses/{}/enrollments'.format(course_id), all_pages=True, params=params)

#     def upload_sis_import_file(self,
#                                account_id,
#                                file_path,
#                                import_type='instructure_csv',
#                                batch_mode=None,
#                                batch_mode_term_id=None,
#                                override_sis_stickiness=None,
#                                add_sis_stickiness=None,
#                                clear_sis_stickiness=None,
#                                diffing_data_set_identifier=None,
#                                diffing_remaster_data_set=None):
#         data = {'import_type': import_type}
#         if batch_mode is not None:
#             assert type(batch_mode) == bool
#             data['batch_mode'] = 1
#         if batch_mode_term_id is not None:
#             data['batch_mode_term_id'] = batch_mode_term_id
#         if override_sis_stickiness is not None:
#             assert type(override_sis_stickiness) == bool
#             data['override_sis_stickiness'] = override_sis_stickiness
#         if add_sis_stickiness is not None:
#             assert type(add_sis_stickiness) == bool
#             data['add_sis_stickiness'] = add_sis_stickiness
#         if clear_sis_stickiness is not None:
#             assert type(clear_sis_stickiness) == bool
#             data['clear_sis_stickiness'] = clear_sis_stickiness
#         if diffing_data_set_identifier is not None:
#             data['diffing_data_set_identifier'] = diffing_data_set_identifier
#         if diffing_remaster_data_set is not None:
#             assert type(diffing_remaster_data_set) == bool
#             data['diffing_remaster_data_set'] = diffing_remaster_data_set
#         # It looks like the Canvas API is doing something weird with the other parameters.
#         # They want a multi-part form in a POST for the file data but they want an urlencoded string for extra params.
#         path = '/api/v1/accounts/{}/sis_imports.json'
#         if data.keys() != []:
#             path += '?' + urllib.urlencode(data)
#         with open(file_path, 'rb') as f:
#             return self.generic_post(path.format(account_id), data=data, files={'attachment': ('data.zip', f)})

#     def list_sis_imports(self, account_id, created_since=None):
#         params = {}
#         if created_since is not None:
#             params['created_since'] = created_since
#         return self.generic_request('GET', '/api/v1/accounts/{}/sis_imports'.format(account_id), params=params, data_key='sis_imports')

#     def get_sis_import_status(self, account_id, sis_import_id):
#         return self.generic_get('/api/v1/accounts/{}/sis_imports/{}'.format(account_id, sis_import_id))

#     def list_logins_for_account(self, account_id):
#         return self.generic_get('/api/v1/accounts/{}/logins'.format(account_id))

#     def list_logins_for_user(self, user_id):
#         return self.generic_get('/api/v1/users/{}/logins'.format(user_id))

#     def edit_user_login(self, account_id, login_id, unique_id=None, password=None, sis_user_id=None, integration_id=None):
#         data = {}
#         if unique_id is not None:
#             data['login[unique_id]'] = unique_id
#         if password is not None:
#             data['login[password]'] = password
#         if sis_user_id is not None:
#             data['login[sis_user_id]'] = sis_user_id
#         if integration_id is not None:
#             data['login[integration_id]'] = integration_id
#         return self.generic_request('PUT', '/api/v1/accounts/{}/logins/{}'.format(account_id, login_id), data=data, no_data=True)

#     def list_users_for_account(self, account_id, search_term=None):
#         params = {}
#         if search_term is not None:
#             params['search_term'] = search_term
#         return self.generic_get('/api/v1/accounts/{}/users'.format(account_id), params=params)

#     def get_user_profile(self, user_id):
#         return self.generic_request('GET', '/api/v1/users/{}/profile'.format(user_id))


#     def list_courses_in_account(self,
#                                 account_id,
#                                 with_enrollments=None,
#                                 enrollment_type=None,
#                                 published=None,
#                                 completed=None,
#                                 by_teachers=None,
#                                 state=None,
#                                 enrollment_term_id=None,
#                                 search_term=None,
#                                 include=None):
#         '''List courses attached to the given account_id'''
#         # Sanity Checks
#         assert with_enrollments in [None, True, False]
#         if enrollment_type is not None:
#             for i in enrollment_type:
#                 assert i in ['teacher', 'student', 'ta', 'observer', 'designer']
#         assert published in [None, True, False]
#         assert completed in [None, True, False]
#         if by_teachers is not None:
#             for i in by_teachers:
#                 assert type(i) == int
#         if state is not None:
#             for i in state:
#                 assert i in ['created', 'claimed', 'available', 'completed', 'deleted', 'all']
#         if enrollment_term_id is not None: assert type(enrollment_term_id) == int
#         if include is not None:
#             for i in include:
#                 assert i in ['syllabus_body', 'term', 'course_progress', 'storage_quota_used_mb', 'total_students', 'teachers']
#         params = {}
#         for pk, pv in (('with_enrollments', with_enrollments),
#                        ('enrollment_type', enrollment_type),
#                        ('published', published),
#                        ('completed', completed),
#                        ('by_teachers', by_teachers),
#                        ('state', state),
#                        ('enrollment_term_id', enrollment_term_id),
#                        ('search_term', search_term),
#                        ('include', include)):
#             if pv is None:
#                 continue
#             else:
#                 params[pk] = pv
#         return self.generic_get('/api/v1/accounts/{}/courses'.format(account_id), all_pages=True, params=params)


# class CanvasAPIError(Exception):
#     def __init__(self, response):
#         self.response = response

#     def __unicode__(self):
#         return u'API Request Failed. Status: {} Content: {}'.format(self.response.status_code, self.response.content)

#     def __str__(self):
#         return 'API Request Failed. Status: {} Content: {}'.format(self.response.status_code, self.response.content)


# class CanvasDataKeyError(Exception):
#     def __init__(self):
#         pass