from django.core.management.base import BaseCommand, CommandError
from apps.jobs.tasks.indeed_tasks import scrap_indeed_jobs
from apps.jobs.tasks.google_tasks import scrap_google_jobs
from apps.jobs.tasks.freelancermap_tasks import scrap_freelancermap_jobs
from apps.jobs.tasks.dasauge_tasks import scrap_dasauge_jobs


class Command(BaseCommand):
    help = 'Initializes the first scrapping task'

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument('-p', '--platform', type=str, help='Initialize scrapping f platform specified')
        parser.add_argument('-e', '--email', type=str, help='Email user to login')
        parser.add_argument('-pwd', '--password', type=str, help='Password user to login')
        parser.add_argument('-l', '--location', type=str, help='Scrap paramater', nargs='?', default='')
        parser.add_argument('-t', '--title', type=str, help='Scrap paramater', nargs='?', default='')

    def handle(self, *args, **options):
        platform = options['platform']
        email = options['email']
        password = options['password']
        title = options['title']
        location = options['location']
        if location == None:
            location = ''
        if title == None:
            title = ''
        if platform:
            if platform == 'indeed':
                scrap_indeed_jobs(title, location)
            elif platform == 'google':
                scrap_google_jobs(title, location)
            elif platform == 'freelancermap':
                scrap_freelancermap_jobs(email, password, title)
            elif platform == 'dasauge':
                scrap_dasauge_jobs(title, location)
            else:
                self.stdout.write(f'Platform not recognized by the system')
        else:
            self.stdout.write(f'Define platform to initialize scrapping')
