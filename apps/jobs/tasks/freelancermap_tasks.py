# importing packages
import logging
from datetime import datetime
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

FREELANCERMAP_LOGIN_URL = 'https://www.freelancermap.de/login'
# FREELANCERMAP_JOBS_URL = 'https://www.freelancermap.de/projektboerse.html'
FREELANCERMAP_LOGIN_ERROR_URL = 'https://www.freelancermap.de/login?cause=1'


@celery_app.task(name="save scrapped freelancermap job", serializer='json')
def save_freelancermap_job(job):
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
            platform="Freelancermap",
            contract_type=job['contract_type'],
            tags=job['tags'],
            project_id=job['project_id']

        )
    except Exception as e:
        print(f'failed to save {title}')
        print(e)

    return print(f'{title} saved to db')


@celery_app.task(name="scrap freelancermap job descriptions", serializer='json')
def scrap_freelancermap_job_descriptions(job, driver):
    try:
        print(f"Started scrapping {job['title']}")
        driver.get(job['link'])
        # let the driver wait 3 seconds to locate the element before exiting out
        driver.implicitly_wait(10)

        try:
            company = driver.find_element_by_xpath('//div[@itemprop="hiringOrganization"]').text
        except:
            company = None
        try:
            dat = driver.find_element_by_xpath('//div[@itemprop="datePosted"]').text
            posted = datetime.strptime(dat, '%d/%m/%Y')
        except:
            posted = timezone.now()
        try:
            place = driver.find_element_by_xpath('//div[@itemprop="jobLocation"]').text
        except:
            place = ''
        try:
            country = driver.find_elements_by_xpath('//div[@class="project-detail"]')[6].find_element_by_class_name(
                "project-detail-description").text
        except:
            country = ''
        location = place + ',' + country
        try:
            contract_type = driver.find_elements_by_xpath('//div[@class="project-detail"]')[
                0].find_element_by_class_name("project-detail-description").text
        except:
            contract_type = None
        try:
            tags = []
            tags_el = driver.find_elements_by_xpath('//div[@class="cat_object"]')
            for tag_el in tags_el:
                tags.append(tag_el.text)
            tags = ";".join(tags)
        except:
            tags = None
        try:
            project_id = driver.find_elements_by_xpath('//div[@class="project-detail"]')[8].find_element_by_class_name(
                "project-detail-description").text
        except:
            project_id = None
        try:
            description = driver.find_element_by_xpath('//div[@itemprop="description"]').text
            summary = description[:130] + '...'
        except:
            summary = None
            description = None

    except:
        location = None
        description = None
        summary = None
        company = None
        posted = timezone.now()
        contract_type = None
        tags = None
        project_id = None
    job['location'] = location
    job['description'] = description
    job['summary'] = summary
    job['company'] = company
    job['posted'] = posted
    job['contract_type'] = contract_type
    job['tags'] = tags
    job['project_id'] = project_id
    print('Finished scrapping descriptions')
    save_freelancermap_job(job)


def login(driver, l_email, l_password):
    try:
        popup = driver.find_element_by_xpath('//button[@id="onetrust-accept-btn-handler"]')
        popup.click()
    except:
        pass
    try:
        email = driver.find_element_by_xpath('//input[@id="login"]')
    except Exception as e:
        logging.warning(e)
        print('Email input not located')
    try:
        password = driver.find_element_by_xpath('//input[@id="password"]')
    except Exception as e:
        logging.warning(e)
        print('Password input not located')
    try:
        login_btn = driver.find_element_by_xpath('//form[@id="loginform"]').find_element_by_xpath(
            '//button[@type="submit"]')
    except Exception as e:
        logging.warning(e)
        print('Login button not located')
    email.clear()
    password.clear()
    email.send_keys(l_email)
    password.send_keys(l_password)
    login_btn.click()
    driver.implicitly_wait(10)
    current_url = driver.current_url
    if FREELANCERMAP_LOGIN_ERROR_URL == current_url:
        raise Exception("Incorrect Login Credentials")


@celery_app.task(name="scrap freelancermap jobs", serializer='json')
def scrap_freelancermap_jobs(l_email, l_password, title):
    start_time = time()
    job_list = []
    FREELANCERMAP_JOBS_URL = f'https://www.freelancermap.de/projektboerse.html?pq={title}'
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
        # prefs = {
        #   "translate_whitelists": {"de":"en"},
        #   "translate":{"enabled":"true"}
        # }
        # chrome_options.add_experimental_option("prefs", prefs)
        if config('MODE') == 'dev':
            driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
            driver1 = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
        else:
            chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
            driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"),
                                      chrome_options=chrome_options)
            driver1 = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"),
                                       chrome_options=chrome_options)

        driver.get(FREELANCERMAP_LOGIN_URL)
        driver1.get(FREELANCERMAP_LOGIN_URL)

        sleep(3)

        action = ActionChains(driver)
        action = ActionChains(driver1)
        # let the driver wait 3 seconds to locate the element before exiting out
        driver.implicitly_wait(10)
        driver1.implicitly_wait(10)
        login(driver, l_email, l_password)
        login(driver1, l_email, l_password)

        try:
            driver.get(FREELANCERMAP_JOBS_URL)
            driver.implicitly_wait(10)
        except Exception as e:
            logging.warning(e)
            print('FAILED TO SEARCH JOBS URL')
        try:
            jobs_count = int(driver.find_element_by_xpath('//span[@id="total-results"]').text)
        except:
            jobs_count = 0
        if jobs_count == 0:
            raise Exception("No jobs found")
        count = 0
        while True:

            count += 1
            try:
                job_card = driver.find_elements_by_xpath('//li[contains(@class,"project-row")]')
            except:
                break
            for idx, job in enumerate(job_card):
                try:
                    title = job.find_element_by_class_name("title").text
                except:
                    title = 'None'
                try:
                    link = job.find_elements_by_xpath('//h3[@class="title"]/a')[idx].get_attribute(name="href")
                except:
                    link = None

                job = {
                    'title': title,
                    'link': link,
                }
                scrap_freelancermap_job_descriptions(job, driver1)

            print("Finished scraping the jobs for page: {}".format(str(count)))

            try:
                next_page = driver.find_elements_by_xpath('//a[@class="next"]')
                if len(next_page) > 1:
                    next_page = next_page[1]
                else:
                    next_page = next_page[0]
                next_page.click()
            except:
                break

        print('Finished scraping freelancermap jobs')


    except Exception as e:
        logging.warning(e)
        print('Failed')
