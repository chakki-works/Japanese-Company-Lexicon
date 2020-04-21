import os
import time
import traceback
from pathlib import Path
from glob import glob
from functools import partial, wraps

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException

from settings import ROOT_DIR


class RetryLimitExceededError(Exception):
  """Raised when retry limit exceeded"""
  pass

def is_downloaded(target_pattern, file_count, driver):
  """Find all target zip files, and confirm the number of downloaing files is matching"""
  return len(glob(target_pattern)) == file_count

def retry(limit, wait_for=2):
  """Retry limit times before raise error"""
  def decorator(target):
    @wraps(target)
    def wrapper(*args, **kwargs):
      for i in range(limit):
        try:
          if i != 0:
            print('retry {}-th time'.format(i))
            return target(*args, **kwargs)
        except TimeoutException:
          time.sleep(wait_for)
          pass
      raise RetryLimitExceededError("Retry limit exceeded")
    return wrapper
  return decorator

@retry(5)
def click_with_waiting(wait, element, when):
  """Donwlading action with retry"""
  element.click()
  wait.until(when)


class Downloader:
  def __init__(self, url, download_directory=None):
    self.url = url
    self.download_directory = download_directory 

  def download(self):
    # downalod settings
    options = webdriver.ChromeOptions()
    prefs = { 
      "download.default_directory": self.download_directory,
      "download.prompt_for_download": False,
      "download.directory_upgrade": True
      }
    options.add_experimental_option('prefs', prefs)
    # options.add_argument('--headless') # disable headless mode could speed up the downloading process
    
    log_path = Path(self.download_directory)
    headless_log_path = Path.joinpath(log_path.parent, 'headless_log') # ../../hojin/headless_log
    browser = webdriver.Chrome(options=options, service_log_path=headless_log_path)
    # downloading process with retry
    try:
      # find all clickable downloading elements
      browser.get(self.url)
      table = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'tbl02'))
        )
      table = browser.find_elements_by_xpath("(//*[@class='tbl02'])[2]") 
      nodes = table[0].find_elements_by_tag_name('a')
      print(len(nodes)) # total 48

      wait = WebDriverWait(browser, 30)
      for i, node in enumerate(nodes, start=1):
        # retry process
        click_with_waiting(wait, node, partial(is_downloaded, os.path.join(self.download_directory, '*.zip'), i)) 
    except Exception as e:
      print('Failed to download file: ' + str(e))
      print(traceback.format_exc())


if __name__ == "__main__":
  url = 'https://www.houjin-bangou.nta.go.jp/download/zenken/' # the target page
  download_dir = os.path.join(ROOT_DIR, 'data/hojin/zip')  # download to where
  downloader = Downloader(url, download_dir)
  downloader.download()
