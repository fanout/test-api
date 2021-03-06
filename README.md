Test API
========

This is a minimal Django backend to demonstrate how to implement realtime API endpoints with Pushpin/Fanout. The demo supports four delivery mechanisms:

* HTTP streaming
* HTTP long-polling
* WebSockets
* Webhooks

The following HTTP endpoints are available:

* GET `/messages/`: Never ending HTTP response that streams messages as lines. The first line will be a welcome message.
* GET `/messages/last/`: Fetch the most recent message value. Pass the `If-None-Match` header to check for changes. Add a `?wait=true` query parameter to have the request long-poll if the value hasn't changed yet.
* POST `/messages/subscriptions/`: Subscribe a callback URL to new messages. Expects a form-encoded body with a `url` parameter set to the callback URL. The response will contain a registration ID that can be used for deletion.
* DELETE `/messages/subscriptions/{id}/`: Unsubscribe a callback URL based on the registration ID.
* POST `/send/`: Broadcast a text message to all listeners. Expects a form-encoded body with a `message` parameter set to a string to send.

There is also a WebSocket endpoint:

* `/messages/`: Connect to this endpoint via WebSocket to listen for new messages. The first message received will be a welcome message. If you send a message to the server, it will be broadcasted to all listeners (same as the `/send/` HTTP endpoint).

Setup
-----

There is an instance of the API running at `86f32743.fanoutcdn.com` to easily try it out. The Django app is running on Heroku, which is then fronted by the Fanout cloud service.

If you want to set it up yourself, be sure to set the following environment variables:

* `GRIP_URL`: A URL to describe the GRIP configuration.
* `FANOUT_REALM` (optional, needed for Webhooks).
* `FANOUT_KEY` (optional, needed for Webhooks).

The Fanout cloud is needed for Webhooks. For HTTP streaming and WebSockets, you can use either the Fanout cloud or your own instance of Pushpin.

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

Open HTTP long-poll:
```
curl -i -H 'If-None-Match: "etag"' \
    http://86f32743.fanoutcdn.com/messages/last/?wait=true
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
curl -i -d 'url=http://example.com/path' \
    http://86f32743.fanoutcdn.com/messages/subscriptions/

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
