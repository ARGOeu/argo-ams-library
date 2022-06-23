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
            added_member_with_service_project = self.ams.add_project_member( username="test-member", roles=["consumer"])

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

    def testGetMember(self):
        @urlmatch(**self.get_member_urlmatch)
        def get_member_mock(url, request):
            self.assertEqual("/v1/projects/test-proj/members/test-member", url.path)
            self.assertEqual("GET", request.method)
            return response(200, self.member_json, None, None, 5, request)

        # Execute ams client with mocked response
        with HTTMock(get_member_mock):
            added_member = self.ams.get_project_member(project="test-proj", username="test-member")
            # test case where the global service project is used
            added_member_with_service_project = self.ams.get_project_member(username="test-member")
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