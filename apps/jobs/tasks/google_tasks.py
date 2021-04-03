# importing packages
import logging
import math
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


# GOOGLE_URL = "https://careers.google.com/jobs"


@celery_app.task(name="save scrapped google job", serializer='json')
def save_google_job(job):
    title = job['title']
    print(f'saving {title} to db')

    try:
        Job.objects.get_or_create(
            title=job['title'],
            link=job['link'],
            company=job['company'],
            summary=job['summary'],
            description=job['description'],
            posted_at=job['posted'],
            location=job['location'],
            platform="Google",
            min_qualifications=job['min_qualifications'],
            preferred_qualifications=job['preferred_qualifications'],
            responsibilities=job['responsibilities']

        )
    except Exception as e:
        print(f'failed to save {title}')
        print(e)

    return print(f'{title} saved to db')


@celery_app.task(name="scrap google job descriptions", serializer='json')
def scrap_google_job_description(job, driver):
    try:
        print(f"Started scrapping {job['title']}")
        driver.get(job['link'])
        # let the driver wait 3 seconds to locate the element before exiting out
        driver.implicitly_wait(10)
        try:
            cookie_popup = driver.find_element_by_xpath('//button[@data-gtm-ref="cookie-bar-ok"]')
            cookie_popup.click()
        except:
            pass

        try:
            location = driver.find_element_by_xpath('//p[@class="gc-job-detail__instruction-description"]/span/b').text
        except:
            try:
                location = driver.find_element_by_xpath('//li[@class="gc-job-tags__location"]').text
            except:
                location = None
        try:
            description = driver.find_element_by_xpath('//div[@itemprop="description"]').text
            summary = description[:130] + '...'
        except:
            description = None
            summary = None
        try:
            qualifications = driver.find_elements_by_xpath('//div[@itemprop="qualifications"]/ul')
            min_qualifications = qualifications[0].text
            preferred_qualifications = qualifications[1].text
        except:
            min_qualifications = None
            preferred_qualifications = None
        try:
            responsibilities = driver.find_element_by_xpath('//div[@id="accordion-responsibilities"]').text
        except:
            responsibilities = None
    except:
        location = None
        description = None
        summary = None
        min_qualifications = None
        preferred_qualifications = None
        responsibilities = None
    job['location'] = location
    job['description'] = description
    job['summary'] = summary
    job['min_qualifications'] = min_qualifications
    job['preferred_qualifications'] = preferred_qualifications
    job['responsibilities'] = responsibilities
    print('Finished scrapping descriptions')
    save_google_job(job)


@celery_app.task(name="scrap google jobs", serializer='json')
def scrap_google_jobs(title, location):
    GOOGLE_URL = f'https://careers.google.com/jobs/results/?location={location}&q={title}&sort_by=date'
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

        driver.get(GOOGLE_URL)
        sleep(3)

        action = ActionChains(driver)
        action = ActionChains(driver1)
        # let the driver wait 3 seconds to locate the element before exiting out
        driver.implicitly_wait(10)
        try:
            no_jobs = driver.find_element_by_xpath('//h2[@data-gtm-ref="search-results-no-results-title"]')
        except:
            no_jobs = False
        if no_jobs:
            raise Exception("No jobs found")
        try:
            cookie_popup = driver.find_element_by_xpath('//button[@data-gtm-ref="cookie-bar-ok"]')
            cookie_popup.click()
        except:
            pass

        try:
            pages = math.ceil(
                int(driver.find_element_by_xpath('//span[contains(@class,"gc-jobs-matched__count")]').text) / 20)
        except:
            pages = 120
        for i in range(0, pages):

            try:
                job_card = driver.find_elements_by_xpath('//ol[contains(@id,"search-results")]/li')
            except:
                break
            for job in job_card:
                try:
                    title = job.find_element_by_class_name("gc-card__title").text
                except:
                    title = 'None'
                try:
                    link = driver.find_element_by_xpath('//a[@aria-label="' + title + '"]').get_attribute(name='href')
                except:
                    link = None

                try:
                    company = job.find_element_by_xpath('//li[@class="gc-job-tags__team"]/span').text
                except:
                    company = None

                posted = timezone.now()
                job = {
                    'title': title,
                    'company': company,
                    'link': link,
                    'posted': posted,
                }
                scrap_google_job_description(job, driver1)

            print("Finished scraping the jobs for page: {}".format(str(i + 1)))

            try:
                next_page = driver.find_element_by_xpath('//a[@data-gtm-ref="search-results-next-click"]')
                next_page.click()
            except:
                break

        print('Finished scraping google jobs')


    except Exception as e:
        logging.warning(e)
        print('Failed')
