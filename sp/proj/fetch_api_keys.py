from playwright.sync_api import sync_playwright
import sys
import requests


BASE_URL = "https://pytlak.eu-central-1.elasticbeanstalk.com"
LOGIN_URL = BASE_URL + "/login"
DEVICE_URL = BASE_URL + "/terminal-edit?selectedId={selected_id}"
ACTIVATE_URL = BASE_URL + "/api/device/activate"
DEACTIVATE_URL = BASE_URL + "/api/device/deactivate"


class DotypayPortal:
    
    def __init__(self, browser, username, password):
        self.browser = browser
        self.username = username
        self.password = password
        self.page = browser.new_page()

    def get_api_keys(self, start, end):
        api_keys = []
        self.login()
        failed = 0
        attempt = 0
        self.current_device_id = start
        for device_id in range(start, end):
            attempt += 1
            try:
                self.go_to_device(device_id) 
                api_key = self.load_device_api_key() 
                api_keys.append((self.get_name(), api_key))
                print(f"loaded api key for device #{device_id} : {api_key}")
            except AssertionError as msg:
                print(msg)
                print(f"Failed to load API key for #{device_id}")
            except:
                print(f"Failed to load API key for unknown reasons for #{device_id}")

        return api_keys

    def login(self):
        print("1")
        self.page.goto(LOGIN_URL)
        print("2")
        self.page.fill('#username', self.username)
        print("3")
        self.page.fill('#password', self.password)
        print("4")
        self.page.dispatch_event("#login-submit", "click") 
        print("5")
        assert self.page.title() == "Dashboard"

    def go_to_device(self, device_id):
        self.page.goto(DEVICE_URL.format(selected_id=device_id))
        assert self.page.title() == "Nastavení zařízení"

    def load_device_api_key(self):
        if self.is_device_activated():
            self.deactivate_device()    

        if self.is_device_deactivated():
            self.activate_device()

        assert self.is_device_to_be_activated()
        response = self.finish_device_activation().json()
        assert "data" in response
        assert "apiToken" in response["data"]
        return response["data"]["apiToken"]

    def is_device_activated(self):
        return self.page.locator('text=Zařízení je aktivováno').count() > 0

    def is_device_deactivated(self):
         return self.page.locator('text=Zařízení je deaktivováno').count() > 0

    def is_device_to_be_activated(self):
         return self.page.locator('text=Zařízení ještě není aktivováno').count() > 0

    def finish_device_activation(self):
        return requests.post(ACTIVATE_URL, json={
            "businessId": self.get_business_id(),
            "model": self.get_model(),
            "pin": self.get_device_pin(),
            "sn": self.get_serial_number()
        })

    def deactivate_device(self):
        self.page.click("text=Deaktivovat")

    def activate_device(self):
        return self.page.click("text=Reaktivovat") 
        
    def get_device_pin(self):
        return self.page.input_value("#pin") 

    def get_business_id(self):
        return self.page.input_value("#companyBusinessId") 

    def get_serial_number(self):
        return self.page.input_value("#serialNumber") 

    def get_model(self):
        return self.page.input_value("#modelName") 

    def get_name(self):
        return self.page.input_value("#name") 
    

def get_api_keys(username, password, start, end):

    with sync_playwright() as p:
        # initialize a browser and the Portal wrapper
        browser = p.chromium.launch()
        portal = DotypayPortal(browser, username, password)

        # get API keys for identifiers within the given interval
        # all devices within the interval will be activated
        keys = portal.get_api_keys(start, end)

        # print keys to stdout
        for (name, key) in keys:
            print(f"{name};{key}")

        browser.close()


if __name__ == "__main__":
   get_api_keys(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]) 
