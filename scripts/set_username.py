from django.contrib.auth.models import User

def run():
  u = User.objects.get(username='modc08')
  print u
  u.first_name='modc'
  u.last_name='admin'
  u.save()

