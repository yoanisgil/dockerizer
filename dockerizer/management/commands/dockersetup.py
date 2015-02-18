from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from optparse import make_option
from django.core import management
from django.core.exceptions import ObjectDoesNotExist

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (make_option('--username', action='store', dest='username', help='User username'), 
    make_option('--password', action='store', dest='password', help='Password'), 
    make_option('--email', action='store', dest='email', help='User email'))
    help = 'Creates a username with the given username/, password and email'

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        email = options['email']
        try:
            user = User.objects.get(username=username)
            user.set_password(password)
            user.email = email
            user.save()
        except ObjectDoesNotExist:
            user = User.objects.create_superuser(username=options['username'], password=options['password'], email=options['email'])
            user.save()
        management.call_command('migrate', verbosity=1, interactive=False)
        management.call_command('collectstatic', verbosity=1, interactive=False)
