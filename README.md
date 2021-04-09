# JOBS SCRAPPING AND MOVIE DOWNLOAD AUTOMATION
####  A python application to scrap jobs from different websites and also automate movie downloads

## Author
[Dennis Kamunya](https://github.com/D-Kamunya)

## Features
Here are the features in summary:
* Scrap jobs  from various websites(indeed.com,freelancermap.de,dasauge,google jobs).
* Provide acces to scrapped jobs via an API
* Automate tv shows downloads from tvshows4mobile.com.

## Getting started
These instructions will get you a copy of the project up and running in your local machine for development and testing purposes.

## Prerequisites
- [Git](https://git-scm.com/download/)
- [Python 3.6 and above](https://www.python.org/downloads/)
- [PostgreSQL](https://www.postgresql.org/)
- [tesseract-ocr](https://github.com/tesseract-ocr/tesseract/)


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
export DOWNLOAD_LOC=
# celery
export CELERY_BROKER_URL=""
export CELERY_RESULT_BACKEND=""
export DJANGO_SETTINGS_MODULE='indeed.settings'

```
- Load the environment variable `source .env`
- Install dependencies to your virtual environment `pip install -r requirements.txt`
- Migrate changes to the newly created database `python manage.py migrate`

## Running job scrappers
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

## Automate movie downloads from tvshows4mobile.com
- To download your favourite tv show activate environment `source .env` and run `make movie`
- For more precise movie search enter series name by its name
- Enter series season to download
- Enter season episodes to download

## Starting the server
- Ensure you are in the project directory on the same level with `manage.py` and the virtual environment is activated
- Run the server `python manage.py runserver` or `make serve` 
