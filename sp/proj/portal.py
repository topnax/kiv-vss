import requests
import datetime


LOGIN_URL = "/login"
DEVICE_URL = "/terminal-edit?selectedId={selected_id}"
NEW_DEVICE_URL = "/device-edit?parentId={parent_id}"
ACTIVATE_URL = "/api/device/activate"
DEACTIVATE_URL = "/api/device/deactivate"


class DotypayPortal:
    
    def __init__(self, browser, base_url, username, password):
        self.browser = browser
        self.base_url = base_url
        self.username = username
        self.password = password
        self.page = browser.new_page()

    def get_endpoint(self, endpoint):
        return self.base_url + endpoint

    def activate_devices(self, start, end):
        api_keys = []
        self.login()
        failed = 0
        attempt = 0
        self.current_device_id = start
        for device_id in range(start, end + 1):
            attempt += 1
            try:
                self.go_to_device(device_id) 
                api_key = self.load_device_api_key() 
                api_keys.append((self.get_name(), api_key))
            except AssertionError as msg:
                print(msg)
                print(f"Failed to load API key for #{device_id}")
            except:
                print(f"Failed to load API key for unknown reasons for #{device_id}")

        return api_keys

    def login(self):
        self.page.goto(self.get_endpoint(LOGIN_URL))
        self.page.fill('#username', self.username)
        self.page.fill('#password', self.password)
        self.page.dispatch_event("#login-submit", "click") 
        assert self.page.title() == "Dashboard"

    def go_to_device(self, device_id):
        self.page.goto(self.get_endpoint(DEVICE_URL.format(selected_id=device_id)))
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
        return requests.post(self.get_endpoint(ACTIVATE_URL), json={
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
    
    def go_to_new_device_page(self, parent_id):
        self.page.goto(self.get_endpoint(NEW_DEVICE_URL.format(parent_id=parent_id)))
        assert self.page.title() == "Vytváření zařízení"

    def create_new_device(self, identifier):
        assert self.page.title() == "Vytváření zařízení"
        self.page.fill('#name', identifier)
        self.page.fill('#serialNumber', identifier)
        self.page.click('#submitButton')
        assert self.page.title() == "Zařízení úspěšně vytvořené"

    def create_new_devices(self, n, parent_id):
        self.login()
        timestamp = datetime.datetime.now().strftime("%d-%m-%Y-%S")
        for i in range(n):
            self.go_to_new_device_page(parent_id)
            identifier = f"{timestamp}-{i}"
            self.create_new_device(identifier)
            print("created new device", identifier)

