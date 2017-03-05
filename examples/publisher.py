#!/usr/bin/env python

from argparse import ArgumentParser
from argo_ams_library import ArgoMessagingService, AmsMessage, AmsException

def main():
    parser = ArgumentParser(description="Simple AMS message publish example")
    parser.add_argument('--host', type=str, default='messaging-devel.argo.grnet.gr', help='FQDN of AMS Service')
    parser.add_argument('--token', type=str, required=True, help='Given token')
    parser.add_argument('--project', type=str, required=True, help='Project  registered in AMS Service')
    parser.add_argument('--topic', type=str, required=True, help='Given topic')
    args = parser.parse_args()

    # initialize service with given token and project
    ams = ArgoMessagingService(endpoint=args.host, token=args.token, project=args.project)

    # ensure that topic is created in first run
    try:
        ams.get_topic(args.topic)
    except AmsException as e:
        ams.create_topic(args.topic)

    # publish one message to given topic. message is constructed with
    # help of AmsMessage which accepts data and attributes keys.
    # data is Base64 encoded, attributes is dictionary of arbitrary
    # key/value pairs
    msg = AmsMessage(data='foo1', attributes={'bar1': 'baz1'}).dict()
    try:
        ret = ams.publish(args.topic, msg)
        print ret
    except AmsException as e:
        print e

    # publish a list of two messages to given topic. publish() method
    # accepts either one messages or list of messages
    msglist = [AmsMessage(data='foo2', attributes={'bar2': 'baz2'}).dict(),
               AmsMessage(data='foo3', attributes={'bar3': 'baz3'}).dict()]
    try:
        ret = ams.publish(args.topic, msglist)
        print ret
    except AmsException as e:
        print e

main()
