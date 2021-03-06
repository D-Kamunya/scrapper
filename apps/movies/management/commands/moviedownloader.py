from django.core.management.base import BaseCommand, CommandError
from threading import Thread
from apps.movies.tasks.tvshows4mobile_tasks  import download_tvshows4mobile_movie



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

        # Number of browsers to run
        nbr_threads = 6

        threads = []
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
                episodes =( input
                ('Enter season episode to download in two digits i.e. 01,02,11,... \n'))
                episodes = episodes.split(',')
                for i, ep in enumerate(episodes):
                    if len(ep)==2 and ep.isdecimal():
                        x = Thread(target=download_tvshows4mobile_movie, args=(site, title, season, ep))
                        x.start()
                        threads.append(x)
                        if (i+1) % nbr_threads == 0:
                            for th in threads:
                                th.join()
                            threads = []
                    else:
                        print(f'Wrong episode format {ep}.')
                for th in threads:
                    th.join()
           