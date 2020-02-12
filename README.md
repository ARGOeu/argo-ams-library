# argo-ams-library

<img src="https://jenkins.argo.grnet.gr/static/3c75a153/images/headshot.png" alt="Jenkins" width="25"/> [![Build Status](https://jenkins.argo.grnet.gr/job/argo-ams-library_devel/badge/icon)](https://jenkins.argo.grnet.gr/job/argo-ams-library_devel)

A simple python library for interacting with the ARGO Messaging Service. 

The Messaging Services is implemented as a Publish/Subscribe Service. Instead of focusing on a single Messaging API specification for handling the logic of publishing/subscribing to the broker network the API focuses on creating nodes of Publishers and Subscribers as a Service.

In the Publish/Subscribe paradigm, Publishers are users/systems that can send messages to named-channels called Topics. Subscribers are users/systems that create Subscriptions to specific topics and receive messages.

You may find more information about [the ARGO Messaging Service documentation](http://argoeu.github.io/messaging/v1/)

## Library installation 

Library is tested and should work with Python versions 2.6, 2.7, 3.4 and 3.6 running on CentOS 6 and CentOS 7 releases.

RPM packages are prepared for both CentOS releases and you may find it and download it from ARGO Repository. PyPI packages are prepared as well.

RPM production packages:

http://rpm-repo.argo.grnet.gr/ARGO/prod/centos6/
http://rpm-repo.argo.grnet.gr/ARGO/prod/centos7/

RPM devel packages:

http://rpm-repo.argo.grnet.gr/ARGO/devel/centos6/
http://rpm-repo.argo.grnet.gr/ARGO/devel/centos7/
 
PyPI package:

https://pypi.org/project/argo-ams-library/


## Authentication
The AMS library uses a valid AMS token to execute requests against the AMS cluster.
This token can be provided with 2 ways:

- Obtain a valid ams token and then use it when initializing the ams object.
```python
from argo_ams_library import ArgoMessagingService
ams = ArgoMessagingService(endpoint="ams_endpoint", project="ams_project", token="your_ams_token")
```

- Use a valid certificate
```python
from argo_ams_library import ArgoMessagingService
ams = ArgoMessagingService(endpoint="ams_endpoint", project="ams_project", cert="/path/to/cert", key="/path/to/cert/key")
```
The library will use the provided certificate to access the corresponding ams token through [the ARGO Authentication Service](https://github.com/ARGOeu/argo-api-authn) and then set the ams object's token field with the retrieved token.

## Examples

In the folder `examples`, you may find examples of using the library:

- for publishing messages (`examples/publish.py`)
- for consuming messages in pull mode (`examples/consume-pull.py`)
- retry feature for publish/consume methods (`examples/retry.py`)

### Publish messages

This example explains how to publish messages in a topic with the use of the library. Topics are resources that can hold messages. Publishers (users/systems) can create topics on demand and name them (Usually with names that make sense and express the class of messages delivered in the topic). A topic name must be scoped to a project.
 
You may find more information about [Topics in the ARGO Messaging Service documentation](http://argoeu.github.io/messaging/v1/api_topics/)
 
```
publish.py  --host=[the FQDN of AMS Service] 
--token=[the user token] 
--project=[the name of your project registered in AMS Service] 
--topic=[the topic to publish your messages]
```
 
### Consume messages in pull mode 
 
This example explains how to consume messages from a predefined subscription with the use of the library. A subscription is a named resource representing the stream of messages from a single, specific topic, to be delivered to the subscribing application. A subscription name  must be scoped to a project. In pull delivery, your subscriber application initiates requests to the Pub/Sub server to retrieve messages. When you create a subscription, the system establishes a sync point. That is, your subscriber is guaranteed to receive any message published after this point. Messages published before the sync point may not be delivered.
 
You may find more information about [Subscriptions in the ARGO Messaging Service documentation](http://argoeu.github.io/messaging/v1/api_subs/)
 
```
consume-pull.py  --host=[the FQDN of AMS Service] 
--token=[the user token] 
--project=[the name of your project registered in AMS Service] 
--topic=[the topic from where the messages are delivered ] 
--subscription=[the subscription name to pull the messages]  
--nummsgs=[the num of messages to consume]

```

### Retry 

Library has self-implemented HTTP request retry ability to seamlesssly interact with the ARGO Messaging service. Specifically, requests will be retried in case of:
* timeouts from AMS (HTTP `408`) or load balancer (HTTP `408` and `504`)
* load balancer HTTP `502`, `503`
* connection related problems in the lower network layers

It has two modes: static sleep and backoff. Examples are given in the in `examples/retry.py`.
