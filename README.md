# Scrapper

## Getting started
These instructions will get you a copy of the project up and running in your local machine for development and testing purposes.

## Prerequisites
- [Git](https://git-scm.com/download/)
- [Python 3.6 and above](https://www.python.org/downloads/)
- [PostgreSQL](https://www.postgresql.org/)


## Installing
### Setting up the database
- Start your database server and create your database

### Setting up and Activating a Virtual Environment
- Navigate to the project directory
- Create a virtual environment `python3 -m venv name_of_your_virtual_environment`
- Create a .env file and put these key=values in it:
```
source venv/bin/activate
export SECRET_KEY=''
export GOOGLE_CHROME_BIN=/app/.apt/usr/bin/google-chrome
export CHROMEDRIVER_PATH=/app/.chromedriver/bin/chromedriver
export DEBUG=True
export DB_NAME=''
export DB_USER=''
export DB_PASSWORD=''
export DB_HOST=''
export MODE='dev'
export ALLOWED_HOSTS=''
export DISABLE_COLLECTSTATIC=1
# celery
export CELERY_BROKER_URL=""
export CELERY_RESULT_BACKEND=""
export DJANGO_SETTINGS_MODULE='indeed.settings'

```
- Load the environment variable `source .env`
- Install dependencies to your virtual environment `pip install -r requirements.txt`
- Migrate changes to the newly created database `python manage.py migrate`

## Running scrappers
- Install redis on your machine
- Run the following commands in separate tabs to scrap from different platforms

- Run `redis-server`
- Activate environment `source .env` and run `make celery`
- Activate environment `source .env` and run `make serve`
### Scrap jobs
- To scrap from indeed platform run `make jobscrap platform=indeed`
- To scrap from dasauge platform run `make jobscrap platform=dasauge`
- To scrap from google platform run `make jobscrap platform=google`
- To scrap from freelancermap platform run `make jobscrap platform=freelancermap email=<your_freelancer_login_email> pass=<your_freelancer_login_password>`
- To scrap with job title and job location filters add `location=<job_location>` or/and `title=<job_title>`  
- N/B To use filter a location or title which is a string e.g `title=software engineering`
  use `+` to join the words i.e. use `title=software+engineering`
## Starting the server
- Ensure you are in the project directory on the same level with `manage.py` and the virtual environment is activated
- Run the server `python manage.py runserver` or `make serve` 
