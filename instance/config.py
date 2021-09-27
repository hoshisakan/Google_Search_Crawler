import os

class Initialization:
    open_browser = True
    browser_type = 'edge'
    webdriver_path = "D:\Files\Project\Crawler\driver\msedgedriver.exe"
    base_url_list = {"google_search": "https://www.google.com.tw/"}
    output_path = "D:\Files\Project\Google_Search_Crawler\output\csv"
    crawler_target_list = []
    search_type_list = ['news', 'video', 'shopping']
    setting_file_path = os.path.join(os.getcwd(), 'crawler.ini')