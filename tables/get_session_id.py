from django.contrib.sessions.models import Session
from django.contrib.auth.models import User

session_key = 'h6js92gkegzzernbu3u1x6d8gekln24c'

session = Session.objects.get(session_key=session_key)
uid = session.get_decoded().get('_auth_user_id')
user = User.objects.get(pk=uid)

print(user.username, user.get_full_name(), user.email)