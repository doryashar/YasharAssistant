# import scheduler
import os, sys, time, re
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import selenium.common.exceptions as exceptions
from selenium.common.exceptions import NoSuchElementException, UnexpectedAlertPresentException
from selenium.webdriver.common.action_chains import ActionChains

from pathlib import Path
from PIL import Image
import io, base64

from selenium import webdriver
import src.xpaths as xp
import chromedriver_autoinstaller
from xvfbwrapper import Xvfb

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.debug = logger.info

class WhatsApper():
    def __init__(
        self,
        mobile = "Anonymous",
        headless = True,
        timeout = 120,
        ):
        
        self.mobile = self.fix_mobile(mobile) if mobile != 'Anonymous' else mobile
        self.base_link = "https://web.whatsapp.com/"
        self.suffix_link = "https://web.whatsapp.com/send?phone={mobile}&text&type=phone_number&app_absent=1"


        opt = webdriver.ChromeOptions()
        self.headless = headless
        if headless: 
            # opt.add_argument('--headless')
            self.display = Xvfb()
            self.display.start()
        opt.add_argument('--user-data-dir=./User_Data/{mobile}'.format(mobile=self.mobile))
        # opt.add_argument("--start-maximized")
        chromedriver_autoinstaller.install()
        self.driver = webdriver.Chrome(options=opt)
        self.wait = WebDriverWait(self.driver, timeout)
        
    def login(self):
        if not self.is_logged_in:
            logger.debug("Logging in")
            self.link_with_phone()
        
    
    def __enter__(self):
        self.login()
        return self
    
    @property
    def is_logged_in(self):
        try:
            self.driver.get(self.base_link)
            self.driver.maximize_window()
            logger.debug("Checking if already logged in")
            res = self.wait.until(EC.any_of(
                EC.presence_of_element_located((By.XPATH, xp.landing_page)),
                EC.presence_of_element_located((By.XPATH, xp.search_box))
            ))
            return not res.text.startswith("WHATSAPP WEB") #self.driver.find_element((By.XPATH, xp.search_box))
        except exceptions.TimeoutException:
            logger.debug("Timeout Reached. Not logged in")
            return False
        
        
    def fix_mobile(self, mobile):
        mobile = '+' + re.sub(r"[^0-9]", "", mobile)
        return mobile
        
    def get_code_for_phone(self, filename='link_code.png'):   
        # try:     
            self.driver.get(self.base_link)
            
            # Wait for the element with the specified text "Link with phone number" to be present
            element = self.wait.until(
                EC.presence_of_element_located((By.XPATH, xp.link_with_phone_link))
            )

            # Scroll into view (optional, depending on the page structure)
            self.driver.execute_script("arguments[0].scrollIntoView();", element)

            # Click the element
            element.click()
            
            # Wait for the input element with type="text" to be present
            input_element = self.wait.until(
                EC.presence_of_element_located((By.XPATH, '//input[@type="text"]'))
            )

            # Scroll into view (optional, depending on the page structure)
            self.driver.execute_script("arguments[0].scrollIntoView();", input_element)

            # Clear existing text, enter the mobile number, and simulate pressing Enter
            input_element.clear()
            for i in range(7): input_element.send_keys(Keys.BACKSPACE)
            input_element.send_keys(self.mobile)
            input_element.send_keys(Keys.RETURN)
            
            element = self.wait.until(EC.presence_of_element_located((By.XPATH, xp.link_code)))
            self.save_element_to_image(element, os.path.join('./Media', filename))

        # except Exception as exp:
        #     logger.error(f'Could not link with phone. exception: {exp}')
        #     return False
        
    def link_with_phone(self):   
        try:     
            code = self.get_code_for_phone()
            logger.info("Enter the code you received")
            if self.is_logged_in:
                logger.debug(f'Successfully linked with phone {self.mobile}')
                return True
            logger.error('Could not link with phone')
            return False
        except Exception as exp:
            logger.error(f'Could not link with phone. exception: {exp}')
            return False
    
    def save_element_to_image(self, element, filename='temp.jpg'):
        try:
            location = element.location
            size = element.size
            
            left = location['x']
            top = location['y']
            right = location['x'] + size['width']
            bottom = location['y'] + size['height']
            
            screenshot = self.driver.get_screenshot_as_base64()
            qr = Image.open(io.BytesIO(base64.b64decode(screenshot)))
            qr_cropped = qr.crop((left, top, right, bottom))
            if filename:
                qr_cropped.save(filename)
                return True
            else:
                #TODO: return base64
                pass
        except Exception as exp:
            logger.error(f'Exception while saving element to file: {exp}')
            return False
        
    def link_with_qr(self, filename='qr.png'):        
        if self.is_logged_in:
            self.logout()
            
        #TODO: wait for QR code         
        element = self.driver.find_element_by_id('hlogo') # find part of the page you want image of
        self.save_element_to_image(element, filename)
    
    def logout(self):
        logger.debug("Shutting down")
        dots_button = self.wait.until(EC.presence_of_element_located((By.XPATH, xp.dots_button)))
        dots_button.click()

        logout_item = self.wait.until(EC.presence_of_element_located((By.XPATH, xp.logout_button)))
        logout_item.click()
        
    def quit(self):
        self.driver.quit()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.quit()
        if self.headless: self.display.stop()
    
    def find_by_username(self, username):
        search_box = self.wait.until(EC.presence_of_element_located((By.XPATH, xp.search_box)))
        search_box.clear()
        search_box.send_keys(username)
        search_box.send_keys(Keys.ENTER)
        try:
            opened_chat = self.driver.find_elements(By.XPATH, xp.chat_title)
            if len(opened_chat) and opened_chat[0].text.upper() == username.upper():
                logger.debug(f'Successfully fetched chat "{username}"')
                return True
            else:
                logger.error(f'It was not possible to fetch chat "{username}"')
                return False
        except NoSuchElementException:
            logger.error(f'It was not possible to fetch chat "{username}"')
            return False
        
    def find_user_by_mobile(self, mobile):
        try:
            self.mobile = mobile
            link = self.suffix_link.format(mobile=mobile)
            self.driver.get(link)
            time.sleep(3)
            return True
        except UnexpectedAlertPresentException as bug:
            logger.error(f"An exception occurred: {bug}")
            return False
           
    def wait_to_datetime(self, at):
        for date_time in at.split():
            date_time_splitted =date_time.split(':')
            hourmin = date_time_splitted[-1]
            day = date_time_splitted[0] if len(date_time_splitted) > 1 else 'today'
    def send_message(self, target, message, attachements=None, time_between_messages=2, at=None):
        if not self.find_by_username(target) and not self.find_user_by_mobile(target):
            return False
        if at is not None:
            self.wait_to_datetime(at)
        if attachements:
            self._send_picture(target, attachements, message, time_between_messages)
        else:
            self._send_message(target, message, time_between_messages)
    
    def _send_picture(self, target, picture: Path, caption="", time_between_messages=2):
        try:
            filename = os.path.realpath(picture)
            
            # Get the attachment button
            clipButton = self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="main"]/footer//*[@data-icon="attach-menu-plus"]/..')))
            clipButton.click()
        
            # To send an Image
            imgButton = self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[1]/div[2]/div/span/div/ul/div/div[2]/li/div/input')))
            imgButton.send_keys(filename)
            if caption:
                self.add_caption(caption, media_type="image")
                
            # Add the attachment
            # Waiting for the pending clock icon to disappear
            self.wait.until_not(EC.presence_of_element_located((By.XPATH, '//*[@id="main"]//*[@data-icon="msg-time"]')))
            sendButton = self.wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="app"]/div[1]/div/div[3]/div[2]/span/div/span/div/div/div[2]/div/div[2]/div[2]/div/div/span')))
            sendButton.click()

            # Waiting for the pending clock icon to disappear again - workaround for large files or loading videos.
            # Appropriate solution for the presented issue. [nCKbr]
            self.wait.until_not(EC.presence_of_element_located((By.XPATH, '//*[@id="main"]//*[@data-icon="msg-time"]')))         
            logger.info(f"Picture has been successfully sent to {target}")
            time.sleep(time_between_messages)
        except (NoSuchElementException, Exception) as bug:
            logger.exception(f"Failed to send a message to {target} - {bug}")

    def add_caption(self, message: str, media_type: str = "image"):
        xpath_map = {
            "image": "/html/body/div[1]/div/div/div[3]/div[2]/span/div/span/div/div/div[2]/div/div[1]/div[3]/div/div/div[2]/div[1]/div[1]",
            "video": "/html/body/div[1]/div/div/div[3]/div[2]/span/div/span/div/div/div[2]/div/div[1]/div[3]/div/div/div[1]/div[1]",
            "file": "/html/body/div[1]/div/div/div[3]/div[2]/span/div/span/div/div/div[2]/div/div[1]/div[3]/div/div/div[1]/div[1]",
        }
        inp_xpath = xpath_map[media_type]
        input_box = self.wait.until(
            EC.presence_of_element_located((By.XPATH, inp_xpath))
        )
        for line in message.split("\n"):
            input_box.send_keys(line)
            ActionChains(self.driver).key_down(Keys.SHIFT).key_down(Keys.ENTER).key_up(
                Keys.ENTER
            ).key_up(Keys.SHIFT).perform()
            
    def _send_message(self, target, message, time_between_messages):
        try:
            input_box = self.wait.until(
                EC.presence_of_element_located((By.XPATH, xp.message_box))
            )
            for line in message.split("\n"):
                input_box.send_keys(line)
                ActionChains(self.driver).key_down(Keys.SHIFT).key_down(
                    Keys.ENTER
                ).key_up(Keys.ENTER).key_up(Keys.SHIFT).perform()
            input_box.send_keys(Keys.ENTER)
            logger.info(f"Message sent successfully to {target}")
            time.sleep(time_between_messages)
        except (Exception, NoSuchElementException) as e:
            logger.error("send message exception: ", e)
            return
        
