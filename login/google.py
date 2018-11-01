#author: johnxguo
#date: 2018-10-31

import os
from .state import LoginState
from selenium import webdriver 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class GoogleLoginHelper:
    def __init__(self, uid:str, password:str):
        self.signin_url = 'https://accounts.google.com/signin/v2/identifier?&flowName=GlifWebSignIn&flowEntry=ServiceLogin&cid=1&navigationDirection=forward'
        self.state = LoginState.logout
        self.waitDomTimeout = 10
        self.waitDomFrq = 0.2
        self.setUserInfo(uid, password)
        print("create webdriver")
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--log-level=3')
        chrome_options.add_argument('user-agent="Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"')
        chromedriver = r'C:\Chrome\Application\chromedriver.exe'
        os.environ["webdriver.chrome.driver"] = chromedriver
        self.driver = webdriver.Chrome(chromedriver, chrome_options=chrome_options)

    def __del__(self):
        self.driver.close()
        self.driver = None
        print("close webdriver")

    def setUserInfo(self, uid:str, password:str):
        self.uid = uid
        self.password = password
    
    def login(self):
        if not self.driver:
            self.state = LoginState.logout
            return self
        try:
            self.state = LoginState.login_process
            print("begin login google..")
            self.driver.get(self.signin_url)
            #self.driver.get_screenshot_as_file("./google-accounts-page.png")
            self.driver.find_element_by_name('identifier').send_keys(self.uid)
            print("fill in username:" + self.uid)
            self.driver.find_element_by_id('identifierNext').click()
            print("submit username, waitting password ready")
            WebDriverWait(self.driver, self.waitDomTimeout, self.waitDomFrq).until(
                EC.element_to_be_clickable((By.NAME, "password"))
            )
            print("fill in password")
            self.driver.find_element_by_name('password').send_keys(self.password)
            print("waitting submit btn ready")
            WebDriverWait(self.driver, self.waitDomTimeout, self.waitDomFrq).until(
                EC.element_to_be_clickable((By.ID, "passwordNext"))
            )
            self.driver.find_element_by_id('passwordNext').click()
            print("submit login... , waitting response")
            WebDriverWait(self.driver, self.waitDomTimeout, self.waitDomFrq).until(self.isLoginComplete)
            self.state = LoginState.login_succ
            print("google login succ!")
        except:
            self.state = LoginState.login_fail
            print("google login fail!")
        return self

    def isLoginOk(self):
        return self.state == LoginState.login_succ

    def getCookie(self):
        if not self.isLoginOk():
            return None
        co = self.driver.get_cookies()
        names = []
        values = []
        for cookie in co:
            names.append(cookie['name'])
            values.append(cookie['value'])
        cookies = dict(zip(names, values))
        return cookies

    def turnTo(self, url:str):
        if url:
            print('turn to ' + url)
            self.driver.get(url)

    def isLoginComplete(self, a):
        if not self.driver:
            return False
        domains = self.driver.get_cookies()
        for domain in domains:
            if domain['domain'] == '.google.com' and \
               domain['name'] == 'SSID':
                return True
        return False
