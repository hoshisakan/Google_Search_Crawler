from bs4 import BeautifulSoup
import requests
from requests.api import options
from selenium.webdriver import ChromeOptions, Chrome, Firefox, DesiredCapabilities
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import os
from msedge.selenium_tools import EdgeOptions, Edge
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

class Automation():
    """
        webdriver_path: use brower of driver path
        open_browser: if True selenuim action open browser page then in background action
    """
    def __init__(self, webdriver_path=None, open_browser=False, browser_type='chrome'):
        self.__webdriver_path = webdriver_path
        self.__open_browser = open_browser
        self.__browser_type = browser_type.lower()

    def __check_driver_is_exists(self):
        return os.path.exists(self.__webdriver_path)

    def __generate_chrome_driver(self):
        self.__options = ChromeOptions()
        if self.__open_browser is False:
            self.__options.add_argument("--headless")
            self.__options.add_argument('--disable-software-rasterizer')
        self.__options.add_argument('--disable-gpu')
        self.__options.add_argument('--disable-infobars')
        self.__options.add_argument('--no-sandbox')
        self.__driver = Chrome(executable_path=self.__webdriver_path, chrome_options=self.__options)
        return self.__driver

    def __generate_edge_driver(self):
        # method 1 but not use option parameters in webdriver
        # self.__driver = webdriver.Edge(executable_path=self.__webdriver_path)
        # method 2 from msedge.selenium_tools import Edge and EdgeOptions
        self.__options = EdgeOptions()
        self.__options.use_chromium = True
        if self.__open_browser is False:
            self.__options.add_argument('--headless')
        self.__options.add_argument('--disable-gpu')
        self.__options.add_argument('--no-sandbox')
        self.__options.add_argument('--disable-dev-shm-usage')
        
        self.__driver = Edge(executable_path=self.__webdriver_path, options=self.__options)
        return self.__driver

    def __generate_firefox_driver(self):
        self.__options = Options()
        if self.__open_browser is False:
            options.add_argument('--headless')
        self.__options.add_argument('--disable-gpu')
        self.__caps = DesiredCapabilities().FIREFOX
        self.__caps["marionette"] = True
        self.__driver = Firefox(executable_path=self.__webdriver_path, firefox_options=self.__options, capabilities=self.__caps)
        return self.__driver

    def __enter__(self):
        if self.__webdriver_path is None or self.__check_driver_is_exists() is False:
            raise Exception(f"The driver path {self.__webdriver_path} not found")
        if self.__browser_type == 'chrome':
            return self.__generate_chrome_driver()
        elif self.__browser_type == 'edge':
            return self.__generate_edge_driver()
        elif self.__browser_type == 'firefox':
            return self.__generate_firefox_driver()

    def __exit__(self, exc_type, exc_value, exc_info):
        self.__driver.quit()

class AnalysisData():
    """
        page_source: page source content
        parser_method: parser page static source, such as 'html.parser'
    """
    def __init__(self, page_source, parser_method):
        self.__page_source = page_source
        self.__parser_method = parser_method

    def __generate(self):
        return BeautifulSoup(self.__page_source, self.__parser_method)

    def __enter__(self):
        return self.__generate()

    def __exit__(self, exc_type, exc_value, exc_info):
        pass
