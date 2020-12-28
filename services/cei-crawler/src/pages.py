import logging
import re
from time import sleep

from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from unidecode import unidecode

from exceptions import LoginError


class LoginPage(object):
    USERNAME_ELEM_ID = 'ctl00_ContentPlaceHolder1_txtLogin'
    PASSWORD_ELEM_ID = 'ctl00_ContentPlaceHolder1_txtSenha'
    SUBMIT_ELEM_ID = 'ctl00$ContentPlaceHolder1$btnLogar'
    LOGIN_URL = "https://cei.b3.com.br/CEI_Responsivo/"
    LOGGER = logging.getLogger()

    def __init__(self, driver, username, password, logger=None):
        self.driver = driver
        self.username = username
        self.password = password

    def login(self):
        try:
            self.LOGGER.info('Login START')
            self.driver.find_element_by_id(self.USERNAME_ELEM_ID).send_keys(self.username)
            self.driver.find_element_by_id(self.PASSWORD_ELEM_ID).send_keys(self.password)
            self.driver.find_element_by_name(self.SUBMIT_ELEM_ID).click()
            self._insecure_bypass()

            WebDriverWait(self.driver, 15).until(
                expected_conditions.visibility_of_element_located((By.ID, 'objGrafPosiInv')))

            self.LOGGER.info('Login END')
            return HomePage(self.driver)
        except UnexpectedAlertPresentException as e:
            self.LOGGER.error(f'Exception on Login: {str(e)}')
            raise LoginError(str(e))

    def _insecure_bypass(self):
        try:
            self.driver.find_element_by_id("exceptionDialogButton").click()
        except:
            pass


class HomePage(object):
    ASSETS_EXTRACT_PATH = 'negociacao-de-ativos.aspx'
    LOGGER = logging.getLogger()

    def __init__(self, driver):
        self.driver = driver

    def go_to_extract_page(self):
        self.LOGGER.info('Redirect to extract page START')
        self.driver.execute_script("window.location.href = '" + self.ASSETS_EXTRACT_PATH + "'")
        self.LOGGER.info('Redirect to extract page END')
        return ExtractPage(self.driver)


class ExtractPage(object):
    LOGGER = logging.getLogger()
    BROKERS_SELECTION_ID = 'ctl00_ContentPlaceHolder1_ddlAgentes'
    INQUIRY_BUTTON_ID = 'ctl00_ContentPlaceHolder1_btnConsultar'

    def __init__(self, driver):
        self.driver = driver

    def get_all_brokers_extract(self):
        self.LOGGER.info('START Get all brokers extract')

        broker_selection_options = Select(
            self.driver.find_element_by_id(self.BROKERS_SELECTION_ID)).options

        all_extracts = []
        for index, elem in enumerate(broker_selection_options[1:], 1):
            stock_brokers_selection = Select(self.driver.find_element_by_id(self.BROKERS_SELECTION_ID))
            broker_name = stock_brokers_selection.options[index].text
            self.LOGGER.info(f'Selecting {broker_name} broker')
            stock_brokers_selection.select_by_index(index)
            WebDriverWait(self.driver, 10).until(
                expected_conditions.element_to_be_selected(
                    stock_brokers_selection.options[index]
                ))
            sleep(1)
            inquire_button = self.driver.find_element_by_id(self.INQUIRY_BUTTON_ID)
            inquire_button.click()
            sleep(3)
            all_extracts = all_extracts + self._parse_broker_extract(broker_name)
            self.driver.refresh()
        self.LOGGER.info('END Get all brokers extract')
        return all_extracts

    def _parse_broker_extract(self, broker_name):
        self.LOGGER.info(f'Parsing extract of broker {broker_name}')
        tables = self.driver.find_elements_by_xpath("//table")
        if not tables:
            self.LOGGER.info('No data')
            return []

        extract_table = tables[0]
        rows = extract_table.find_elements_by_tag_name('tr')

        if len(rows) <= 1:
            self.LOGGER.info('Empty table')
            return []

        headers = [cell.text for cell in rows[0].find_elements_by_xpath('./*')]
        rows = [[cell.text for cell in row.find_elements_by_xpath('./*')] for row in rows[1:]]

        result = []
        for row in rows:
            row_dict = {}
            for index, elem in enumerate(row):
                key = self._pythonfy_text(headers[index])
                row_dict[key] = unidecode(elem).replace(',', '.')
            row_dict['corretora'] = broker_name
            result.append(row_dict)

        return result

    @staticmethod
    def _pythonfy_text(text):
        new_text = text.replace('(R$)', '').strip()
        return re.sub(r'[ /]', "_", unidecode(new_text).lower())
