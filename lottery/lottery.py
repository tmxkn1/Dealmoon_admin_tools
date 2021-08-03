from enum import Enum
from typing import Union
from selenium.common.exceptions import ElementNotVisibleException, NoSuchElementException
from selenium.webdriver.remote.webelement import WebElement
from lib.autobrowser import *
import json

LOTTERY_URL = 'https://adm.dealmoon.co.uk/pages/index.html#/common-lottery/edit-lottery'
CLASS_NAME_PRIZE_TYPE = 'ant-select-item-option-content'

class PrizeType(Enum):
    EMPTY = 0
    GIFT_CARD = 1
    PHYSICAL_ITEM = 2
    GOLD = 3


class DMLottery:
    KEY_ADMIN_URL = "admin_url"
    KEY_USER_NAME = "user_name"
    KEY_PASSWORD = "password"
    def __init__(self):
        self._browser = browser_setup(headless_mode=False)

    @staticmethod
    def get_row_xpath(row_num):
        return f'//*[@data-row-key="{row_num}"]'

    def login(self):
        credentials = json.load(open("login_credentials.json"))
        self._browser.get(credentials[DMLottery.KEY_ADMIN_URL])
        self._browser.find_element_by_xpath(u'//*[@id="UK"]/div[1]/section/div/div/div/form/div[1]/input').send_keys(credentials[DMLottery.KEY_USER_NAME])
        self._browser.find_element_by_xpath(u'//*[@id="UK"]/div[1]/section/div/div/div/form/div[2]/input').send_keys(credentials[DMLottery.KEY_PASSWORD])
        self._browser.find_element_by_xpath(u'//*[@id="UK"]/div[1]/section/div/div/div/form/div[3]/input').click()

    def initiate_lottery(self):        
        self._browser.refresh()
        self._browser.get(LOTTERY_URL)
        wait_until_visible(self._browser, By.XPATH, DMLottery.get_row_xpath(1))

    def select_row(self, row_num):
        return LotteryDataRow(self._browser, row_num)


class LotteryDataRow:
    def __init__(self, browser:webdriver.Chrome, row_num:int):
        self._browser = browser
        self._row_num = row_num

    @property
    def element(self) -> WebElement:
        return self._browser.find_element_by_xpath(DMLottery.get_row_xpath(self._row_num))

    def config(self, prize_type:PrizeType=None, prize_quantity:Union[int,str]=None, gold_quantity:Union[int,str]=None):
        if prize_type:
            self.set_prize_type(prize_type)
            if gold_quantity is not None:
                time.sleep(0.2)
        if prize_quantity:
            self.set_prize_quantity(prize_quantity)
        if gold_quantity:
            self.set_gold_quantity(gold_quantity)

    def set_prize_quantity(self, quantity:Union[int,str]):
        ele = self.element.find_element_by_xpath('td[5]/div/div[2]/input')
        ele.send_keys(u'\ue009' + u'\ue003')
        ele.send_keys(quantity)

    def set_prize_type(self, prize_type:PrizeType):
        self.element.find_element_by_xpath('td[3]/div/div').click()
        self._browser.find_elements_by_xpath(f'//div[contains(@id,"rc_select_{self._row_num}_list")]/parent::div//div[contains(@class,"ant-select-item ant-select-item-option")]')[prize_type.value].click()

    def set_gold_quantity(self, quantity:Union[int,str]):
        try:
            self.element.find_element_by_class_name('ant-table-row-expand-icon-collapsed').click()
        except NoSuchElementException:
            pass
        except ElementNotVisibleException:
            pass
        self._browser.execute_script("""return arguments[0].nextElementSibling""", self.element).find_element_by_tag_name('input').send_keys(quantity)

        