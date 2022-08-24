import sys
import unittest

from httmock import urlmatch, response, HTTMock

from pymod import AmsUser, AmsUserProject
from pymod import ArgoMessagingService


class TestUser(unittest.TestCase):

    def setUp(self):
        self.ams = ArgoMessagingService(endpoint="localhost", token="s3cr3t",
                                        project="TEST")

        project = AmsUserProject(project="e2epush", roles=["consumer"], topics=["t1"], subscriptions=["s1"])
        project2 = AmsUserProject(project="test-aggr-project", roles=["publisher"])
        self.default_user = AmsUser(name="test-lib", email="lol@gmail.com",
                                    firstname="first", lastname="last",
                                    description="desc", organization="org",
                                    modified_on="now", created_on="now", created_by="admin", token="token", uuid="u1",
                                    projects=[project, project2], service_roles=["service_admin"])

        self.user_json = """{"projects": [
                    {"project": "e2epush", "roles": ["consumer"], "topics": ["t1"], "subscriptions": ["s1"]},
                    {"project": "test-aggr-project", "roles": ["publisher"]}], "name": "test-user_create",
                    "first_name": "first", "last_name": "last", "description": "desc", "organization": "org",
                    "email": "lol@gmail.com", "service_roles": ["service_admin"], "token": "token", "uuid": "u1",
                    "modified_on": "now", "created_on": "now", "created_by": "admin", "name": "test-lib"}"""

        self.users_json = """{"totalSize": 3, "nextPageToken":"token", "users": [{"projects": [
                    {"project": "e2epush", "roles": ["consumer"], "topics": ["t1"], "subscriptions": ["s1"]},
                    {"project": "test-aggr-project", "roles": ["publisher"]}], "name": "test-user_create",
                    "first_name": "first", "last_name": "last", "description": "desc", "organization": "org",
                    "email": "lol@gmail.com", "service_roles": ["service_admin"], "token": "token", "uuid": "u1",
                    "modified_on": "now", "created_on": "now", "created_by": "admin", "name": "test-lib"}]}"""

    create_user_urlmatch = dict(netloc="localhost",
                                path="/v1/users/test-user-create",
                                method='POST')

    update_user_urlmatch = dict(netloc="localhost",
                                path="/v1/users/test-user",
                                method='PUT')

    get_user_urlmatch = dict(netloc="localhost",
                             path="/v1/users/test-user-create",
                             method='GET')

    get_user_by_token_urlmatch = dict(netloc="localhost",
                                      path="/v1/users:byToken/token",
                                      method='GET')

    get_user_by_uuid_urlmatch = dict(netloc="localhost",
                                     path="/v1/users:byUUID/u1",
                                     method='GET')

    get_user_profile_urlmatch = dict(netloc="localhost",
                                     path="/v1/users/profile",
                                     method='GET')

    users_list_urlmatch = dict(netloc="localhost",
                               path="/v1/users",
                               method='GET')

    delete_user_urlmatch = dict(netloc="localhost",
                                path="/v1/users/test-user",
                                method='DELETE')

    refresh_user_token_urlmatch = dict(netloc="localhost",
                                       path="/v1/users/test-user:refreshToken",
                                       method='POST')

    def testCreateUser(self):
        @urlmatch(**self.create_user_urlmatch)
        def create_user_mock(url, request):
            self.assertEqual("/v1/users/test-user-create", url.path)
            self.assertEqual("POST", request.method)
            return response(200, self.user_json, None, None, 5, request)

        # Execute ams client with mocked response
        with HTTMock(create_user_mock):
            user = AmsUser(name="test-user-create")
            created_user = self.ams.create_user(user=user)

            self.assertEqual(self.default_user.name, created_user.name)
            self.assertEqual(self.default_user.email, created_user.email)
            self.assertEqual(self.default_user.uuid, created_user.uuid)
            self.assertEqual(self.default_user.token, created_user.token)
            self.assertEqual(self.default_user.modified_on, created_user.modified_on)
            self.assertEqual(self.default_user.created_by, created_user.created_by)
            self.assertEqual(self.default_user.created_on, created_user.created_on)
            self.assertEqual(self.default_user.firstname, created_user.firstname)
            self.assertEqual(self.default_user.lastname, created_user.lastname)
            self.assertEqual(self.default_user.description, created_user.description)
            self.assertEqual(self.default_user.organization, created_user.organization)
            self.assertEqual(self.default_user.service_roles, created_user.service_roles)
            self.assertEqual(self.default_user.projects[0].project, created_user.projects[0].project)
            self.assertEqual(self.default_user.projects[0].roles, created_user.projects[0].roles)
            self.assertEqual(self.default_user.projects[0].subscriptions, created_user.projects[0].subscriptions)
            self.assertEqual(self.default_user.projects[0].topics, created_user.projects[0].topics)
            self.assertEqual(self.default_user.projects[1].project, created_user.projects[1].project)
            self.assertEqual(self.default_user.projects[1].roles, created_user.projects[1].roles)
            self.assertEqual(self.default_user.projects[1].subscriptions, created_user.projects[1].subscriptions)
            self.assertEqual(self.default_user.projects[1].topics, created_user.projects[1].topics)

    def testUpdateUser(self):
        @urlmatch(**self.update_user_urlmatch)
        def update_user_mock(url, request):
            self.assertEqual("/v1/users/test-user", url.path)
            self.assertEqual("PUT", request.method)
            self.assertTrue('"first_name": "f1u"' in request.body)
            self.assertTrue('"last_name": "l1u"' in request.body)
            self.assertTrue('"organization": "ou"' in request.body)
            self.assertTrue('"description": "du"' in request.body)
            self.assertTrue('"service_roles": ["service_admin"]' in request.body)
            self.assertTrue('"name": "testu"' in request.body)
            self.assertTrue('"email": "eu@gmail.com"' in request.body)
            self.assertTrue('"project": "testp"' in request.body)
            self.assertTrue('"roles": ["publisher"]' in request.body)
            self.assertTrue('"projects": [{' in request.body)


            return response(200, self.user_json, None, None, 5, request)

        # Execute ams client with mocked response
        with HTTMock(update_user_mock):
            created_user = self.ams.update_user(name="test-user",
                                                first_name="f1u",
                                                last_name="l1u",
                                                organization="ou",
                                                description="du",
                                                service_roles=["service_admin"],
                                                username="testu",
                                                email="eu@gmail.com",
                                                projects=[AmsUserProject(project="testp", roles=["publisher"])])

            self.assertEqual(self.default_user.name, created_user.name)
            self.assertEqual(self.default_user.email, created_user.email)
            self.assertEqual(self.default_user.uuid, created_user.uuid)
            self.assertEqual(self.default_user.token, created_user.token)
            self.assertEqual(self.default_user.modified_on, created_user.modified_on)
            self.assertEqual(self.default_user.created_by, created_user.created_by)
            self.assertEqual(self.default_user.created_on, created_user.created_on)
            self.assertEqual(self.default_user.firstname, created_user.firstname)
            self.assertEqual(self.default_user.lastname, created_user.lastname)
            self.assertEqual(self.default_user.description, created_user.description)
            self.assertEqual(self.default_user.organization, created_user.organization)
            self.assertEqual(self.default_user.service_roles, created_user.service_roles)
            self.assertEqual(self.default_user.projects[0].project, created_user.projects[0].project)
            self.assertEqual(self.default_user.projects[0].roles, created_user.projects[0].roles)
            self.assertEqual(self.default_user.projects[0].subscriptions, created_user.projects[0].subscriptions)
            self.assertEqual(self.default_user.projects[0].topics, created_user.projects[0].topics)
            self.assertEqual(self.default_user.projects[1].project, created_user.projects[1].project)
            self.assertEqual(self.default_user.projects[1].roles, created_user.projects[1].roles)
            self.assertEqual(self.default_user.projects[1].subscriptions, created_user.projects[1].subscriptions)
            self.assertEqual(self.default_user.projects[1].topics, created_user.projects[1].topics)

    def testGetUser(self):
        @urlmatch(**self.get_user_urlmatch)
        def get_user_mock(url, request):
            self.assertEqual("/v1/users/test-user-create", url.path)
            self.assertEqual("GET", request.method)
            return response(200, self.user_json, None, None, 5, request)

        # Execute ams client with mocked response
        with HTTMock(get_user_mock):
            created_user = self.ams.get_user(name="test-user-create")

            self.assertEqual(self.default_user.name, created_user.name)
            self.assertEqual(self.default_user.email, created_user.email)
            self.assertEqual(self.default_user.uuid, created_user.uuid)
            self.assertEqual(self.default_user.token, created_user.token)
            self.assertEqual(self.default_user.modified_on, created_user.modified_on)
            self.assertEqual(self.default_user.created_by, created_user.created_by)
            self.assertEqual(self.default_user.created_on, created_user.created_on)
            self.assertEqual(self.default_user.firstname, created_user.firstname)
            self.assertEqual(self.default_user.lastname, created_user.lastname)
            self.assertEqual(self.default_user.description, created_user.description)
            self.assertEqual(self.default_user.organization, created_user.organization)
            self.assertEqual(self.default_user.service_roles, created_user.service_roles)
            self.assertEqual(self.default_user.projects[0].project, created_user.projects[0].project)
            self.assertEqual(self.default_user.projects[0].roles, created_user.projects[0].roles)
            self.assertEqual(self.default_user.projects[0].subscriptions, created_user.projects[0].subscriptions)
            self.assertEqual(self.default_user.projects[0].topics, created_user.projects[0].topics)
            self.assertEqual(self.default_user.projects[1].project, created_user.projects[1].project)
            self.assertEqual(self.default_user.projects[1].roles, created_user.projects[1].roles)
            self.assertEqual(self.default_user.projects[1].subscriptions, created_user.projects[1].subscriptions)
            self.assertEqual(self.default_user.projects[1].topics, created_user.projects[1].topics)

    def testGetUserByToken(self):
        @urlmatch(**self.get_user_by_token_urlmatch)
        def get_user_by_token_mock(url, request):
            self.assertEqual("/v1/users:byToken/token", url.path)
            self.assertEqual("GET", request.method)
            return response(200, self.user_json, None, None, 5, request)

        # Execute ams client with mocked response
        with HTTMock(get_user_by_token_mock):
            created_user = self.ams.get_user_by_token(token="token")

            self.assertEqual(self.default_user.name, created_user.name)
            self.assertEqual(self.default_user.email, created_user.email)
            self.assertEqual(self.default_user.uuid, created_user.uuid)
            self.assertEqual(self.default_user.token, created_user.token)
            self.assertEqual(self.default_user.modified_on, created_user.modified_on)
            self.assertEqual(self.default_user.created_by, created_user.created_by)
            self.assertEqual(self.default_user.created_on, created_user.created_on)
            self.assertEqual(self.default_user.firstname, created_user.firstname)
            self.assertEqual(self.default_user.lastname, created_user.lastname)
            self.assertEqual(self.default_user.description, created_user.description)
            self.assertEqual(self.default_user.organization, created_user.organization)
            self.assertEqual(self.default_user.service_roles, created_user.service_roles)
            self.assertEqual(self.default_user.projects[0].project, created_user.projects[0].project)
            self.assertEqual(self.default_user.projects[0].roles, created_user.projects[0].roles)
            self.assertEqual(self.default_user.projects[0].subscriptions, created_user.projects[0].subscriptions)
            self.assertEqual(self.default_user.projects[0].topics, created_user.projects[0].topics)
            self.assertEqual(self.default_user.projects[1].project, created_user.projects[1].project)
            self.assertEqual(self.default_user.projects[1].roles, created_user.projects[1].roles)
            self.assertEqual(self.default_user.projects[1].subscriptions, created_user.projects[1].subscriptions)
            self.assertEqual(self.default_user.projects[1].topics, created_user.projects[1].topics)

    def testGetUserByUUID(self):
        @urlmatch(**self.get_user_by_uuid_urlmatch)
        def get_user_by_uuid_mock(url, request):
            self.assertEqual("/v1/users:byUUID/u1", url.path)
            self.assertEqual("GET", request.method)
            return response(200, self.user_json, None, None, 5, request)

        # Execute ams client with mocked response
        with HTTMock(get_user_by_uuid_mock):
            created_user = self.ams.get_user_by_uuid(uuid="u1")

            self.assertEqual(self.default_user.name, created_user.name)
            self.assertEqual(self.default_user.email, created_user.email)
            self.assertEqual(self.default_user.uuid, created_user.uuid)
            self.assertEqual(self.default_user.token, created_user.token)
            self.assertEqual(self.default_user.modified_on, created_user.modified_on)
            self.assertEqual(self.default_user.created_by, created_user.created_by)
            self.assertEqual(self.default_user.created_on, created_user.created_on)
            self.assertEqual(self.default_user.firstname, created_user.firstname)
            self.assertEqual(self.default_user.lastname, created_user.lastname)
            self.assertEqual(self.default_user.description, created_user.description)
            self.assertEqual(self.default_user.organization, created_user.organization)
            self.assertEqual(self.default_user.service_roles, created_user.service_roles)
            self.assertEqual(self.default_user.projects[0].project, created_user.projects[0].project)
            self.assertEqual(self.default_user.projects[0].roles, created_user.projects[0].roles)
            self.assertEqual(self.default_user.projects[0].subscriptions, created_user.projects[0].subscriptions)
            self.assertEqual(self.default_user.projects[0].topics, created_user.projects[0].topics)
            self.assertEqual(self.default_user.projects[1].project, created_user.projects[1].project)
            self.assertEqual(self.default_user.projects[1].roles, created_user.projects[1].roles)
            self.assertEqual(self.default_user.projects[1].subscriptions, created_user.projects[1].subscriptions)
            self.assertEqual(self.default_user.projects[1].topics, created_user.projects[1].topics)

    def testGetUserProfile(self):
        @urlmatch(**self.get_user_profile_urlmatch)
        def get_user_profile_mock(url, request):
            self.assertEqual("/v1/users/profile", url.path)
            self.assertEqual("GET", request.method)
            return response(200, self.user_json, None, None, 5, request)

        # Execute ams client with mocked response
        with HTTMock(get_user_profile_mock):
            created_user = self.ams.get_user_profile()

            self.assertEqual(self.default_user.name, created_user.name)
            self.assertEqual(self.default_user.email, created_user.email)
            self.assertEqual(self.default_user.uuid, created_user.uuid)
            self.assertEqual(self.default_user.token, created_user.token)
            self.assertEqual(self.default_user.modified_on, created_user.modified_on)
            self.assertEqual(self.default_user.created_by, created_user.created_by)
            self.assertEqual(self.default_user.created_on, created_user.created_on)
            self.assertEqual(self.default_user.firstname, created_user.firstname)
            self.assertEqual(self.default_user.lastname, created_user.lastname)
            self.assertEqual(self.default_user.description, created_user.description)
            self.assertEqual(self.default_user.organization, created_user.organization)
            self.assertEqual(self.default_user.service_roles, created_user.service_roles)
            self.assertEqual(self.default_user.projects[0].project, created_user.projects[0].project)
            self.assertEqual(self.default_user.projects[0].roles, created_user.projects[0].roles)
            self.assertEqual(self.default_user.projects[0].subscriptions, created_user.projects[0].subscriptions)
            self.assertEqual(self.default_user.projects[0].topics, created_user.projects[0].topics)
            self.assertEqual(self.default_user.projects[1].project, created_user.projects[1].project)
            self.assertEqual(self.default_user.projects[1].roles, created_user.projects[1].roles)
            self.assertEqual(self.default_user.projects[1].subscriptions, created_user.projects[1].subscriptions)
            self.assertEqual(self.default_user.projects[1].topics, created_user.projects[1].topics)

    def testListUsers(self):
        @urlmatch(**self.users_list_urlmatch)
        def list_users_mock(url, request):
            self.assertEqual("/v1/users", url.path)
            self.assertEqual("GET", request.method)
            self.assertTrue("details=True" in url.query)
            self.assertTrue("pageSize=1" in url.query)
            self.assertTrue("nextPageToken=token" in url.query)
            return response(200, self.users_json, None, None, 5, request)

        # Execute ams client with mocked response
        with HTTMock(list_users_mock):
            users_page = self.ams.list_users(details=True, page_size=1, next_page_token="token")

            self.assertEqual(3, users_page.total_size)
            self.assertEqual("token", users_page.next_page_token)
            self.assertEqual(self.default_user.name, users_page.users[0].name)
            self.assertEqual(self.default_user.email, users_page.users[0].email)
            self.assertEqual(self.default_user.uuid, users_page.users[0].uuid)
            self.assertEqual(self.default_user.token, users_page.users[0].token)
            self.assertEqual(self.default_user.modified_on, users_page.users[0].modified_on)
            self.assertEqual(self.default_user.created_by, users_page.users[0].created_by)
            self.assertEqual(self.default_user.created_on, users_page.users[0].created_on)
            self.assertEqual(self.default_user.firstname, users_page.users[0].firstname)
            self.assertEqual(self.default_user.lastname, users_page.users[0].lastname)
            self.assertEqual(self.default_user.description, users_page.users[0].description)
            self.assertEqual(self.default_user.organization, users_page.users[0].organization)
            self.assertEqual(self.default_user.service_roles, users_page.users[0].service_roles)
            self.assertEqual(self.default_user.projects[0].project, users_page.users[0].projects[0].project)
            self.assertEqual(self.default_user.projects[0].roles, users_page.users[0].projects[0].roles)
            self.assertEqual(self.default_user.projects[0].subscriptions, users_page.users[0].projects[0].subscriptions)
            self.assertEqual(self.default_user.projects[0].topics, users_page.users[0].projects[0].topics)
            self.assertEqual(self.default_user.projects[1].project, users_page.users[0].projects[1].project)
            self.assertEqual(self.default_user.projects[1].roles, users_page.users[0].projects[1].roles)
            self.assertEqual(self.default_user.projects[1].subscriptions, users_page.users[0].projects[1].subscriptions)
            self.assertEqual(self.default_user.projects[1].topics, users_page.users[0].projects[1].topics)

    def testDeleteUser(self):
        @urlmatch(**self.delete_user_urlmatch)
        def delete_user_mock(url, request):
            self.assertEqual("/v1/users/test-user", url.path)
            self.assertEqual("DELETE", request.method)
            return response(200, None, None, None, 5, request)

        # Execute ams client with mocked response
        with HTTMock(delete_user_mock):
            self.ams.delete_user(name="test-user")

    def testRefreshUserToken(self):
        @urlmatch(**self.refresh_user_token_urlmatch)
        def refresh_user_token_mock(url, request):
            self.assertEqual("/v1/users/test-user:refreshToken", url.path)
            self.assertEqual("POST", request.method)
            return response(200, self.user_json, None, None, 5, request)

        # Execute ams client with mocked response
        with HTTMock(refresh_user_token_mock):
            created_user = self.ams.refresh_user_token(name="test-user")

            self.assertEqual(self.default_user.name, created_user.name)
            self.assertEqual(self.default_user.email, created_user.email)
            self.assertEqual(self.default_user.uuid, created_user.uuid)
            self.assertEqual(self.default_user.token, created_user.token)
            self.assertEqual(self.default_user.modified_on, created_user.modified_on)
            self.assertEqual(self.default_user.created_by, created_user.created_by)
            self.assertEqual(self.default_user.created_on, created_user.created_on)
            self.assertEqual(self.default_user.firstname, created_user.firstname)
            self.assertEqual(self.default_user.lastname, created_user.lastname)
            self.assertEqual(self.default_user.description, created_user.description)
            self.assertEqual(self.default_user.organization, created_user.organization)
            self.assertEqual(self.default_user.service_roles, created_user.service_roles)
            self.assertEqual(self.default_user.projects[0].project, created_user.projects[0].project)
            self.assertEqual(self.default_user.projects[0].roles, created_user.projects[0].roles)
            self.assertEqual(self.default_user.projects[0].subscriptions, created_user.projects[0].subscriptions)
            self.assertEqual(self.default_user.projects[0].topics, created_user.projects[0].topics)
            self.assertEqual(self.default_user.projects[1].project, created_user.projects[1].project)
            self.assertEqual(self.default_user.projects[1].roles, created_user.projects[1].roles)
            self.assertEqual(self.default_user.projects[1].subscriptions, created_user.projects[1].subscriptions)
            self.assertEqual(self.default_user.projects[1].topics, created_user.projects[1].topics)

    def testCreateUserInvalidArgument(self):
        try:
            self.ams.create_user(user="u")
        except Exception as e:
            self.assertEqual("user has to be of type AmsUser", str(e))
            self.assertTrue(isinstance(e, ValueError))

    def testUserInitWithWrongServiceRoles(self):
        try:
            AmsUser(name="u1", service_roles=["role1", 8])
        except Exception as e:
            self.assertEqual("service role has to be of type str", str(e))
            self.assertTrue(isinstance(e, ValueError))

    def testUserInitWithWrongProjects(self):
        try:
            AmsUser(name="u1", projects=["project"])
        except Exception as e:
            self.assertEqual("project has to be of type AmsUserProject", str(e))
            self.assertTrue(isinstance(e, ValueError))

    def testUserProjectInitWithWrongRoles(self):
        try:
            AmsUserProject(project="project-1", roles=[8])
        except Exception as e:
            self.assertEqual("role has to be of type str", str(e))
            self.assertTrue(isinstance(e, ValueError))

    def testUserToJsonFullEmpty(self):
        user = AmsUser()
        self.assertEqual("{}", user.to_json())

    def testUserToJsonFull(self):
        project = AmsUserProject(project="e2epush", roles=["consumer"], topics=["t1"])
        project2 = AmsUserProject(project="test-aggr-project", roles=["publisher"], subscriptions=["s1"])
        user = AmsUser(name="test-lib", email="lol@gmail.com",
                       firstname="first", lastname="last",
                       description="desc", organization="org",
                       projects=[project, project2], service_roles=["service_admin"])
        user_json = user.to_json()
        self.assertTrue('"first_name": "first"' in user_json)
        self.assertTrue('"last_name": "last"' in user_json)
        self.assertTrue('"organization": "org"' in user_json)
        self.assertTrue('"description": "desc"' in user_json)
        self.assertTrue('"email": "lol@gmail.com"' in user_json)
        self.assertTrue('"service_roles": ["service_admin"]' in user_json)
        self.assertTrue('projects' in user_json)
        self.assertTrue('"project": "e2epush"' in user_json)
        self.assertTrue('"roles": ["consumer"]' in user_json)
        self.assertTrue('"topics": ["t1"]' in user_json)
        self.assertTrue('"topics": []' in user_json)
        self.assertTrue('"subscriptions": ["s1"]' in user_json)
        self.assertTrue('"subscriptions": []' in user_json)
        self.assertTrue('"roles": ["publisher"]' in user_json)
        self.assertTrue('"project": "test-aggr-project"' in user_json)

    def testUserLoadFromDict(self):
        user_json = {"projects": [
            {"project": "e2epush", "roles": ["consumer"], "topics": ["t1"], "subscriptions": ["s1"]},
            {"project": "test-aggr-project", "roles": ["publisher"]}],
            "first_name": "first", "last_name": "last", "description": "desc", "organization": "org",
            "email": "lol@gmail.com", "service_roles": ["service_admin"], "token": "token", "uuid": "u1",
            "modified_on": "now", "created_on": "now", "created_by": "admin", "name": "test-lib"
        }

        loaded_user = AmsUser().load_from_dict(user_json)

        self.assertEqual(self.default_user.name, loaded_user.name)
        self.assertEqual(self.default_user.email, loaded_user.email)
        self.assertEqual(self.default_user.uuid, loaded_user.uuid)
        self.assertEqual(self.default_user.token, loaded_user.token)
        self.assertEqual(self.default_user.modified_on, loaded_user.modified_on)
        self.assertEqual(self.default_user.created_by, loaded_user.created_by)
        self.assertEqual(self.default_user.created_on, loaded_user.created_on)
        self.assertEqual(self.default_user.firstname, loaded_user.firstname)
        self.assertEqual(self.default_user.lastname, loaded_user.lastname)
        self.assertEqual(self.default_user.description, loaded_user.description)
        self.assertEqual(self.default_user.organization, loaded_user.organization)
        self.assertEqual(self.default_user.service_roles, loaded_user.service_roles)
        self.assertEqual(self.default_user.projects[0].project, loaded_user.projects[0].project)
        self.assertEqual(self.default_user.projects[0].roles, loaded_user.projects[0].roles)
        self.assertEqual(self.default_user.projects[0].subscriptions, loaded_user.projects[0].subscriptions)
        self.assertEqual(self.default_user.projects[0].topics, loaded_user.projects[0].topics)
        self.assertEqual(self.default_user.projects[1].project, loaded_user.projects[1].project)
        self.assertEqual(self.default_user.projects[1].roles, loaded_user.projects[1].roles)
        self.assertEqual(self.default_user.projects[1].subscriptions, loaded_user.projects[1].subscriptions)
        self.assertEqual(self.default_user.projects[1].topics, loaded_user.projects[1].topics)


if __name__ == '__main__':
    unittest.main()