if __name__ == '__main__':
    import argparse
    import shutil

    DEFAULT_MOBILE = "972548826569"
    args = sys.argv[1:] if len(sys.argv) > 1 else '--message שלום -t תתעלם'.split()
    
    parser = argparse.ArgumentParser(description='PyWhatsapp Guide')
    parser.add_argument('--from', dest='mobile', action='store', type=str, default=DEFAULT_MOBILE, help='Phone number of the sender')
    parser.add_argument('--message', '-m', action='store', type=str, required=True, help='Message you want to send')
    parser.add_argument('--target', '-t', action='store', type=str, required=True, help='Target username/phone number')
    parser.add_argument('--remove_cache', action='store_true', default=False, help='Remove Cache | Scan QR again or Not')
    parser.add_argument('--headless', action='store_true', default=False, help='Enable Headless Driver')
    parser.add_argument('--at', type=str, default=None, help='Send message at specific time/day, usage: [day/dd_mm_yyyy]:[hour/24h]_[minute] ex: 25_05_2022:20_00 or monday:10_00')
    args = parser.parse_args(args)
    
    if args.remove_cache:
        logger.info("Removing User_Data folder")
        shutil.rmtree('User_Data/', ignore_errors=True)
        
    with WhatsApper(mobile=args.mobile, headless=args.headless) as cli:
        # cli.find_by_username(args.target)
        cli.send_message(args.target, args.message, at=args.at)

    logger.info('Goodbye!')