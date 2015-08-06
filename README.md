Test API
========

This a minimal backend to demonstrate how to implement realtime API endpoints with Fanout. The demo supports three delivery mechanisms:

* HTTP streaming
* WebSockets
* Webhooks

The following HTTP endpoints are available:

* GET `/messages/`: Never ending HTTP response that streams messages as lines. The first line will be a welcome message.
* POST `/messages/subscriptions/`: Subscribe a callback URL to new messages. Expects a form-encoded body with a `url` parameter set to the callback URL. The response will contain a registration ID that can be used for deletion.
* DELETE `/messages/subscriptions/{id}/`: Unsubscribe a callback URL based on the registration ID.
* POST `/send/`: Broadcast a text message to all listeners. Expects a form-encoded body with a `message` parameter set to a string to send.

There is also a WebSocket endpoint:

* `/messages/`: Connect to this endpoint via WebSocket to listen for new messages. The first message received will be a welcome message. If you send a message to the server, it will be broadcasted to all listeners (same as the `/send/` HTTP endpoint).

There is an instance of the API running at `86f32743.fanoutcdn.com` to easily try it out.

Examples
--------

Open HTTP stream:
```
curl -i http://86f32743.fanoutcdn.com/messages/

HTTP/1.1 200 OK
Server: gunicorn/19.3.0
Date: Thu, 06 Aug 2015 23:50:11 GMT
Content-Type: text/plain
Transfer-Encoding: chunked
Connection: Transfer-Encoding

Welcome to the Test API
```

Open WebSocket connection:
```
wscat -c ws://86f32743.fanoutcdn.com/messages/

connected (press CTRL+C to quit)
  < Welcome to the Test API
>
```

Subscribe a callback URL:
```
curl -i -d 'url=http://example.com/path' http://86f32743.fanoutcdn.com/messages/subscriptions/

HTTP/1.1 201 CREATED
Server: gunicorn/19.3.0
Date: Thu, 06 Aug 2015 23:51:05 GMT
Content-Type: text/plain
Content-Length: 27

Created registration. id=1
```

Push a message to all listeners:
```
curl -i -d 'message=hello everyone' http://86f32743.fanoutcdn.com/send/
```

Delete callback URL:
```
curl -i -X DELETE http://86f32743.fanoutcdn.com/messages/subscriptions/1/

HTTP/1.1 200 OK
Server: gunicorn/19.3.0
Date: Thu, 06 Aug 2015 23:51:54 GMT
Content-Type: text/plain
Content-Length: 8

Deleted
```
