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
	if request.wscontext:
		ws = request.wscontext
		if ws.is_opening():
			ws.accept()
			ws.subscribe('messages')
			ws.send('Welcome to the Test API')
		while ws.can_recv():
			m = ws.recv()
			if m is None:
				ws.close()
				break
			publish_message(m)
		return HttpResponse()

	if request.method == 'GET':
		set_hold_stream(request, 'messages')
		return HttpResponse('Welcome to the Test API\n',
			content_type='text/plain')
	else:
		return HttpResponseNotAllowed(['GET'])

def messages_last(request):
	if request.method == 'GET':
		message = LastMessage.get_only().text
		etag = '"%s"' % hashlib.md5(message).hexdigest()

		inm = request.META.get('HTTP_IF_NONE_MATCH')
		wait = (request.GET.get('wait') == 'true')

		if inm == etag:
			resp = HttpResponseNotModified()
			if wait:
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
		r = CallbackRegistration(url=url)
		r.save()
		hrq_sub_add('messages', r.url)
		return HttpResponse('Created registration. id=%d\n' % r.id,
			status=201, content_type='text/plain')
	else:
		return HttpResponseNotAllowed(['POST'])

def messages_subscriptions_item(request, reg_id):
	if request.method == 'DELETE':
		r = get_object_or_404(CallbackRegistration, pk=reg_id)
		hrq_sub_remove('messages', r.url)
		r.delete()
		return HttpResponse('Deleted\n', content_type='text/plain')
	else:
		return HttpResponseNotAllowed(['DELETE'])

def send(request):
	if request.method == 'POST':
		message = request.POST['message']
		publish_message(message)
		return HttpResponse('Ok\n', content_type='text/plain')
	else:
		return HttpResponseNotAllowed(['POST'])

def publish_message(message):
	m = LastMessage.get_only()
	m.text = message
	m.save()

	etag = '"%s"' % hashlib.md5(message).hexdigest()
	headers = {'Content-Type': 'text/plain', 'ETag': etag}

	formats = []
	formats.append(HttpResponseFormat(headers=headers, body=message + '\n'))
	formats.append(HttpStreamFormat(message + '\n'))
	formats.append(WebSocketMessageFormat(message))
	formats.append(HttpRequestFormat('POST', headers=headers,
		body=message + '\n'))
	publish('messages', formats)
