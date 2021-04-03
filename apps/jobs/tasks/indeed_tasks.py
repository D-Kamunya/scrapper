# importing packages
import logging
from datetime import timedelta
from django.utils import timezone
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from time import sleep, time
from scrapper import celery_app
from apps.jobs.models import Job
import os
from decouple import config

URL_24hrs = "http://www.indeed.com/jobs?q=All+Locations&filter=0&start=0&sort=date&fromage=1"
URL_14days = "http://www.indeed.com/jobs?q=All+Locations&filter=0&start=0&sort=date&fromage=14"


@celery_app.task(name="save scrapped indeed job", serializer='json')
def save_indeed_job(job):
    title = job['title']
    print(f'saving {title} to db')

    try:
        Job.objects.get_or_create(
            title=job['title'],
            link=job['link'],
            company=job['company'],
            summary=job['summary'],
            company_avatar=job['avatar'],
            description=job['description'],
            posted_at=job['posted'],
            platform="Indeed",
            review=job['review'],
            location=job['location'],
            salary=job['salary']
        )
    except Exception as e:
        print(f'failed to save {title}')
        print(e)

    return print(f'{title} saved to db')


@celery_app.task(name="scrap indeed job descriptions", serializer='json')
def scrap_indeed_job_description(job, driver):
    try:
        print(f"Started scrapping {job['title']}")
        driver.get(job['link'])
        try:
            close_popup = driver.find_element_by_id("popover-x")
            close_popup.click()
        except:
            pass
        try:
            jd = driver.find_element_by_xpath('//div[@id="jobDescriptionText"]').text
        except:
            jd = None
        try:
            company_avatar = driver.find_element_by_class_name("jobsearch-CompanyAvatar-image").get_attribute('src')
        except:
            company_avatar = None
    except:
        jd = None
        company_avatar = None
    job['description'] = jd
    job['avatar'] = company_avatar
    print('Finished scrapping descriptions')
    save_indeed_job(job)


@celery_app.task(name="scrap indeed jobs", serializer='json')
def scrap_indeed_jobs(title, location):
    if title == '' and location == '':
        url = "http://www.indeed.com/jobs?q=All+Locations&filter=0&start=0&sort=date&fromage=14"
    else:
        url = f'http://www.indeed.com/jobs?q={title}&l={location}&filter=0&start=0&sort=date&fromage=14'
    print(url)
    try:

        # Add additional Options to the webdriver
        chrome_options = Options()
        # add the argument and make the browser Headless.
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920x1080")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        if config('MODE') == 'dev':
            driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
            driver1 = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
        else:
            chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
            driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"),
                                      chrome_options=chrome_options)
            driver1 = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"),
                                       chrome_options=chrome_options)

        driver.get(url)
        sleep(3)

        action = ActionChains(driver)
        action = ActionChains(driver1)
        # let the driver wait 3 seconds to locate the element before exiting out
        driver.implicitly_wait(10)
        try:
            no_jobs = driver.find_element_by_xpath('//div[contains(@class,"no_results")]')
        except:
            no_jobs = False
        if no_jobs:
            raise Exception("No jobs found")
        try:
            close_popup = driver.find_element_by_id("popover-x")
            close_popup.click()
        except:
            pass

        try:
            pages = int(
                driver.find_element_by_xpath('//div[contains(@id,"searchCountPages")]').text.split(' ')[3].replace(',',
                                                                                                                   ''))
        except:
            pages = 100

        for i in range(0, pages):
            try:
                close_popup = driver.find_element_by_id("popover-x")
                close_popup.click()
            except:
                pass

            job_card = driver.find_elements_by_xpath('//div[contains(@class,"clickcard")]')

            for job in job_card:
                # .  not all companies have review
                try:
                    review = job.find_element_by_xpath('.//span[@class="ratingsContent"]').text
                except:
                    review = None
                # .   not 'all positions have salary
                try:
                    salary = job.find_element_by_xpath('.//span[@class="salaryText"]').text
                except:
                    salary = None

                try:
                    location = job.find_element_by_xpath('.//span[contains(@class,"location")]').text
                except:
                    location = None

                try:
                    summary = job.find_element_by_class_name("summary").text
                except:
                    summary = None

                try:
                    title = job.find_element_by_xpath('.//h2[@class="title"]//a').text
                except:
                    try:
                        title = job.find_element_by_xpath('.//h2[@class="title"]//a').get_attribute(name="title")
                    except:
                        title = 'None'
                try:
                    link = job.find_element_by_xpath('.//h2[@class="title"]//a').get_attribute(name="href")
                except:
                    link = None
                try:
                    company = job.find_element_by_xpath('.//span[@class="company"]').text
                except:
                    company = None
                try:
                    posted = job.find_element_by_xpath('.//span[@class="date-ally"]').text
                    if posted == "Today":
                        posted = timezone.now()
                    elif posted == "Just posted":
                        posted = timezone.now()
                    else:
                        days_ago = posted.split(' ')[0]
                        posted = timezone.now() - timedelta(days=int(days_ago))
                except:
                    posted = timezone.now()

                job = {
                    'title': title,
                    'location': location,
                    'company': company,
                    'link': link,
                    'summary': summary,
                    'avatar': '',
                    'description': '',
                    'posted': posted,
                    'salary': salary,
                    'review': review
                }
                scrap_indeed_job_description(job, driver1)

            print("Finished scraping the jobs for page: {}".format(str(i + 1)))

            try:
                next_page = driver.find_element_by_xpath('//a[@aria-label={}]//span[@class="pn"]'.format(i + 2))
                next_page.click()

            except:
                try:
                    next_page = driver.find_element_by_xpath('//a[@aria-label="Next"]//span[@class="np"]')
                    next_page.click()
                except:
                    print('Finished scraping the jobs')
                    break

            # except:
            # next_page = driver.find_element_by_xpath('//a[.//span[contains(text(),"Next")]]')
            # next_page.click()

        print('Finished scraping the jobs')


    except Exception as e:
        logging.warning(e)
        print('Failed')

# @celery_app.task(name="scrap indeed jobs 24hrs")
# def scrap_indeed_jobs_24hrs_(**kwargs):
#     """
#     Function scrap indeed jobs
#     """
#     scrap_indeed_jobs('','',URL_24hrs)

# @celery_app.task(name="scrap indeed jobs 14days")
# def scrap_indeed_jobs_14days_(**kwargs):
#     """
#     Function scrap indeed jobs from 14days ago
#     """
#     scrap_indeed_jobs('','',URL_14days)
