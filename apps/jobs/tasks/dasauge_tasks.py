# importing packages
import logging
import math
from django.utils import timezone
from django.utils import dateparse
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from time import sleep, time
from scrapper import celery_app
from apps.jobs.models import Job
import os
from decouple import config


# DASAUGE_URL = "https://dasauge.de/jobs/stellenangebote/"


@celery_app.task(name="save scrapped dasauge job", serializer='json')
def save_dasauge_job(job):
    title = job['title']
    print(f'saving {title} to db')

    try:
        Job.objects.get_or_create(
            title=job['title'],
            link=job['link'],
            company_avatar=job['company_avatar'],
            contract_type=job['contract_type'],
            company=job['company'],
            summary=job['summary'],
            description=job['description'],
            posted_at=job['posted'],
            location=job['location'],
            platform="Dasauge",
            tags=job['tags']
        )
    except Exception as e:
        print(f'failed to save {title}')
        print(e)

    return print(f'{title} saved to db')


@celery_app.task(name="scrap dasauge job descriptions", serializer='json')
def scrap_dasauge_job_descriptions(job, driver):
    try:
        print(f"Started scrapping {job['title']}")
        driver.get(job['link'])
        # let the driver wait 3 seconds to locate the element before exiting out
        driver.implicitly_wait(10)

        try:
            location = driver.find_element_by_xpath('//span[contains(@itemprop,"address")]').text
        except:
            location = None
        try:
            description = driver.find_element_by_xpath('//table[@class="infotab"]').text
        except:
            description = None
        try:
            tags = []
            tags_el = driver.find_elements_by_xpath('//a[@rel="tag"]')
            for tag in tags_el:
                tags.append(tag.text)
            tags = ';'.join(tags)

        except:
            tags = None

    except:
        location = None
        description = None
        tags = None
    job['location'] = location
    job['description'] = description
    job['tags'] = tags
    print('Finished scrapping descriptions')
    save_dasauge_job(job)


@celery_app.task(name="scrap dasauge jobs", serializer='json')
def scrap_dasauge_jobs(title, location):
    DASAUGE_URL = f'https://dasauge.de/jobs/stellenangebote/?begriff={title}&land={location}'
    try:

        # Add additional Options to the webdriver
        chrome_options = Options()
        # add the argument and make the browser Headless.
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--window-size=1920x1080")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-dev-shm-usage")
        if config('MODE') == 'dev':
            driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
            driver1 = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
        else:
            chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
            driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"),
                                      chrome_options=chrome_options)
            driver1 = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"),
                                       chrome_options=chrome_options)

        driver.get(DASAUGE_URL)
        sleep(3)

        action = ActionChains(driver)
        action = ActionChains(driver1)
        # let the driver wait 3 seconds to locate the element before exiting out
        driver.implicitly_wait(10)
        try:
            no_jobs = driver.find_element_by_xpath('//div[contains(@id,"infobox")]/h2').text
        except:
            no_jobs = False
        if (no_jobs == 'Leider wurden keine Einträge nach deinen Kriterien gefunden.'
                or no_jobs == 'Unfortunately no entries were found according to your criteria.'):
            raise Exception("No jobs found")
        try:
            pages = math.ceil(int(driver
                                  .find_element_by_xpath('//div[contains(@class,"in")]')
                                  .text.split(' ')[0].replace('.', '')) / 15)
        except:
            pages = 100
        for i in range(0, pages):

            try:
                job_card = driver.find_elements_by_xpath('//div[contains(@id,"eliste")]/article')
            except:
                break
            for idx, job in enumerate(job_card):
                try:
                    title = job.find_elements_by_xpath('//h2[contains(@class,"hassub")]')[idx].text
                except:
                    title = 'None'
                try:
                    link = (job
                            .find_elements_by_xpath('//h2[contains(@class,"hassub")]')[idx]
                            .find_element_by_tag_name('a')
                            .get_attribute(name="href"))
                except:
                    link = None

                try:
                    company = (job
                               .find_elements_by_xpath('//div[@class="boxsubline toplinie"]')[idx]
                               .find_element_by_tag_name('em').text)
                except:
                    company = None

                try:
                    company_avatar = (job
                                      .find_elements_by_xpath(
                        '//div[@class="mlogomini mlogof uid"]')[idx]
                                      .find_element_by_tag_name('img').get_attribute(name="src"))
                except:
                    company_avatar = None
                try:
                    c_list = []
                    c_types = (job
                               .find_elements_by_xpath(
                        '//ul[@class="jobprops"]')[idx]
                               .find_elements_by_tag_name("li"))
                    for c in c_types:
                        c_list.append(c.text)
                    contract_type = ';'.join(c_list)
                except:
                    contract_type = None
                try:
                    summary = (job
                               .find_elements_by_xpath(
                        '//div[@class="neutral klickbatzen"]')[idx]
                               .find_element_by_tag_name('p').text[:130] + '...')
                except:
                    summary = None
                try:
                    posted = dateparse.parse_datetime(
                        job.find_elements_by_xpath('//time[@itemprop="datePosted"]')[idx]
                            .get_attribute(name='datetime'))
                except:
                    posted = timezone.now()

                job = {
                    'title': title,
                    'company': company,
                    'link': link,
                    'posted': posted,
                    'company_avatar': company_avatar,
                    'summary': summary,
                    'contract_type': contract_type,
                }
                scrap_dasauge_job_descriptions(job, driver1)

            print("Finished scraping the jobs for page: {}".format(str(i + 1)))

            try:
                next_page = driver.find_element_by_xpath('//a[@rel="next"]')
                next_page.click()
            except:
                break

        print('Finished scraping dasauge jobs')


    except Exception as e:
        logging.warning(e)
        print('Failed')
