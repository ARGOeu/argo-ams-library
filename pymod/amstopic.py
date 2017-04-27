class AmsTopic(object):
    """Abstraction of AMS Topic

       Topic represents named bucket on AMS service that can hold messages.
       Supported methods are wrappers around the same methods defined in client
       class with preconfigured topic name.
    """

    def _build_name(self, fullname):
        return fullname.split('/projects/{0}/topics/'.format(self.init.project))[1]

    def __init__(self, fullname, init):
        self.init = init
        self.fullname = fullname
        self.name = self._build_name(self.fullname)

    def delete(self):
        """Delete subscription

           Return:
               True: succesfull topic deletion
        """

        return self.init.delete_topic(self.name)

    def subscription(self, sub, ackdeadline=10, **reqkwargs):
        """Create a subscription for the topic

           Args:
               sub (str): Name of the subscription
           Kwargs:
               ackdeadline (int): Time window in which the AMS service expects
                                  acknowledgement received for pulled messages
           Return:
               object (AmsSubscription)

        """
        return self.init.create_sub(sub, self.name, ackdeadline=ackdeadline, retobj=True, **reqkwargs)

    def iter_subs(self):
        """Generator method that can be used to iterate over subscription
           associated with the topic
        """

        for s in self.init.iter_subs(topic=self.name):
            yield s

    def publish(self, msg, **reqkwargs):
        """Publish message to topic

           Args:
               msg (list, dict): One or list of dictionaries representing AMS
                                 Message
           Kwargs:
               reqkwargs: Keyword argument that will be passed to underlying
                          python-requests library call.

           Returns:
               dict: Dictionary with messageIds of published messages
        """

        return self.init.publish(self.name, msg, **reqkwargs)
