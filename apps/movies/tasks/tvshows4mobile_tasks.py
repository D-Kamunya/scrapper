# importing packages
import logging
import math
from time import sleep, time
import os
from io import BytesIO

from django.utils import timezone
from decouple import config
from PIL import Image
from pytesseract import image_to_string
from urllib.request import urlretrieve
from progress.bar import Bar
from progress.spinner import Spinner

from scrapper import celery_app

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import selenium.webdriver.common.keys
# Add capabilities to browser
capa = DesiredCapabilities.CHROME
capa["pageLoadStrategy"] = "none"

# Class to download video url and show progress
class Getter:
    def get(self, url, to):
        self.p = None

        def update(blocks, bs, size):
            if not self.p:
                if size < 0:
                    self.p = Spinner(to)
                else:
                    self.p = Bar(to, max=size, fill='#', suffix='%(percent)d%%')
            else:
                if size < 0:
                    self.p.update()
                else:
                    self.p.goto(blocks * bs)

        urlretrieve(url, to, update)
        self.p.finish()

# Decode CAPTACHA image
def decode_captcha(wait,driver,mainWindowHandle):
    wait.until(EC.visibility_of_element_located((By.XPATH, '//img[@alt="CAPTCHA Code"]')))
    wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@value='Continue Download']")))
    driver.execute_script("window.stop();")
    driver.switch_to_window(mainWindowHandle)
    # find part of the page with captcha
    captcha_img_ele = driver.find_element_by_xpath('//img[@alt="CAPTCHA Code"]') 
    location = captcha_img_ele.location
    size = captcha_img_ele.size
    png = driver.get_screenshot_as_png() # saves screenshot of entire page
    im = Image.open(BytesIO(png)) # uses PIL library to open image in memory
    left = location['x']
    top = location['y']
    right = location['x'] + size['width']
    bottom = location['y'] + size['height']
    im = im.crop((left, top, right, bottom)) # defines crop points
    # im.save('screenshot.png') # saves new cropped image
    text = image_to_string(im)
    text = text.split("\n")[0]
    cap_input = driver.find_element_by_xpath("//input[@name='captchainput']")
    cap_input.clear()
    cap_input.send_keys(text)
    page = driver.current_url
    download_btn = driver.find_element_by_xpath("//input[@value='Continue Download']")
    download_btn.click()
    return page

@celery_app.task(name="Download tvshows4mobile movie", serializer='json')
def download_tvshows4mobile_movie(site, title, season, episode):
    try:

        # Add additional Options to the webdriver
        chrome_options = Options()
        # add the argument and make the browser Headless.
        chrome_options.add_argument("--headless")
        p = {
         'download.default_directory':'/home/kinc/Downloads'}
        chrome_options.add_experimental_option('prefs', p)
        chrome_options.add_argument("--window-size=1920x1080")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        if config('MODE') == 'dev':
            driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options,desired_capabilities=capa)
        else:
            chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
            driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"),
                                      chrome_options=chrome_options,desired_capabilities=capa)
        # Driver wait time
        wait = WebDriverWait(driver, 20)

       
        # Get the movie site
        driver.get(site)

        # Maximize opened window
        driver.maximize_window()
        sleep(3)

        action = ActionChains(driver)


        # Get the movie and click it
        # let the driver wait  to locate the element before exiting out
        wait.until(EC.visibility_of_all_elements_located((By.XPATH, '//div[contains(@class,"data")]')))
        driver.execute_script("window.stop();")
        # Get the ID of the main open window
        mainWindowHandle = driver.current_window_handle
        try:
            movies = driver.find_elements_by_xpath(f"//a[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{title}')]")
            # movie = driver.find_element_by_partial_link_text(title)
            if len(movies)>1:
                opts = []
                print('Choose series from list')
                for idx, m in enumerate(movies):
                    opts.append(str(idx+1))
                    print(f"{idx+1}.{m.text}")
                while True:
                    movie = input()
                    if movie not in opts:
                        print('Invalid choice')
                    else:
                        mov = movies[int(movie)-1]
                        break
            else:
                mov = movies[0]
            title = mov.text
            mov.click()
        except Exception as e:
            logging.warning(e)
            print(f'Movie {title} not found')

       
        # Get the season and click it
        wait.until(EC.visibility_of_all_elements_located((By.XPATH, '//div[contains(@class,"data")]')))
        driver.execute_script("window.stop();")
        driver.switch_to_window(mainWindowHandle)
        if season == 'all':
            pass
        else:
            try:
                seasonn = driver.find_element_by_partial_link_text(f"Season {season}").click()
            except Exception as e:
                logging.warning(e)
                print(f'Season {season} not found')

        
        # Get the episode and click it
        wait.until(EC.visibility_of_all_elements_located((By.XPATH, '//div[contains(@class,"data")]')))
        driver.execute_script("window.stop();")
        driver.switch_to_window(mainWindowHandle)
        if episode == 'all':
            pass
        else:
            while True:
                try:
                    episodee = driver.find_element_by_partial_link_text(f"Episode {episode}").click()
                    break
                except:
                    try:
                        next_btn = driver.find_element_by_partial_link_text('Next').click()
                        wait.until(EC.visibility_of_all_elements_located((By.XPATH, '//div[contains(@class,"data")]')))
                        driver.execute_script("window.stop();")
                        driver.switch_to_window(mainWindowHandle)
                    except Exception as e:
                        logging.warning(e)
                        print(f'Episode {episode} not found')
                        break


        # Get the movie quality and click it
        wait.until(EC.visibility_of_all_elements_located((By.XPATH, '//div[contains(@class,"data")]')))
        driver.execute_script("window.stop();")
        driver.switch_to_window(mainWindowHandle)
        try:
            quality = driver.find_element_by_partial_link_text("HD Mp4 Format").click()
        except:
            try:
                quality = driver.find_element_by_partial_link_text("Mp4 Format").click()
            except Exception as e:
                logging.warning(e)
                print('Movie Quality not found')

        page=decode_captcha(wait,driver,mainWindowHandle)
        
        # Loop to decode captcha if wrong
        while True:
            wait.until(EC.visibility_of_element_located((By.TAG_NAME, "body")))
            driver.execute_script("window.stop();")
            driver.switch_to_window(mainWindowHandle)
            if driver.current_url == page:
                driver.get(page)
                decode_captcha(wait,driver,mainWindowHandle)
            else:
                break

        # Get movie video url
        video_url = driver.current_url
        driver.quit()

        # Start video download and show progress
        try:
            Getter().get(video_url, f"/mnt/4df6fa89-cc6d-4302-b1bb-569190748cb2/movies/{title} - S{season}E{episode}")
            print('Finished downloading movie')
        except Exception as e:
            logging.warning(e)
            print('Failed load video url')

    except Exception as e:
        logging.warning(e)
        print('Failed')
