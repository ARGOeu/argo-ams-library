import unittest

from httmock import urlmatch, response, HTTMock

from pymod import AmsUser, AmsUserProject
from pymod import ArgoMessagingService


class TestProject(unittest.TestCase):

    def setUp(self):
        self.ams = ArgoMessagingService(endpoint="localhost", token="s3cr3t",
                                        project="test-proj")

        self.member_json = """{"projects": [
                    {"project": "test-proj", "roles": ["consumer"], "topics": [], "subscriptions": []}] ,
                    "name": "test-member",
                    "first_name": "first", "last_name": "last", "description": "desc", "organization": "org",
                    "email": "lol@gmail.com", "service_roles": [], "token": "token", "uuid": "u1",
                    "modified_on": "now", "created_on": "now", "created_by": "admin"}"""

        self.project_json = """
            {
                "project": "test-project",
                "description": "nice project"
            }
        """

        project = AmsUserProject(project="test-proj", roles=["consumer"])
        self.default_user = AmsUser(name="test-member", email="lol@gmail.com",
                                    firstname="first", lastname="last",
                                    description="desc", organization="org",
                                    modified_on="now", created_on="now", created_by="admin", token="token", uuid="u1",
                                    projects=[project], service_roles=[])

    add_member_urlmatch = dict(netloc="localhost",
                               path="/v1/projects/test-proj/members/test-member:add",
                               method='POST')

    get_member_urlmatch = dict(netloc="localhost",
                               path="/v1/projects/test-proj/members/test-member",
                               method='GET')

    create_member_urlmatch = dict(netloc="localhost",
                                  path="/v1/projects/test-proj/members/test-member",
                                  method='POST')

    remove_member_urlmatch = dict(netloc="localhost",
                                  path="/v1/projects/test-proj/members/test-member:remove",
                                  method='POST')

    create_project_urlmatch = dict(netloc="localhost",
                                   path="/v1/projects/test-project",
                                   method='POST')

    update_project_urlmatch = dict(netloc="localhost",
                                   path="/v1/projects/test-project",
                                   method='PUT')

    get_project_urlmatch = dict(netloc="localhost",
                                path="/v1/projects/test-project",
                                method='GET')

    delete_project_urlmatch = dict(netloc="localhost",
                                   path="/v1/projects/test-project",
                                   method='DELETE')

    def testAddMember(self):
        @urlmatch(**self.add_member_urlmatch)
        def add_member_mock(url, request):
            self.assertEqual("/v1/projects/test-proj/members/test-member:add", url.path)
            self.assertEqual("POST", request.method)
            self.assertTrue('"roles": ["consumer"]' in request.body)
            return response(200, self.member_json, None, None, 5, request)

        # Execute ams client with mocked response
        with HTTMock(add_member_mock):
            added_member = self.ams.add_project_member(project="test-proj", username="test-member", roles=["consumer"])
            # test case where the global service project is used
            added_member_with_service_project = self.ams.add_project_member(username="test-member", roles=["consumer"])

            added_members = [added_member, added_member_with_service_project]
            for added_member in added_members:
                self.assertEqual(self.default_user.name, added_member.name)
                self.assertEqual(self.default_user.email, added_member.email)
                self.assertEqual(self.default_user.uuid, added_member.uuid)
                self.assertEqual(self.default_user.token, added_member.token)
                self.assertEqual(self.default_user.modified_on, added_member.modified_on)
                self.assertEqual(self.default_user.created_by, added_member.created_by)
                self.assertEqual(self.default_user.created_on, added_member.created_on)
                self.assertEqual(self.default_user.firstname, added_member.firstname)
                self.assertEqual(self.default_user.lastname, added_member.lastname)
                self.assertEqual(self.default_user.description, added_member.description)
                self.assertEqual(self.default_user.organization, added_member.organization)
                self.assertEqual(self.default_user.service_roles, added_member.service_roles)
                self.assertEqual(self.default_user.projects[0].project, added_member.projects[0].project)
                self.assertEqual(self.default_user.projects[0].roles, added_member.projects[0].roles)
                self.assertEqual(self.default_user.projects[0].subscriptions, added_member.projects[0].subscriptions)
                self.assertEqual(self.default_user.projects[0].topics, added_member.projects[0].topics)

    def testCreateMember(self):
        @urlmatch(**self.create_member_urlmatch)
        def create_member_mock(url, request):
            self.assertEqual("/v1/projects/test-proj/members/test-member", url.path)
            self.assertEqual("POST", request.method)
            return response(200, self.member_json, None, None, 5, request)

        # Execute ams client with mocked response
        with HTTMock(create_member_mock):
            created_member = self.ams.create_project_member(project="test-proj",
                                                            username="test-member",
                                                            email="lol@gmail.com")
            # test case where the global service project is used
            created_member_with_service_project = self.ams.create_project_member(username="test-member",
                                                                                 email="lol@gmail.com")
            created_members = [created_member, created_member_with_service_project]

            for added_member in created_members:
                self.assertEqual(self.default_user.name, added_member.name)
                self.assertEqual(self.default_user.email, added_member.email)
                self.assertEqual(self.default_user.uuid, added_member.uuid)
                self.assertEqual(self.default_user.token, added_member.token)
                self.assertEqual(self.default_user.modified_on, added_member.modified_on)
                self.assertEqual(self.default_user.created_by, added_member.created_by)
                self.assertEqual(self.default_user.created_on, added_member.created_on)
                self.assertEqual(self.default_user.firstname, added_member.firstname)
                self.assertEqual(self.default_user.lastname, added_member.lastname)
                self.assertEqual(self.default_user.description, added_member.description)
                self.assertEqual(self.default_user.organization, added_member.organization)
                self.assertEqual(self.default_user.service_roles, added_member.service_roles)
                self.assertEqual(self.default_user.projects[0].project, added_member.projects[0].project)
                self.assertEqual(self.default_user.projects[0].roles, added_member.projects[0].roles)
                self.assertEqual(self.default_user.projects[0].subscriptions, added_member.projects[0].subscriptions)
                self.assertEqual(self.default_user.projects[0].topics, added_member.projects[0].topics)

    def testRemoveMember(self):
        @urlmatch(**self.remove_member_urlmatch)
        def remove_member_mock(url, request):
            self.assertEqual("/v1/projects/test-proj/members/test-member:remove", url.path)
            self.assertEqual("POST", request.method)
            return response(200, self.member_json, None, None, 5, request)

        # Execute ams client with mocked response
        with HTTMock(remove_member_mock):
            self.ams.remove_project_member(project="test-proj", username="test-member")

    def testCreateProject(self):
        @urlmatch(**self.create_project_urlmatch)
        def create_project_mock(url, request):
            self.assertEqual("/v1/projects/test-project", url.path)
            self.assertEqual("POST", request.method)
            self.assertTrue('"description": "nice project"' in request.body)
            return response(200, self.project_json, None, None, 5, request)

        # Execute ams client with mocked response
        with HTTMock(create_project_mock):
            r = self.ams.create_project(name="test-project", description="nice project")
            self.assertEqual("test-project", r["project"])
            self.assertEqual("nice project", r["description"])

    def testUpdateProject(self):
        @urlmatch(**self.update_project_urlmatch)
        def update_project_mock(url, request):
            self.assertEqual("/v1/projects/test-project", url.path)
            self.assertEqual("PUT", request.method)
            self.assertTrue('"description": "nice project"' in request.body)
            self.assertTrue('"name": "updated"' in request.body)
            return response(200, self.project_json, None, None, 5, request)

        # Execute ams client with mocked response
        with HTTMock(update_project_mock):
            r = self.ams.update_project(name="test-project", description="nice project", updated_name="updated")
            self.assertEqual("test-project", r["project"])
            self.assertEqual("nice project", r["description"])

    def testGetProject(self):
        @urlmatch(**self.get_project_urlmatch)
        def get_project_mock(url, request):
            self.assertEqual("/v1/projects/test-project", url.path)
            self.assertEqual("GET", request.method)
            return response(200, self.project_json, None, None, 5, request)

        # Execute ams client with mocked response
        with HTTMock(get_project_mock):
            r = self.ams.get_project(name="test-project")
            self.assertEqual("test-project", r["project"])
            self.assertEqual("nice project", r["description"])

    def testDeleteProject(self):
        @urlmatch(**self.delete_project_urlmatch)
        def delete_project_mock(url, request):
            self.assertEqual("/v1/projects/test-project", url.path)
            self.assertEqual("DELETE", request.method)
            return response(200, None, None, None, 5, request)

        # Execute ams client with mocked response
        with HTTMock(delete_project_mock):
            self.ams.delete_project(name="test-project")


if __name__ == '__main__':
    unittest.main()
