from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404
from gripcontrol import HttpStreamFormat, WebSocketMessageFormat
from django_grip import set_hold_stream, publish
from .models import CallbackRegistration
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
	formats = []
	formats.append(HttpStreamFormat(message + '\n'))
	formats.append(WebSocketMessageFormat(message))
	formats.append(HttpRequestFormat('POST',
		headers={'Content-Type': 'text/plain'},
		body=message))
	publish('messages', formats)
