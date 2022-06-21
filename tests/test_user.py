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
                                    description="desc", organisation="org",
                                    modified_on="now", created_on="now", created_by="admin", token="token", uuid="u1",
                                    projects=[project, project2], service_roles=["service_admin"])

    create_user_urlmatch = dict(netloc="localhost",
                                path="/v1/users/test-user-create",
                                method='POST')

    def testCreateUser(self):
        @urlmatch(**self.create_user_urlmatch)
        def create_user_mock(url, request):
            self.assertEqual("/v1/users/test-user-create", url.path)
            user_json = """{"projects": [
                {"project": "e2epush", "roles": ["consumer"], "topics": ["t1"], "subscriptions": ["s1"]},
                {"project": "test-aggr-project", "roles": ["publisher"]}],
                "first_name": "first", "last_name": "last", "description": "desc", "organisation": "org",
                "email": "lol@gmail.com", "service_roles": ["service_admin"], "token": "token", "uuid": "u1",
                "modified_on": "now", "created_on": "now", "created_by": "admin", "name": "test-lib"}"""
            return response(200, user_json, None, None, 5, request)

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
            self.assertEqual(self.default_user.organisation, created_user.organisation)
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
                       description="desc", organisation="org",
                       projects=[project, project2], service_roles=["service_admin"])
        user_json = user.to_json()
        self.assertTrue('"first_name": "first"' in user_json)
        self.assertTrue('"last_name": "last"' in user_json)
        self.assertTrue('"organisation": "org"' in user_json)
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
            "first_name": "first", "last_name": "last", "description": "desc", "organisation": "org",
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
        self.assertEqual(self.default_user.organisation, loaded_user.organisation)
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
