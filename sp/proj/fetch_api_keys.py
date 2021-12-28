from playwright.sync_api import sync_playwright
import sys
import requests

BASE_URL = "https://pytlak.eu-central-1.elasticbeanstalk.com"
LOGIN_URL = BASE_URL + "/login"
DEVICE_URL = BASE_URL + "/terminal-edit?selectedId={selected_id}"
ACTIVATE_URL = BASE_URL + "/api/device/activate"


class DotypayPortal:
    
    def __init__(self, browser, username, password):
        self.browser = browser
        self.username = username
        self.password = password
        self.current_device_id = 0
        self.page = browser.new_page()

    def get_api_keys(self, n):
        api_keys = []
        self.login()
        while len(api_keys) < n:
            self.go_to_next_device() 
            response = self.load_device_api_key() 
            jjjjjjjjj
    

    def login(self, n):
        page.fill('#username', self.username)
        page.fill('#password', self.password)
        page.click(".loginButton") 

    def go_to_next_device(self):
        self.current_device_id += 1
        self.page.goto(DEVICE_URL.format(selected_id=self.current_device_id))
        assert self.page.title() == "Nastavení zařízení"

    def load_device_api_key(self):
        if not is_device_activated():
            activate_device()    

        response = finish_device_api_key().json()
        assert "data" in response
        assert "apiToken" in resposne["data"]
        return response["data"]["apiToken"]

    def is_device_activated(self):
        return self.page.locator('text=Zařízení ještě není aktivováné')

    def finish_device_activation(self):
        return requests.post(ACTIVATE_URL, json={
            "businessId": self.get_device_pin(),
            "model": self.get_model(),
            "pin": self.get_device_pin(),
            "sn": self.get_serial_number()
        }

    def activate_device(self):
        return self.click("text=Reaktivovat") 
        
    def get_device_pin(self):
        return self.page.input_value("#pin") 

    def get_business_id(self):
        return self.page.input_value("#companyBusinessId") 

    def get_serial_number(self):
        return self.page.input_value("#serialNumber") 

    def get_model(self):
        return self.page.input_value("#modelName") 

    

def get_api_keys(username, password):
    login()
    
    n
    go_to_terminal_list()

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(LOGIN_URL)
        print(page.title())
        browser.close()


if __name__ == "__main__":
   get_api_keys(sys.argv[1], sys.argv[2]) 
