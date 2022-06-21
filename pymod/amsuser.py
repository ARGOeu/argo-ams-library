import json


class AmsUserProject(object):

    def __init__(self, project="", roles=None, topics=None, subscriptions=None):
        """
        Initialises a new User-Project object.

        NOTE:
        When using a new AmsUserProject object during the creation of a new user in ams,
        you can only affect the project and roles fields.You cannot add a user to a topic
        or subscription through the create functionality.The topics and subscriptions fields
        are present only for view purposes.

        :param project: (str) name of the project
        :param roles: (str[]) roles the user has under the given project
        :param topics: (str[]) topics that the user belongs to under the given project
        :param subscriptions: (str[]) subscriptions that the user belongs to under the given project
        """
        if subscriptions is None or not isinstance(subscriptions, list):
            subscriptions = []
        if topics is None or not isinstance(topics, list):
            topics = []
        if roles is None or not isinstance(roles, list):
            roles = []
        else:
            for r in roles:
                if not isinstance(r, str):
                    raise ValueError("role has to be of type str")
        self.project = project
        self.roles = roles
        self.topics = topics
        self.subscriptions = subscriptions

    def load_from_dict(self, project_dict):
        """
        Accepts a dictionary that contains project data in order to fill the instance's fields
        :param (dict) project_dict: dict that contains project data
        :return: (AmsUserProject) the ams user project object filled with any data provided to its respective fields
        """
        if "project" in project_dict:
            self.project = project_dict["project"]

        if "roles" in project_dict:
            self.roles = project_dict["roles"]
        else:
            self.roles = []

        if "topics" in project_dict:
            self.topics = project_dict["topics"]
        else:
            self.topics = []

        if "subscriptions" in project_dict:
            self.subscriptions = project_dict["subscriptions"]
        else:
            self.subscriptions = []

        return self


class AmsUser(object):

    def __init__(self, uuid="", name="", projects=None, firstname="", lastname="", organization="", description="",
                 token="", email="", service_roles=None, created_on="", created_by="", modified_on=""):
        """

        Initialise a new user object.

        NOTE:
        When using a new AmsUser object during the create functionality, the fields that will affect
        the user creation are name, projects, firstname, lastname, organisation, description, email and
        service_roles.You cannot control the values for the rest of the fields through the create functionality.
        The rest of the fields are present for view purposes.

        :param uuid: (str) the uuid of the user
        :param name: (str) the username
        :param projects: (AmsUserProject[]) list of projects the user belongs to in AMS
        :param firstname: (str) firstname of the user
        :param lastname:  (str) lastname of the user
        :param organization: (str) organisation of the user
        :param description: (str) description of the user
        :param token: (str) user access token for the AMS
        :param email: (str) user email
        :param service_roles: (str[]) possible service roles the user might have in AMS
        :param created_on: (str) user creation date
        :param created_by: (str) user creator
        :param modified_on: (str) timestamp of the latest modification
        """

        if service_roles is None or not isinstance(service_roles, list):
            service_roles = []
        else:
            for s in service_roles:
                if not isinstance(s, str):
                    raise ValueError("service role has to be of type str")

        if projects is None or not isinstance(projects, list):
            projects = []
        else:
            for p in projects:
                if not isinstance(p, AmsUserProject):
                    raise ValueError("project has to be of type AmsUserProject")

        self.uuid = uuid
        self.name = name
        self.projects = projects
        self.firstname = firstname
        self.lastname = lastname
        self.organization = organization
        self.description = description
        self.token = token
        self.email = email
        self.service_roles = service_roles
        self.created_on = created_on
        self.created_by = created_by
        self.modified_on = modified_on

    def to_json(self):
        """
        Utility function that helps convert the AmsUser object to its json string representation
        using json.dumps().
        :return: (str) the json string representation of the object
        """
        user_dict = {}
        if len(self.projects) > 0:
            projects_body = []
            for p in self.projects:
                projects_body.append(
                    {
                        "project": p.project,
                        "roles": p.roles,
                        "topics": p.topics,
                        "subscriptions": p.subscriptions
                    }
                )
            user_dict["projects"] = projects_body

        if self.firstname != "":
            user_dict["first_name"] = self.firstname

        if self.lastname != "":
            user_dict["last_name"] = self.lastname

        if self.description != "":
            user_dict["description"] = self.description

        if self.organization != "":
            user_dict["organization"] = self.organization

        if self.email != "":
            user_dict["email"] = self.email

        if len(self.service_roles) > 0:
            user_dict["service_roles"] = self.service_roles

        return json.dumps(user_dict)

    def load_from_dict(self, user_dict):
        """
        Accepts a dictionary that contains user data in order to fill the instance's fields
        :param (dict) user_dict: dict that contains user data
        :return: (AmsUser) the user object filled with any data provided to its respective fields
        """

        if "uuid" in user_dict:
            self.uuid = user_dict["uuid"]

        if "projects" in user_dict:
            user_projects = []
            for p in user_dict["projects"]:
                user_projects.append(AmsUserProject().load_from_dict(p))
            self.projects = user_projects

        if "name" in user_dict:
            self.name = user_dict["name"]

        if "token" in user_dict:
            self.token = user_dict["token"]

        if "email" in user_dict:
            self.email = user_dict["email"]

        if "service_roles" in user_dict:
            self.service_roles = user_dict["service_roles"]

        if "created_on" in user_dict:
            self.created_on = user_dict["created_on"]

        if "modified_on" in user_dict:
            self.modified_on = user_dict["modified_on"]

        if "created_by" in user_dict:
            self.created_by = user_dict["created_by"]

        if "description" in user_dict:
            self.description = user_dict["description"]

        if "first_name" in user_dict:
            self.firstname = user_dict["first_name"]

        if "last_name" in user_dict:
            self.lastname = user_dict["last_name"]

        if "organization" in user_dict:
            self.organization = user_dict["organization"]

        return self
