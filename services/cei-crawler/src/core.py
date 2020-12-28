from constants import ImportStatus
from exceptions import LoginError
from goatcommons.utils import JsonUtils
from lessmium.webdriver import LessmiumDriver
from models import CEICrawRequest, CEICrawResult
from pages import LoginPage


class CEICrawlerCore:
    LOGIN_URL = "https://ceiapp.b3.com.br/CEI_Responsivo/login.aspx"

    def __init__(self):
        self.driver = LessmiumDriver()
        self.queue = None

    def craw_all_extract(self, request: CEICrawRequest):
        response = CEICrawResult(subject=request.subject, datetime=request.datetime)
        try:
            login_page = LoginPage(self.driver, request.credentials.tax_id, request.credentials.password)
            home_page = login_page.login()
            extract_page = home_page.go_to_extract_page()
            extract = extract_page.get_all_brokers_extract()
            response.status = ImportStatus.SUCCESS
        except Exception as e:
            response.status = ImportStatus.ERROR
            response.payload = JsonUtils.dump({"error_message": str(e)})
        self.queue.send(response)
