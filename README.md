Test API
========

This a minimal backend to showcase realtime API endpoints with Fanout. Three mechanisms are supported:

* HTTP streaming
* WebSockets
* Webhooks

The service has the following HTTP endpoints:

* GET `/messages/`: Never ending HTTP response that streams messages as lines. The first line will be a welcome message.
* POST `/messages/subscriptions/`: Subscribe a callback URL to new messages. Expects a form-encoded body with a `url` parameter set to the callback URL. The response will contain a registration ID that can be used for deletion.
* DELETE `/messages/subscriptions/{id}/`: Unsubscribe a callback URL based on the registration ID.
* POST `/send/`: Broadcast a text message to all listeners. Expects a form-encoded body with a `message` parameter set to a string to send.

The service also has a WebSocket endpoint:

* `/messages/`: Connect to this endpoint via WebSocket to listen for new messages. The first message received will be a welcome message. If you send a message to the server, it will be broadcasted to all listeners (same as the `/send` HTTP endpoint).

There is an instance of the API running at `86f32743.fanoutcdn.com` to easily try it out.
