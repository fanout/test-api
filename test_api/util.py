from datetime import datetime
from base64 import b64encode, b64decode
from urllib import quote
import time
import calendar
import requests
import jwt
from django.conf import settings
from pubcontrol import Format

def _is_unicode_instance(instance):
	try:
		if isinstance(instance, unicode):
			return True
	except NameError:
		if isinstance(instance, str):
			return True
	return False

def _is_basestring_instance(instance):
	try:
		if isinstance(instance, basestring):
			return True
	except NameError:
		if isinstance(instance, str):
			return True
	return False

def _bin_or_text(s):
	if _is_unicode_instance(s):
		return (True, s)
	try:
		return (True, s.decode('utf-8'))
	except UnicodeDecodeError:
		return (False, s)

def _timestamp_utcnow():
	return calendar.timegm(datetime.utcnow().utctimetuple())

def _auth_header():
	iss = settings.FANOUT_REALM
	key = b64decode(settings.FANOUT_KEY)
	claim = {'iss': iss, 'exp': int(time.time()) + 3600}
	return 'Bearer ' + jwt.encode(claim, key)

class HttpRequestFormat(Format):
	def __init__(self, method, headers=None, body=None):
		self.method = method
		self.headers = headers
		self.body = body

	def name(self):
		return 'http-request'

	def export(self):
		out = dict()
		out['method'] = self.method
		if self.headers:
			out['headers'] = self.headers
		if self.body:
			is_text, val = _bin_or_text(self.body)
			if is_text:
				out['body'] = val
			else:
				out['body-bin'] = b64encode(val)
		return out

if getattr(settings, 'GRIP_PREFIX'):
	channel_prefix = settings.GRIP_PREFIX
else:
	channel_prefix = ''

def hrq_sub_add(channel, url):
	resp = requests.post('%s/channel/%s/hrq-subscriptions/'
		% (settings.FANOUT_BASE_URI, channel_prefix + channel),
		headers={'Authorization': _auth_header()},
		data={'url': url},
		verify=False)
	if resp.status_code != 200:
		raise ValueError('failed to subscribe url')

def hrq_sub_remove(channel, url):
	resp = requests.delete('%s/channel/%s/hrq-subscription/%s/'
		% (settings.FANOUT_BASE_URI, channel_prefix + channel,
		quote(url, '')),
		headers={'Authorization': _auth_header()},
		verify=False)
	if resp.status_code not in (200, 404):
		raise ValueError('failed to unsubscribe url')
