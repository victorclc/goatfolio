import math
import re
from time import sleep

import pandas as pd
from aws_lambda_powertools import Logger
from selenium.common.exceptions import (
    UnexpectedAlertPresentException,
    StaleElementReferenceException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from unidecode import unidecode

from exceptions import LoginError

logger = Logger()


class LoginPage(object):
    USERNAME_ELEM_ID = "ctl00_ContentPlaceHolder1_txtLogin"
    PASSWORD_ELEM_ID = "ctl00_ContentPlaceHolder1_txtSenha"
    SUBMIT_ELEM_ID = "ctl00$ContentPlaceHolder1$btnLogar"
    LOGIN_URL = "https://ceiapp.b3.com.br/CEI_Responsivo/login.aspx"

    def __init__(self, driver, username, password, logger=None):
        self.driver = driver
        self.username = username
        self.password = password

    def login(self):
        try:
            logger.info("Login START")
            self.driver.get(self.LOGIN_URL)
            self.driver.find_element_by_id(self.USERNAME_ELEM_ID).send_keys(
                self.username
            )
            self.driver.find_element_by_id(self.PASSWORD_ELEM_ID).send_keys(
                self.password
            )
            self.driver.find_element_by_name(self.SUBMIT_ELEM_ID).click()
            self._insecure_bypass()

            WebDriverWait(self.driver, 15).until(
                expected_conditions.visibility_of_element_located(
                    (By.ID, "objGrafPosiInv")
                )
            )

            logger.info("Login END")
            return HomePage(self.driver)
        except UnexpectedAlertPresentException as e:
            logger.error(f"Exception on Login: {str(e)}")
            raise LoginError(str(e))

    def _insecure_bypass(self):
        try:
            self.driver.find_element_by_id("exceptionDialogButton").click()
        except:
            pass


class HomePage(object):
    ASSETS_EXTRACT_PATH = "negociacao-de-ativos.aspx"
    ASSET_INQUIRY_PATH = "ConsultarCarteiraAtivos.aspx"

    def __init__(self, driver):
        self.driver = driver

    def go_to_extract_page(self):
        logger.info("Redirect to extract page START")
        self.driver.execute_script(
            "window.location.href = '" + self.ASSETS_EXTRACT_PATH + "'"
        )
        logger.info("Redirect to extract page END")
        return ExtractPage(self.driver)

    def go_to_asset_inquiry_page(self):
        logger.info("Redirect to asset inquiry page START")
        self.driver.execute_script(
            "window.location.href = '" + self.ASSET_INQUIRY_PATH + "'"
        )
        logger.info("Redirect to asset inquiry page END")
        return AssetInquiryPage(self.driver)


class ExtractPage(object):
    BROKERS_SELECTION_ID = "ctl00_ContentPlaceHolder1_ddlAgentes"
    INQUIRY_BUTTON_ID = "ctl00_ContentPlaceHolder1_btnConsultar"

    def __init__(self, driver):
        self.driver = driver

    def get_all_brokers_extract(self):
        logger.info("START Get all brokers extract")

        broker_selection_options = Select(
            self.driver.find_element_by_id(self.BROKERS_SELECTION_ID)
        ).options

        all_extracts = []
        for index, elem in enumerate(broker_selection_options[1:], 1):
            stock_brokers_selection = Select(
                self.driver.find_element_by_id(self.BROKERS_SELECTION_ID)
            )
            broker_name = stock_brokers_selection.options[index].text
            logger.info(f"Selecting {broker_name} broker")
            stock_brokers_selection.select_by_index(index)

            # WebDriverWait(self.driver, 30, ignored_exceptions=StaleElementReferenceException).until(
            #     expected_conditions.element_to_be_selected(
            #         Select(self.driver.find_element_by_id(self.BROKERS_SELECTION_ID)).options[index]
            #     ))
            sleep(3)
            inquire_button = self.driver.find_element_by_id(self.INQUIRY_BUTTON_ID)
            inquire_button.click()
            sleep(3)
            all_extracts = all_extracts + self._parse_broker_extract(broker_name)
            self.driver.refresh()
        logger.info("END Get all brokers extract")
        return all_extracts

    def _parse_broker_extract(self, broker_name):
        logger.info(f"Parsing extract of broker {broker_name}")
        tables = self.driver.find_elements_by_xpath("//table")
        if not tables:
            logger.info("No data")
            return []

        extract_table = tables[0]
        rows = extract_table.find_elements_by_tag_name("tr")

        if len(rows) <= 1:
            logger.info("Empty table")
            return []

        headers = [cell.text for cell in rows[0].find_elements_by_xpath("./*")]
        rows = [
            [cell.text for cell in row.find_elements_by_xpath("./*")]
            for row in rows[1:]
        ]

        result = []
        for row in rows:
            row_dict = {}
            for index, elem in enumerate(row):
                key = self._pythonfy_text(headers[index])
                row_dict[key] = unidecode(elem).replace(",", ".")
            row_dict["corretora"] = broker_name
            result.append(row_dict)

        return result

    @staticmethod
    def _pythonfy_text(text):
        new_text = text.replace("(R$)", "").strip()
        return re.sub(r"[ /]", "_", unidecode(new_text).lower())


class AssetInquiryPage(object):
    INQUIRY_BUTTON_ID = "ctl00_ContentPlaceHolder1_btnConsultar"

    def __init__(self, driver):
        self.driver = driver

    def get_assets_quantity(self):
        logger.info("START Get all brokers assets")

        inquire_button = self.driver.find_element_by_id(self.INQUIRY_BUTTON_ID)

        WebDriverWait(
            self.driver, 30, ignored_exceptions=StaleElementReferenceException
        ).until(
            expected_conditions.element_to_be_clickable((By.ID, self.INQUIRY_BUTTON_ID))
        )
        inquire_button.click()

        sleep(3)
        assets_qty = {}
        tables = pd.read_html(self.driver.page_source)
        logger.info(f"Found {len(tables)} tables.")
        logger.debug("ASSETS QUANTITY HTML: " + self.driver.page_source)
        for table in tables:
            logger.info(f"Table columns: {table.head}")
            for row in table.iterrows():
                if len(row[1]) < 6:
                    continue
                ticker = row[1][2]
                quantity = row[1][5]
                if type(ticker) == float and math.isnan(ticker) or math.isnan(quantity):
                    continue
                self._add_quantity(assets_qty, ticker, quantity)

        logger.info(f"END Get all brokers assets: {assets_qty}")
        return assets_qty

    @staticmethod
    def _add_quantity(asset_dict, ticker, quantity):
        if ticker in asset_dict:
            asset_dict[ticker] += quantity
        else:
            asset_dict[ticker] = quantity
