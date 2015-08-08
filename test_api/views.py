import hashlib
from django.http import HttpResponse, HttpResponseNotModified, \
    HttpResponseNotAllowed
from django.shortcuts import get_object_or_404
from gripcontrol import Channel, HttpResponseFormat, HttpStreamFormat, \
    WebSocketMessageFormat
from django_grip import set_hold_longpoll, set_hold_stream, publish
from .models import LastMessage, CallbackRegistration
from .util import HttpRequestFormat, hrq_sub_add, hrq_sub_remove

def messages(request):
    # The wscontext property is set by the django-grip middleware if the
    #   request is related to a WebSocket session.
    if request.wscontext:
        ws = request.wscontext

        if ws.is_opening():
            # Accept all new connections, subscribe them to a channel, and
            #   send a welcome message.
            ws.accept()
            ws.subscribe('messages')
            ws.send('Welcome to the Test API')

        # Handle any messages in the request.
        while ws.can_recv():
            m = ws.recv()

            if m is None:
                # The recv() function returns None if the WebSocket
                #   connection was closed. In that case, we'll acknowledge
                #   by closing as well.
                ws.close()
                break

            # Relay incoming message to listeners.
            publish_message(m)

        # Since the request was related to a WebSocket session, the
        #   django-grip middleware will override whatever we return here.
        #   However, we still have to return a valid object in order to
        #   satisfy Django.
        return HttpResponse()

    # If we get here, then the request was not related to a WebSocket
    #   session and we should treat it like a regular request.

    if request.method == 'GET':
        # Set the request to hold open as a stream, subscribed to a
        #   channel.
        set_hold_stream(request, 'messages')

        # Return the initial response for the stream. The django-grip
        #   middleware will ensure that additional instructions are
        #   included in the response, so that the proxy knows to hold
        #   the connection open.
        return HttpResponse('Welcome to the Test API\n',
            content_type='text/plain')
    else:
        return HttpResponseNotAllowed(['GET'])

def messages_last(request):
    if request.method == 'GET':
        # Get the most recent sent message from the database (empty string by
        #   default), and generate a simple ETag.
        message = LastMessage.get_only().text
        etag = '"%s"' % hashlib.md5(message).hexdigest()

        inm = request.META.get('HTTP_IF_NONE_MATCH')
        wait = (request.GET.get('wait') == 'true')

        if inm == etag:
            # If a matching If-None-Match header was supplied, then return
            #   status 304.
            resp = HttpResponseNotModified()

            if wait:
                # Set the request to hold open as a long-poll, subscribed to
                #   a channel.
                channel = Channel('messages', prev_id=etag)
                set_hold_longpoll(request, channel)
        else:
            resp = HttpResponse(message + '\n',
                content_type='text/plain')

        resp['ETag'] = etag
        return resp
    else:
        return HttpResponseNotAllowed(['GET'])

def messages_subscriptions(request):
    if request.method == 'POST':
        url = request.POST['url']

        # Save the URL to local database so we can refer to it by ID.
        r = CallbackRegistration(url=url)
        r.save()

        # Subscribe the URL to the channel on the Fanout service.
        hrq_sub_add('messages', r.url)

        return HttpResponse('Created registration. id=%d\n' % r.id,
            status=201, content_type='text/plain')
    else:
        return HttpResponseNotAllowed(['POST'])

def messages_subscriptions_item(request, reg_id):
    if request.method == 'DELETE':
        r = get_object_or_404(CallbackRegistration, pk=reg_id)

        # Unsubscribe the URL from the channel on the Fanout service.
        hrq_sub_remove('messages', r.url)

        # Delete the URL from the local database.
        r.delete()

        return HttpResponse('Deleted\n', content_type='text/plain')
    else:
        return HttpResponseNotAllowed(['DELETE'])

def send(request):
    if request.method == 'POST':
        message = request.POST['message']

        # Relay message to listeners.
        publish_message(message)

        return HttpResponse('Ok\n', content_type='text/plain')
    else:
        return HttpResponseNotAllowed(['POST'])

def publish_message(message):
    # Save the current message to the database, overwriting the previous.
    m = LastMessage.get_only()
    m.text = message
    m.save()

    # Generate a simple ETag, using the same algorithm as the GET handler.
    etag = '"%s"' % hashlib.md5(message).hexdigest()

    # Also prepare headers for the HTTP request and HTTP response delivery
    #   mechanisms.
    headers = {'Content-Type': 'text/plain', 'ETag': etag}

    formats = []

    # Prepare the message in four different formats.
    formats.append(HttpResponseFormat(headers=headers, body=message + '\n'))
    formats.append(HttpStreamFormat(message + '\n'))
    formats.append(WebSocketMessageFormat(message))
    formats.append(HttpRequestFormat('POST', headers=headers,
        body=message + '\n'))

    # Send to the proxy and/or Fanout.
    publish('messages', formats)
