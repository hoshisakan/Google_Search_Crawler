import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from module.handle_exception import HandleException
from module.reptile import Automation, AnalysisData
from selenium.webdriver.support.wait import WebDriverWait
# from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from instance.config import Initialization as Init
from threading import Thread
from module.log_generate import Loggings
from module.date import DateTimeTools as DT
import re
import pandas as pd
from module.argument_config import ArgumentConfig
import configparser


logger = Loggings()

def timer(func):
    def time_count():
        exc_start_time = DT.get_current_datetime()
        func()
        exc_end_time = DT.get_current_datetime()
        exc_time = exc_end_time - exc_start_time
        msg = "執行時間: {}".format(exc_time)
        logger.info(msg)
    return time_count

def write_iterator_to_log(iterator):
    [logger.info(read_iterator_info) for read_iterator_info in iterator]

def write_iterator_multiple_to_log(iterator):
    for outside_index, outside in enumerate(iterator, 1):
        logger.info(f'The {outside_index} iterator')
        logger.info('------------------------------------------------------')
        for inner_index, inner_iterator in enumerate(outside, 1):
            logger.info(f"The {inner_index} data is {inner_iterator}")
        logger.info('------------------------------------------------------')

class GoogleSearchInfo():
    """
        :Parameters:
            keyword: The Google search keyword.
            search type: news, video, shopping,
            page count: The Google search get info page count
    """
    def __init__(self, keyword, search_type, page_count):
        self.__base_url = Init.base_url_list['google_search']
        self.__browser_type = Init.browser_type
        self.__webdriver_path = Init.webdriver_path
        self.__open_browser = Init.open_browser
        self.__output_path = Init.output_path
        self.__page_count = page_count
        self.__keyword = keyword
        self.__search_type = search_type
    
    def __generate_list(self, size):
        return [[] for _ in range(0, size)]

    def __check_list_none(self, check_list):
        return None in check_list

    def __wait_element_load(self, **load):
        return WebDriverWait(load['driver'], load['wait_time'], load['check_time']).until(EC.presence_of_all_elements_located(load['locator']))

    def __wait_element_load_for_clickable(self, **load):
        return WebDriverWait(load['driver'], load['wait_time'], load['check_time']).until(EC.element_to_be_clickable(load['locator']))

    def __check_path_exists_and_create(self, path):
        if not os.path.exists(self.__output_path):
            os.makedirs(self.__output_path)

    def __check_path_exists_and_remove(self, path):
        if os.path.exists(path):
            os.remove(path)
            logger.info(f'Removeing duplicate file from path {path}.')

    def __filter_duplicate_items(self, filter_condition, filter_items):
        return re.sub(filter_condition, '', filter_items)

    def __get_news(self, page_source_list):
        info = []
        try:
            logger.info(f'Will load source page total: {len(page_source_list)}')
            info_columns = ['title', 'summary', 'updated_length', 'url', 'newspaper', 'search_page']
            logger.info("Starting get hot news information from page source")
            for page_count, page_source in enumerate(page_source_list, 1):
                current_info_dict = []
                if page_source is None:
                    raise Exception("Load static page source failed")
                logger.info(f"Current page is: {page_count}")

                with AnalysisData(page_source, 'html.parser') as soup:
                    search_div_tag = soup.find('div', {'id': 'search'})
                    if page_count > 0 and search_div_tag is not None:
                        news_all_g_card_element = search_div_tag.find_all('g-card')
                    else:
                        raise Exception('No hot news div tag found')
                    for current_page_news_count, current_g_card_element in enumerate(news_all_g_card_element, 1):
                        one_of_card_div_tag = current_g_card_element.find('div', {'class': 'iRPxbe'})
                        if one_of_card_div_tag is not None:
                            newspaper_div_tag = one_of_card_div_tag.find('div', {'class': 'CEMjEf'})
                            newspaper = newspaper_div_tag.get_text().strip().replace('\n\r', '') if newspaper_div_tag is not None else ''
                            title_div_tag = one_of_card_div_tag.find('div', { 'class', 'mCBkyc JQe2Ld nDgy9d' })
                            title = title_div_tag.get_text().strip().replace('\n\r', '') if title_div_tag is not None else ''
                            summary_div_tag = one_of_card_div_tag.find('div', { 'class': 'GI74Re nDgy9d' })
                            summary = summary_div_tag.get_text().strip().replace('\n\r', '') if summary_div_tag is not None else ''
                            update_time_div_tag = one_of_card_div_tag.find('div', { 'class': 'ZE0LJd iuBdze' })
                            update_time = update_time_div_tag.find('p', { 'class': 'S1FAPd ecEXdc' }).get_text().strip().replace('\n\r', '') if update_time_div_tag is not None else ''
                            link_a_tag = current_g_card_element.find('a')
                            link = link_a_tag['href'] if link_a_tag is not None else ''
                            temp_list = [title, summary, update_time, link, newspaper, page_count]

                            if any(temp_list) is True:
                                current_info_dict.append(dict(zip(info_columns, temp_list)))
                            else:
                                logger.error(f'Found empty in current page {page_count} the {current_page_news_count} data')
                            if not newspaper and not title and not summary and not update_time and not link:
                                raise Exception(f"Data catch empty\n{current_info_dict}")
                info.extend(list({v['title']:v for v in current_info_dict}.values()))
            logger.info("Finish get google search news information from page source")
        except Exception as e:
            logger.error(HandleException.show_exp_detail_message(e))
        return info

    def __get_video(self, page_source_list):
        info = []
        try:
            info_columns = ['title', 'summary', 'update_time', 'url', 'video_time', 'uploader', 'search_page']
            logger.info("Starting get video information from page source")
            for page_count, page_source in enumerate(page_source_list, 1):
                current_info_dict = []
                if page_source is None:
                    raise Exception("Load static page source failed")
                logger.info(f"Current page is: {page_count}")
                with AnalysisData(page_source, 'html.parser') as soup:
                    search_div_tag = soup.find('div', {'id': 'search'})
                    video_main_div_tag = search_div_tag.find('div', {'class': 'v7W49e'}) if page_count > 0 and search_div_tag is not None or not search_div_tag else None
                    all_video_div_tag = video_main_div_tag.find_all('div', {'class': 'g'}) if video_main_div_tag is not None or not video_main_div_tag else None
                    if all_video_div_tag is None:
                        raise Exception('Not found any match video div tag')
                    else:
                        for current_page_video_count, current_video_items in enumerate(all_video_div_tag, 1):
                            video_items_outer_div_tag = current_video_items.find('div', {'class': 'tF2Cxc'})
                            title_h3_tag = video_items_outer_div_tag.find('div', { 'class': 'yuRUbf' }).find('a').find('h3', {'class': 'LC20lb DKV0Md'}) if video_items_outer_div_tag is not None else ''
                            title = title_h3_tag.getText().strip().replace('\n\r', '') if title_h3_tag is not None else ''
                            # logger.info(f'Current page {current_page_video_count} the title is: {title}')
                            video_items_inner_div_tag = current_video_items.find('div', {'class': 'IsZvec'})
                            video_a_tag_class_div = video_items_inner_div_tag.find('div', {'class': 'N3nEGc'})
                            video_a_tag = video_a_tag_class_div.find('a') if video_a_tag_class_div is not None else None
                            link = video_a_tag['href'] if video_a_tag is not None else ''
                            # image_g_img_tag = video_a_tag.find('g-img').find('img')
                            # image_src_link = image_g_img_tag['src'] if image_g_img_tag is not None else ''
                            video_time_div_tag = video_a_tag.find('div', {'class': 'ij69rd UHe5G'}) if video_a_tag is not None else None
                            video_time = video_time_div_tag.getText() if video_time_div_tag is not None else ''
                            summary_span_tag = video_items_inner_div_tag.find('span', {'class': 'aCOpRe'})
                            summary = summary_span_tag.getText().strip().replace('\n\r', '')if summary_span_tag is not None else ''
                            update_time_and_uploader_div_tag = video_items_inner_div_tag.find('div', {'class': 'fG8Fp uo4vr'})
                            update_time_and_uploader_list = update_time_and_uploader_div_tag.getText().strip().replace(' ', '').replace('上傳者：', '').replace('Uploadedby', '').split('·') if update_time_and_uploader_div_tag is not None else ''
                            update_time = '' if not update_time_and_uploader_list or len(update_time_and_uploader_list) < 1 else update_time_and_uploader_list[0]
                            uploader = '' if not update_time_and_uploader_list or len(update_time_and_uploader_list) < 2 else update_time_and_uploader_list[1]
                            temp_list = [title, summary, update_time, link, video_time, uploader, page_count]
                            if any(temp_list) is True and link:
                                current_info_dict.append(dict(zip(info_columns, temp_list)))
                            else:
                                logger.error(f'Found empty in current page {page_count} the {current_page_video_count} data')
                info.extend(list({v['title']:v for v in current_info_dict}.values()))
            logger.info("Finish get video information from page source")
        except Exception as e:
            logger.error(HandleException.show_exp_detail_message(e))
        return info

    def __get_shopping(self, page_source_list):
        info = []
        try:
            logger.info(f'Will load source page total: {len(page_source_list)}')
            info_columns = ['name', 'price', 'platform', 'free shipping option', 'url', 'search_page']
            logger.info("Starting get shopping information from page source")
            for page_count, page_source in enumerate(page_source_list, 1):
                current_info_dict = []
                if page_source is None:
                    raise Exception("Load static page source failed")
                logger.info(f"Current page is: {page_count}")

                with AnalysisData(page_source, 'html.parser') as soup:
                    search_div_tag = soup.find('div', {'id': 'search'})
                    commodities_div_tag = search_div_tag.find('div', {'class': 'v7W49e'}) if search_div_tag is not None else None
                    find_grid_tag = False
                    
                    all_commodities_div_grid_tag = commodities_div_tag.find_all('div', {'class': 'sh-dgr__gr-auto sh-dgr__grid-result'}) if commodities_div_tag is not None else None
                    
                    if all_commodities_div_grid_tag is not None and any(all_commodities_div_grid_tag) is True:
                        logger.info(f'find grid element')
                        all_commodities_div_tag = all_commodities_div_grid_tag
                        find_grid_tag = True
                    else:
                        logger.info('find list element')
                        all_commodities_div_tag = commodities_div_tag.find_all('div', {'class': 'sh-dlr__content xal5Id'}) if commodities_div_tag is not None else None
                        find_grid_tag = False

                    if all_commodities_div_tag is None or any(all_commodities_div_tag) is False:
                        logger.error(f'No div tag found: {all_commodities_div_tag}')
                        # raise Exception('No div tag found')
                        pass
                    elif all_commodities_div_tag is not None and find_grid_tag is True:
                        logger.info(f'all commodities count: {len(all_commodities_div_tag)}')
                        for current_page_commodity_count, current_commodity_tag in enumerate(all_commodities_div_tag, 1):
                            commodity_top_div = current_commodity_tag.find('div', {'class': 'i0X6df'})
                            commodity_inner_div = commodity_top_div.find('div', {'class': 'sh-dgr__content'}) if commodity_top_div is not None else None
                            commodity_name_and_link_tag = commodity_inner_div.find('span', {'class': 'C7Lkve'}) if commodity_inner_div is not None else None
                            commodity_first_a_tag = commodity_name_and_link_tag.find('a', {'class': 'Lq5OHe eaGTj translate-content'}) if commodity_name_and_link_tag is not None else None
                            commodity_name_tag = commodity_first_a_tag.find('h4', {'class': 'Xjkr3b'}) if commodity_first_a_tag is not None else None
                            commodity_name = commodity_name_tag.getText() if commodity_name_tag is not None else ''
                            # commodity_link = self.__base_url.strip('/') + commodity_first_a_tag['href'] if commodity_first_a_tag is not None else ''
                            commodity_other_items_tag = commodity_inner_div.find('div', {'class': 'zLPF4b'}) if commodity_inner_div is not None else None
                            commodity_second_a_tag = commodity_other_items_tag.find('a', {'class': 'eaGTj mQaFGe shntl'}) if commodity_other_items_tag is not None else None
                            commodity_link = self.__base_url.strip('/') + commodity_second_a_tag['href'] if commodity_second_a_tag is not None else ''
                            # commodity_price = commodity_second_a_tag.find('span', {'class': 'a8Pemb OFFNJ'}).getText().replace('.00', '').replace(',', '').strip('NT$').strip('$') if commodity_second_a_tag is not None else ''
                            commodity_price = self.__filter_duplicate_items('[.00|,|NT$|$| + tax]', commodity_second_a_tag.find('span', {'class': 'a8Pemb OFFNJ'}).getText()) if commodity_second_a_tag is not None else ''
                            commodity_buy_platform = commodity_other_items_tag.find('div', {'class': 'aULzUe IuHnof'}).getText() if commodity_other_items_tag is not None else ''
                            commodity_free_shipping_option = commodity_other_items_tag.find('div', {'class': 'bONr3b'}).getText() if commodity_other_items_tag is not None else ''
                            temp_list = [commodity_name, commodity_price, commodity_buy_platform, commodity_free_shipping_option, commodity_link, page_count]
                            if any(temp_list) is True:
                                current_info_dict.append(dict(zip(info_columns, temp_list)))
                            else:
                                logger.error(f'Found empty in current page {page_count} the {current_page_commodity_count} data')
                        info.extend(list({v['name']:v for v in current_info_dict}.values()))
                    elif all_commodities_div_tag is not None and find_grid_tag is False:
                        logger.info(f'all commodities count: {len(all_commodities_div_tag)}')
                        for current_page_commodity_count, current_commodity_tag in enumerate(all_commodities_div_tag, 1):
                            commodity_inner_div = current_commodity_tag.find('div', {'class': 'ZGFjDb'})
                            commodity_name_and_link_tag = commodity_inner_div.find('div', {'class': 'LNwFVe'}) if commodity_inner_div is not None else None
                            commodity_first_a_tag = commodity_name_and_link_tag.find('a', {'class': 'VZTCjd translate-content'}) if commodity_name_and_link_tag is not None else None
                            # commodity_link = self.__base_url.strip('/') + commodity_first_a_tag['href'] if commodity_first_a_tag is not None else ''
                            commodity_name_h3_tag = commodity_first_a_tag.find('h3', {'class': 'OzIAJc'}) if commodity_first_a_tag is not None else None
                            commodity_name = commodity_name_h3_tag.getText() if commodity_name_h3_tag is not None else ''
                            commodity_other_items_tag = commodity_inner_div.find('div', {'class': 'm31woc'}) if commodity_inner_div is not None else None
                            commodity_second_a_tag = commodity_other_items_tag.find('a', {'class': 'LBbJwb shntl'}) if commodity_other_items_tag is not None else None
                            commodity_link = self.__base_url.strip('/') + commodity_second_a_tag['href'] if commodity_second_a_tag is not None else ''
                            commodity_price_span_tag = commodity_second_a_tag.find('span', {'class': 'a8Pemb OFFNJ'})
                            # commodity_price = commodity_price_span_tag.getText().replace('.00', '').replace(',', '').strip('NT$').strip('$') if commodity_price_span_tag is not None else ''
                            commodity_price = self.__filter_duplicate_items('[.00|,|NT$|$| + tax]', commodity_price_span_tag.getText()) if commodity_price_span_tag is not None else ''
                            commodity_buy_platform_div_tag = commodity_other_items_tag.find('div', {'class': 'b07ME mqQL1e'}) if commodity_other_items_tag is not None else None
                            commodity_buy_platform = commodity_buy_platform_div_tag.getText() if commodity_buy_platform_div_tag is not None else ''
                            commodity_free_shipping_option_div = commodity_other_items_tag.find('div', {'class': 'vEjMR'}) if commodity_other_items_tag is not None else None
                            commodity_free_shipping_option = commodity_free_shipping_option_div.getText() if commodity_free_shipping_option_div is not None else ''
                            temp_list = [commodity_name, commodity_price, commodity_buy_platform, commodity_free_shipping_option, commodity_link, page_count]
                            # logger.info(temp_list)
                            if any(temp_list) is True:
                                current_info_dict.append(dict(zip(info_columns, temp_list)))
                            else:
                                logger.error(f'Found empty in current page {page_count} the {current_page_commodity_count} data')
                            # logger.info(f'Commodity name is: {commodity_name}\nCommodity link is: {commodity_link}')
                            # logger.info('-------------------------------------------------------')
                        info.extend(list({v['name']:v for v in current_info_dict}.values()))
            logger.info("Finish get shopping information from page source")
        except Exception as e:
            logger.error(HandleException.show_exp_detail_message(e))
        return info

    def __loading_google_search_page_source(self):
        page_source_list = []
        try:
            with Automation(
                webdriver_path=self.__webdriver_path,
                open_browser=self.__open_browser,
                browser_type=self.__browser_type
            ) as d:
                browser_version = d.capabilities['browserVersion']
                browser_name = d.capabilities['browserName']
                logger.info(f"Search keyword is: {self.__keyword}, Search page count is: {self.__page_count}, Data Type is: {self.__search_type}, Browser name is: {browser_name}, Browser version is: {browser_version}")

                search_params_list = ['nws', 'vid', 'shop', 'isch', 'bks']
                country_code_list = ['en', 'zh-TW']

                if self.__search_type == 'news':
                    search_type = search_params_list[0]
                elif self.__search_type == 'video':
                    search_type = search_params_list[1]
                elif self.__search_type == 'shopping':
                    search_type = search_params_list[2]
                else:
                    raise Exception("Not mathch search type option.")

                d.get(f'{self.__base_url}/search?q={self.__keyword}&tbm={search_type}&hl={country_code_list[0]}')

                page_source_list.append(d.page_source)
                logger.info(f'Load 1 page source finish')

                for _ in range(0, self.__page_count - 1):
                    next_page_button = self.__wait_element_load_for_clickable(
                        driver=d,
                        locator=(By.XPATH, "/html/body[@id='gsr']/div[@id='main']/div[@id='cnt']/div[@id='rcnt']/div[@class='D6j0vc']/div[@id='center_col']/div[6]/span[@id='xjs']/table[@class='AaVjTc']/tbody/tr/td[@class='d6cvqb'][2]/a[@id='pnnext']/span[2]"),
                        wait_time=10,
                        check_time=1)
                    next_page_button.click()
                    self.__wait_element_load(driver=d, locator=(By.CLASS_NAME, "GyAeWb"), wait_time=10, check_time=1)
                    self.__wait_element_load(driver=d, locator=(By.CLASS_NAME, "eqAnXb"), wait_time=10, check_time=1)
                    page_source_list.append(d.page_source)
                    logger.info(f'Load {_ + 2} page source finish')
            logger.info("Get all page static source")
        except Exception as e:
            logger.error(HandleException.show_exp_detail_message(e))
        return page_source_list

    def scrape(self):
        result = []
        try:
            page_source_list = self.__loading_google_search_page_source()
            if self.__check_list_none(page_source_list) is True:
                raise Exception("Load all source page failed")
            if self.__search_type == 'news':
                result = self.__get_news(page_source_list)
            elif self.__search_type == 'video':
                result = self.__get_video(page_source_list)
            elif self.__search_type == 'shopping':
                result = self.__get_shopping(page_source_list)

            if any(result) is True:
                try:
                    if self.__output_path is None:
                        raise FileNotFoundError('Output path is required.')
                    self.__check_path_exists_and_create(self.__output_path)
                except (FileNotFoundError, OSError, Exception) as fe:
                    logger.error(HandleException.show_exp_detail_message(fe))
                else:
                    full_path = f"{self.__output_path}\\{self.__keyword}_{self.__search_type}.csv"
                    self.__check_path_exists_and_remove(full_path)
                    df = pd.DataFrame(result)
                    logger.debug(df)
                    df.to_csv(full_path, encoding='utf-8-sig', index=False)
                    logger.info(f'Create keyword {self.__keyword} csv file successful!')
        except Exception as e:
            logger.error(HandleException.show_exp_detail_message(e))

def init_global():
    config = configparser.ConfigParser()
    logger.debug(Init.setting_file_path)
    config.read(Init.setting_file_path, encoding="utf-8")
    Init.crawler_target_list = [read.strip().split(',') for read in config.get("Settings", "Crawler_Task").split('|')]
    Init.output_path = config.get("Settings", "Output_Path")
    temp_open_browser = config.get("Settings", "Open_Browser")
    Init.open_browser = False if not temp_open_browser or temp_open_browser.upper() == 'NO' else True
    Init.webdriver_path = config.get("Settings", "Driver_Path")
    Init.browser_type = config.get("Settings", "Browser_Type")

def run_job():
    ArgumentConfig.run()
    init_global()

    task_job = []

    for task in Init.crawler_target_list:
        logger.info(f"Init task {task}")
        if task[1] in Init.search_type_list:
            obj = GoogleSearchInfo(
                keyword=task[0], search_type=task[1],
                page_count=int(task[2])
            )
            task_job.append(Thread(target=obj.scrape))
        else:
            logger.error(f'Not found the "{task[1]}" search type.\n Task {task[0]} execute failed.')

    for job in task_job:
        job.start()

    for job in task_job:
        job.join()

if __name__ == '__main__':
    run_job()