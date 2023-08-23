import json
import time
from datetime import datetime
import os
import hostel.constants as const
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException



class Hostel(webdriver.Chrome):
    def __init__(self, driver_path='src/chromedriver.exe', chrome_options=None, teardown=False):
        self.driver_path = driver_path
        self.teardown = teardown
        os.environ['PATH'] += self.driver_path

        # provided chrome_options or create default options with "detach" experimental option
        # https://stackoverflow.com/questions/51865300/python-selenium-keep-browser-open
        chrome_options = chrome_options or Options()
        chrome_options.add_experimental_option("detach", True)
        super(Hostel, self).__init__(options=chrome_options)
        self.implicitly_wait(15)
        self.maximize_window()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.teardown:
            self.quit()

    def land_first_page(self):
        self.get(const.BASE_URL)

    def select_place_to_go(self, place_to_go):
        search_field = self.find_element('xpath', '//*[@id="__layout"]/div/div[2]/div[2]/div[2]/div/div/div/div[1]/div[1]/div/div[2]/input')
        search_field.clear()
        search_field.send_keys(place_to_go)

        first_result = self.find_element('xpath', '// *[ @ id = "325"]')
        first_result.click()

    def select_dates(self):
        time.sleep(2)
        open_calender = self.find_element('xpath', '//*[@id="__layout"]/div/div[2]/div[2]/div[2]/div/div/div/div[3]/div/div/div/div[2]/input')
        open_calender.click()

        time.sleep(2)
        navagate_month = self.find_element('xpath','//*[@id="__layout"]/div/div[2]/div[2]/div[2]/div/div/div/div[3]/div[2]/div[2]/div/div/div[1]/div[2]/div[1]/div[3]/button')
        navagate_month.click()

        time.sleep(2)
        check_in_date = self.find_element('xpath', '//*[@id="__layout"]/div/div[2]/div[2]/div[2]/div/div/div/div[3]/div[2]/div[2]/div/div/div[2]/div[1]/div[2]/div[33]/button/div')
        check_in_date.click()

        time.sleep(2)
        check_out_date = self.find_element('xpath', '//*[@id="__layout"]/div/div[2]/div[2]/div[2]/div/div/div/div[3]/div[2]/div[2]/div/div/div[2]/div[1]/div[2]/div[39]/button')
        check_out_date.click()

        time.sleep(2)
        aplly_dates = self.find_element('xpath','//*[@id="__layout"]/div/div[2]/div[2]')
        aplly_dates.click()

    def click_search(self):
        time.sleep(2)
        search = self.find_element('xpath', '/html/body/div[3]/div/div/div[2]/div[2]/div[2]/div/div/div/div[5]/button')
        search.click()

        time.sleep(2)
        click_outside = self.find_element('xpath', '//*[@id="__layout"]/div/div[2]/div/div[2]/div[2]')
        click_outside.click()
        time.sleep(5)

    def set_filter(self, min_value):
        time.sleep(5)
        search_filter = self.find_element('xpath', '//*[@id="__layout"]/div/div[2]/div/div[1]/div[1]/div/div/div/button[1]')
        search_filter.click()

        time.sleep(3)
        enter_min_value = self.find_element('xpath', '//*[@id="__layout"]/div/div[2]/div/div[1]/div[1]/div/div[2]/div/div[2]/div/div[1]/div[1]/div[1]/div/div[1]/input')
        enter_min_value.clear()
        enter_min_value.send_keys(min_value)

        time.sleep(3)
        apply_filter = self.find_element('xpath', '//*[@id="__layout"]/div/div[2]/div/div[1]/div[1]/div/div[2]/div/div[3]/div/button')
        apply_filter.click()

class Collect_data(Hostel):
    def get_data(self):
        current_time = datetime.now()
        time.sleep(5)
        property_elements = self.find_elements(By.CLASS_NAME, 'property-card')
        data_list = []

        for property_element in property_elements:
            property_info = {}

            property_info['name'] = self.try_except(property_element, 'property-name')
            property_info['rating'] = self.try_except(property_element, 'number')
            review_text = self.try_except(property_element, 'left-margin')
            if review_text:
                property_info['review'] = review_text.replace('(', '').replace(')', '')
            distance_text = self.try_except(property_element, 'distance-description')
            if distance_text:
                property_info['distance'] = distance_text.replace('- ', '')
            property_info['link'] = property_element.find_element(By.CLASS_NAME, 'nuxt-link').get_attribute("href")

            prices_divs = property_element.find_elements(By.CLASS_NAME, 'property-accommodation-prices')

            property_info['prices'] = {
                'dorms from': [],
                'privates from': []
            }

            for prices_div in prices_divs:
                price_divs = prices_div.find_elements(By.CLASS_NAME, 'property-accommodation-price')
                for price_div in price_divs:
                    try:
                        room_type_element = price_div.find_element(By.CLASS_NAME, "accommodation-label")
                        room_type = room_type_element.text.lower().strip()

                        price_element = price_div.find_element(By.CLASS_NAME, "current")
                        price = price_element.text

                        if room_type:
                            property_info['prices'][room_type].append(price)

                    except NoSuchElementException:
                        pass

            property_info['created_at'] = current_time.strftime('%Y-%m-%d %H:%M:%S')
            property_info['updated_at'] = current_time.strftime('%Y-%m-%d %H:%M:%S')

            data_list.append(property_info)

        return data_list

    def try_except(self, parent_element, class_name):
        try:
            return parent_element.find_element(By.CLASS_NAME, class_name).text
        except NoSuchElementException:
            return None

    def navigate_through_pages(self):
        current_page = 1
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        folder_name = "data"
        file_name = f'{timestamp}.json'
        data_writer = Data_Writer(folder_name, file_name)

        while True:
            data_list = self.get_data()
            print(f"Navigating to page {current_page}")
            data_writer.write(data_list)  # Write data collected from the current page

            next_page_button = self.find_element(By.CLASS_NAME, 'pagination-container')

            if not next_page_button:
                print("Next page button not found")
                break

            page_buttons = next_page_button.find_elements(By.CLASS_NAME, 'page-number')
            next_page_found = False

            for button in page_buttons:
                if button.text.strip() == str(current_page + 1):
                    self.execute_script("arguments[0].click();", button)
                    next_page_found = True
                    break

            if not next_page_found:
                print("No next page button found")
                break

            current_page += 1


class Data_Writer:
    def __init__(self, folder_name, filename):
        self.folder_name = folder_name
        self.filename = filename

        # Create the folder if it doesn't exist
        os.makedirs(self.folder_name, exist_ok=True)

    def _write_row(self, row):
        with open(os.path.join(self.folder_name, self.filename), "a") as f:
            f.write(row)

    def write(self, data_list):
        for data in data_list:
            self._write_row(json.dumps(data) + "\n")