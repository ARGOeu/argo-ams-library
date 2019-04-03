#!/usr/bin/env python

from argparse import ArgumentParser
from argo_ams_library import ArgoMessagingService, AmsException

def main():
    parser = ArgumentParser(description="Simple AMS example of subscription pull/consume")
    parser.add_argument('--host', type=str, default='messaging-devel.argo.grnet.gr', help='FQDN of AMS Service')
    parser.add_argument('--token', type=str, required=True, help='Given token')
    parser.add_argument('--project', type=str, required=True, help='Project  registered in AMS Service')
    parser.add_argument('--subscription', type=str, required=True, help='Subscription name')
    parser.add_argument('--topic', type=str, required=True, help='Given topic')
    parser.add_argument('--nummsgs', type=int, default=3, help='Number of messages to pull and ack')
    args = parser.parse_args()

    # initialize service with given token and project
    ams = ArgoMessagingService(endpoint=args.host, token=args.token, project=args.project)

    # ensure that subscription is created in first run. messages can be
    # pulled from the subscription only when subscription already exists
    # for given topic prior messages being published to topic
    try:
        if not ams.has_sub(args.subscription):
            ams.create_sub(args.subscription, args.topic)
    except AmsException as e:
        print(e)
        raise SystemExit(1)

    # try to pull number of messages from subscription. method will
    # return (ackIds, AmsMessage) tuples from which ackIds and messages
    # payload will be extracted.
    ackids = list()
    for id, msg in ams.pull_sub(args.subscription, args.nummsgs):
        data = msg.get_data()
        msgid = msg.get_msgid()
        attr = msg.get_attr()
        print('msgid={0}, data={1}, attr={2}'.format(msgid, data, attr))
        ackids.append(id)

    # pass list of extracted ackIds to AMS Service so that
    # it can move the offset for the next subscription pull
    # (basically acknowledging pulled messages)
    if ackids:
        ams.ack_sub(args.subscription, ackids)

main()
