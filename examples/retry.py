#!/usr/bin/env python

from argparse import ArgumentParser
from argo_ams_library import ArgoMessagingService, AmsMessage, AmsException

import logging


# setup logger to see the retry messages from ams-library
log = logging.getLogger('argo_ams_library')
log.setLevel(logging.WARNING)
log.addHandler(logging.handlers.SysLogHandler('/dev/log', logging.handlers.SysLogHandler.LOG_USER))
log.addHandler(logging.StreamHandler())


def main():
    parser = ArgumentParser(description="Simple AMS message publish example")
    parser.add_argument('--host', type=str, default='messaging-devel.argo.grnet.gr', help='FQDN of AMS Service')
    parser.add_argument('--token', type=str, required=True, help='Given token')
    parser.add_argument('--project', type=str, required=True, help='Project  registered in AMS Service')
    parser.add_argument('--topic', type=str, required=True, help='Given topic')
    parser.add_argument('--subscription', type=str, required=True, help='Subscription name')
    parser.add_argument('--nummsgs', type=int, default=3, help='Number of messages to pull and ack')
    args = parser.parse_args()

    ams = ArgoMessagingService(endpoint=args.host, token=args.token, project=args.project)

    # static sleep between retry attempts
    msg = AmsMessage(data='foo1', attributes={'bar1': 'baz1'}).dict()
    try:
        ret = ams.publish(args.topic, msg, retry=3, retrysleep=5, timeout=5)
        print(ret)
    except AmsException as e:
        print(e)

    # iptables -A OUTPUT -d messaging-devel.argo.grnet.gr -j DROP

    ackids = list()
    for id, msg in ams.pull_sub(args.subscription, args.nummsgs, retry=3,
                                retrysleep=5, timeout=5):
        data = msg.get_data()
        msgid = msg.get_msgid()
        attr = msg.get_attr()
        print('msgid={0}, data={1}, attr={2}'.format(msgid, data, attr))
        ackids.append(id)

    if ackids:
        ams.ack_sub(args.subscription, ackids, retry=3, retrysleep=5,
                    timeout=5)

    # backoff with each next retry attempt exponentially longer
    msg = AmsMessage(data='foo2', attributes={'bar2': 'baz2'}).dict()
    try:
        ret = ams.publish(args.topic, msg, retry=3, retrybackoff=5, timeout=5)
        print(ret)
    except AmsException as e:
        print(e)

    # iptables -A OUTPUT -d messaging-devel.argo.grnet.gr -j DROP

    ackids = list()
    for id, msg in ams.pull_sub(args.subscription, args.nummsgs,
                                retrybackoff=3, retrysleep=5, timeout=5):
        data = msg.get_data()
        msgid = msg.get_msgid()
        attr = msg.get_attr()
        print('msgid={0}, data={1}, attr={2}'.format(msgid, data, attr))
        ackids.append(id)

    if ackids:
        ams.ack_sub(args.subscription, ackids)

    # static sleep between retry attempts. this example uses consume context
    # method that pull and acks msgs in one call.
    msg = AmsMessage(data='foo3', attributes={'bar3': 'baz3'}).dict()
    try:
        ret = ams.publish(args.topic, msg, retry=3, retrysleep=5, timeout=5)
        print(ret)
    except AmsException as e:
        print(e)

    try:
        msgs = ams.pullack_sub(args.subscription, args.nummsgs, retry=3,
                               retrysleep=5, timeout=5)
        for msg in msgs:
            data = msg.get_data()
            msgid = msg.get_msgid()
            attr = msg.get_attr()
            print('msgid={0}, data={1}, attr={2}'.format(msgid, data, attr))

    except AmsException as e:
        print(e)

main()
