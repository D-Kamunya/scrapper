from django.core.management.base import BaseCommand, CommandError
from apps.movies.tasks.tvshows4mobile_tasks  import download_movie

class Command(BaseCommand):
    help = 'Download movies'

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument('-s', '--site', type=str, help='Specify site to download movie', nargs='?', default='')
        parser.add_argument('-t', '--title', type=str, help='Specify movie title', nargs='?', default='')
        parser.add_argument('-se', '--season', type=str, help='Specify movie season', nargs='?', default='')
        parser.add_argument('-ep', '--episode', type=str, help='Specify season episode', nargs='?', default='')

    def handle(self, *args, **options):
        site = options['site']
        title = options['title']
        season = options['season']
        episode = options['episode']
        if site == None:
            while True:
                site =( input
                ('Choose site to download movie \n 1.Tvshows4mobile.com \n 2.Telegram \n'))
                if site=='1' or site =='2':
                    if site=='1':
                        site='https://tvshows4mobile.com/search/list_all_tv_series'
                    break
                else:
                    print("Invalid choice")
                    
        if title == None:
            while True:
                title =input('Enter movie title \n')
                if title=='':
                    print("Enter a movie title")
                else:
                    break

        if season == None:
            while True:
                season =( input
                ('Enter movie season to download in two digits i.e. 01,02,11,... \n'))
                if len(season)<2:
                    print("Wrong season format.Write in tens")
                else:
                    if season.isdecimal():
                        break
                    else:
                        print('Wrong season format.Should only contain numbers')
        
        if episode == None:
            while True:
                episode =( input
                ('Enter season episode to download in two digits i.e. 01,02,11,... \n'))
                if len(season)<2:
                    print("Wrong episode format.Write in tens")
                else:
                    if episode.isdecimal():
                        break
                    else:
                        print('Wrong episode format.Should only contain numbers')

        download_movie(site, title, season, episode)