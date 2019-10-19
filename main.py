import requests
import json
from time import sleep
from bs4 import BeautifulSoup as bs
from random import randint, choice
from faker import Faker
import string
import sys
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import os
import zipfile
from hyper.contrib import HTTP20Adapter
import re
import untangle
from sensor import Sensor
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
import ssl
import uuid

class MyAdapter(HTTPAdapter):
	def init_poolmanager(self, connections, maxsize, block=False):
		self.poolmanager = PoolManager(num_pools=connections,
			maxsize=maxsize,
			block=block,
			ssl_version=ssl.PROTOCOL_TLSv1_1)

from utils import Logger

logger = Logger()
faker = Faker()

class Nike():

	def __init__(self):
		with open('config.json') as file:
			self.config = json.load(file)
			file.close()
		if self.config['password']['random']:
			self.password = None
		else:
			self.password = self.config['password']['fixed']
		self.generator = Sensor()

	def __get_session(self, proxy):
		s = requests.Session()
		s.mount('https://', MyAdapter())
		sData = self.generator.generateSensorData()
		payload = {'sensor_data': sData}
		s.post('https://www.nike.com/_bm/_data', json=payload)
		self.generator.cookie = s.cookies['_abck']
		sData = self.generator.generatesensordata1()
		payload = {'sensor_data': sData}
		s.post('https://www.nike.com/_bm/_data', json=payload)
		s.headers.update({"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36","Accept":"*/*","Accept-Encoding":"gzip, deflate, br","Accept-Language":"en-US,en;q=0.9,ms;q=0.8"})
		s.cookies["CONSUMERCHOICE"]="gb/en_gb"
		s.cookies["NIKE_COMMERCE_COUNTRY"]="GB"
		s.cookies["NIKE_COMMERCE_LANG_LOCALE"]="en_GB"
		s.cookies["nike_locale"]="gb/en_gb"
		return s

	def create_account(self, proxy):
		s = self.__get_session(proxy)
		genders = ["M", "F"]
		gender = choice(genders)
		while True:
			name = faker.name()
			if "." not in name.split()[0]:
				break
			else:
				pass
		emailChoices = []
		emailChoices.append("{}{}{}@{}".format(name.split()[0], name.split()[1], randint(11,9999), self.config['domain']))
		emailChoices.append("{}{}{}@{}".format(name.split()[0][0], name.split()[1], randint(11,9999), self.config['domain']))
		if self.config['domain'] != "gmail.com":
			emailChoices.append("{}{}@{}".format(name.split()[0], randint(111,999), self.config['domain']))
		email = choice(emailChoices)
		if not self.password:
			allchar = string.ascii_letters + string.digits
			while True:
				password = "".join(choice(allchar) for x in range(randint(8, 12)))
				if any(i.isdigit() for i in password) and any(i.isupper() for i in password) and any(i.islower() for i in password):
					break
				else:
					continue
		else:
			password = self.password
		payload = {
			'account': {
				'email': email.lower(),
				'passwordSettings': {
					'password': password,
					'passwordConfirm': password
				}
			},
			'locale': '{}_{}'.format(self.config['language'], self.config['locale']),
			'welcomeEmailTemplate': 'TSD_PROF_COMM_WELCOME_V1.0',
			'registrationSiteId': 'snkrsweb',
			'username': email.lower(),
			'firstName': name.split()[0],
			'lastName': name.split()[1],
			'dateOfBirth': "{}-{}-{}".format(randint(1979,1996), randint(10,12), randint(10,28)),
			'country': self.config['locale'],
			'gender': gender,
			'receiveEmail': True,
			'emailAddress': email.lower(),
			'password': password
		}
		params = {
			'appVersion': '440',
			'experienceVersion': '369',
			'uxid': 'com.nike.commerce.snkrs.web',
			'locale': '{}_{}'.format(self.config['language'], self.config['locale']),
			'backendEnvironment': 'identity',
			'browser': 'Google Inc.',
			'os': 'undefined',
			'mobile': 'false',
			'native': 'false',
			'visitor': uuid.uuid4(),
			'visit': '1',
			'language': '{}-{}'.format(self.config['language'], self.config['locale'])
		}
		r = s.post("https://unite.nike.com/access/users/v1", json=payload, params=params, proxies=proxy)
		print(r.text)
		if r.status_code == 201:
			return True, email, password
		else:
			return False, email, password

	def account_login(self, email, password, proxy):
		s = self.__get_session(proxy)
		payload = {
			'client_id': 'PbCREuPr3iaFANEDjtiEzXooFl7mXGQ7',
			'grant_type': 'password',
			'password': password,
			'username': email,
			'ux_id': 'com.nike.commerce.snkrs.web'
		}
		params = {
			'appVersion': '440',
			'experienceVersion': '369',
			'uxid': 'com.nike.commerce.snkrs.web',
			'locale': '{}_{}'.format(self.config['language'], self.config['locale']),
			'backendEnvironment': 'identity',
			'browser': 'Google Inc.',
			'os': 'undefined',
			'mobile': 'false',
			'native': 'false',
			'visitor': uuid.uuid4(),
			'visit': '1',
			'language': '{}-{}'.format(self.config['language'], self.config['locale'])
		}
		r = s.post("https://unite.nike.com/login", json=payload, params=params, proxies=proxy)
		try:
			data = r.json()
			return True, data['access_token']
		except:
			return False, None

	def request_sms(self, number, accessToken, proxy):
		s = self.__get_session(proxy)
		params = {
			'appVersion': '440',
			'experienceVersion': '369',
			'uxid': 'com.nike.commerce.snkrs.web',
			'locale': '{}_{}'.format(self.config['language'], self.config['locale']),
			'backendEnvironment': 'identity',
			'browser': 'Google Inc.',
			'os': 'undefined',
			'mobile': 'false',
			'native': 'false',
			'visit': '1',
			'visitor': uuid.uuid4(),
			'phone': number,
			'language': '{}-{}'.format(self.config['language'], self.config['locale']),
			'country': self.config['locale']
		}
		s.headers['authorization'] = 'Bearer {}'.format(accessToken)
		r = s.post('https://unite.nike.com/sendCode', params=params, json={}, proxies=proxy)
		if r.status_code == 202:
			return True
		else:
			return False

	def verify_code(self, code, accessToken, proxy):
		s = self.__get_session(proxy)
		params = {
			'appVersion': '440',
			'experienceVersion': '369',
			'uxid': 'com.nike.commerce.snkrs.web',
			'locale': '{}_{}'.format(self.config['language'], self.config['locale']),
			'backendEnvironment': 'identity',
			'browser': 'Google Inc.',
			'os': 'undefined',
			'mobile': 'false',
			'native': 'false',
			'visit': '1',
			'visitor': uuid.uuid4(),
			'code': code,
			'language': '{}-{}'.format(self.config['language'], self.config['locale'])
		}
		s.headers['authorization'] = 'Bearer {}'.format(accessToken)
		r = s.post("https://unite.nike.com/verifyCode", params=params, json={}, proxies=proxy)
		if r.status_code == 200:
			return True
		else:
			return False

	def check_verification(self, accessToken, proxy):
		s = self.__get_session(proxy)
		params = {
			'appVersion': '440',
			'experienceVersion': '369',
			'uxid': 'com.nike.commerce.snkrs.web',
			'locale': '{}_{}'.format(self.config['language'], self.config['locale']),
			'backendEnvironment': 'identity',
			'browser': 'Google Inc.',
			'os': 'undefined',
			'mobile': 'false',
			'native': 'false',
			'visit': '1',
			'visitor': uuid.uuid4(),
			'viewId': 'commerce',
			'language': '{}-{}'.format(self.config['language'], self.config['locale'])
		}
		s.headers['authorization'] = 'Bearer {}'.format(accessToken)
		r = s.get('https://unite.nike.com/getUserService', params=params, proxies=proxy)
		try:
			data = r.json()
			if data['verifiedphone']:
				return True
			else:
				return False
		except:
			return False

	def __get_driver(self):
		chrome_options = Options()
		# pluginfile = 'proxy_auth_plugin.zip'
		# with zipfile.ZipFile(pluginfile, 'w') as zp:
		# 	zp.writestr("manifest.json", manifest_json)
		# 	zp.writestr("background.js", background_js)
		# chrome_options.add_extension(pluginfile)
		chrome_options.add_argument("--start-maximized")
		prefs = {"profile.managed_default_content_settings.images":2}
		chrome_options.add_experimental_option("prefs", prefs)
		driver = webdriver.Chrome(executable_path='C:\\Users\\Ryan\\Documents\\YEEZUS\\9 - CartChefs Nike\\Account Generator\\chromedriver.exe', chrome_options=chrome_options)
		return driver

	def create_account_sel(self, number, proxy):
		driver = self.__get_driver()
		driver.get("https://www.nike.com/gb/launch/")
		while True:
			name = faker.name()
			if "." not in name.split()[0]:
				break
			else:
				pass
		emailChoices = []
		emailChoices.append("{}{}{}@{}".format(name.split()[0], name.split()[1], randint(11,9999), self.config['domain']))
		emailChoices.append("{}{}{}@{}".format(name.split()[0][0], name.split()[1], randint(11,9999), self.config['domain']))
		if self.config['domain'] != "gmail.com":
			emailChoices.append("{}{}@{}".format(name.split()[0], randint(111,999), self.config['domain']))
		email = choice(emailChoices)
		if not self.password:
			allchar = string.ascii_letters + string.digits
			while True:
				password = "".join(choice(allchar) for x in range(randint(8, 12)))
				if any(i.isdigit() for i in password):
					break
				else:
					continue
		else:
			password = self.password
		# print("{}:{}".format(email, password))
		sleep(2)
		driver.find_element_by_xpath("//*[contains(text(), 'Yes, I Accept')]").click()
		sleep(1)
		driver.find_element_by_xpath("//a[@aria-label='Join or Log In']").click()
		driver.find_element_by_xpath("//*[contains(text(), 'Join now.')]").click()
		driver.find_element_by_name('emailAddress').send_keys(email)
		driver.find_element_by_name('password').send_keys(password)
		driver.find_element_by_name('firstName').send_keys(name.split()[0])
		driver.find_element_by_name('lastName').send_keys(name.split()[1])
		driver.find_element_by_name('dateOfBirth').send_keys("{}{}{}".format(randint(10,28), randint(10,12), randint(1979,1996)))
		driver.find_element_by_xpath("//*[contains(text(), 'Male')]").click()
		driver.find_element_by_xpath("//input[@value='CREATE ACCOUNT']").click()
		sleep(5)
		driver.find_element_by_xpath("//input[@placeholder='Mobile Number']").send_keys(number)
		driver.find_element_by_xpath("//input[@value='Send Code']").click()
		return True, email, password, driver

	def submit_code_sel(self, driver, code, proxy):
		driver.find_element_by_xpath("//input[@placeholder='Enter Code']").send_keys(code)
		driver.find_element_by_xpath("//input[@value='CONTINUE']").click()
		sleep(5)
		driver.close()
		return True

class Dongle():

	def __init__(self):
		self.URL = "192.168.8.1"
		self.smsView = "http://192.168.8.1/html/smsinbox.html"
		self.smsEndpoint = "/api/sms/sms-list"
		self.s = requests.Session()

	def __extract_code(self, content):
		return content[-6:]
		
	def __get_auth(self):
		try:
			r = requests.get(self.smsView, timeout=1)
		except:
			# logger.error("Failed getting SIM reader authentication cookies.")
			return None, None
		Setcookie = r.headers.get('set-cookie')
		sessionID = Setcookie.split(';')[0]
		token = re.findall(r'"([^"]*)"', r.text)[2]
		return sessionID, token

	def __delete_sms(self, index):
		sessionID, token = self.__get_auth()
		headers = {
			'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
			'__RequestVerificationToken': token,
			'Cookie': sessionID
		}
		data = '<?xml version="1.0" encoding="UTF-8"?><request><Index>{}</Index></request>'.format(index)
		r = requests.post("http://{}/api/sms/delete-sms".format(self.URL), data=data, headers=headers, timeout=1)

	def get_number(self):
		sessionID, token = self.__get_auth()
		headers = {
			'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
			'__RequestVerificationToken': token,
			'Cookie': sessionID
		}
		try:
			r = requests.get('http://{}/api/device/information'.format(self.URL), headers=headers, timeout=1)
			obj = untangle.parse(r.text)
			number = obj.response.Msisdn.cdata
			number = str(number).split('+44')[1]
			return True, number
		except:
			return False, None

	def get_code(self):
		sessionID, token = self.__get_auth()
		headers = {
			'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
			'__RequestVerificationToken': token,
			'Cookie': sessionID
		}
		data = '<request><PageIndex>1</PageIndex><ReadCount>20</ReadCount><BoxType>1</BoxType><SortType>0</SortType><Ascending>0</Ascending><UnreadPreferred>0</UnreadPreferred></request>'
		r = requests.post("http://{}{}".format(self.URL, self.smsEndpoint), data=data, headers=headers, timeout=1)
		obj = untangle.parse(r.text)
		if int(obj.response.Count.cdata) > 0:
			for message in obj.response.Messages.Message:
				if "Nike" in message.Content.cdata:
					code = self.__extract_code(message.Content.cdata)
					self.__delete_sms(message.Index.cdata)
					return True, code
				else:
					continue
			return False, None
		else:
			return False, None

proxies = None

if __name__ == '__main__':
	logger.log("CartChefs Nike || Manual Account Generator v2.0")
	nike = Nike()
	dongle = Dongle()
	num = input("#: ")
	for x in range(int(num)):
		logger.log("Waiting for response from SIM reader...")
		success = False
		while not success:
			success, number = dongle.get_number()
		logger.log("Using +44{} from SIM reader.".format(number))
		success = False
		while not success:
			success, email, password = nike.create_account(proxy=proxies)
			if success:
				logger.log("Created nike account ({}:{}).".format(email, password))
			else:
				logger.error("Failed creating nike account ({}:{}).".format(email, password))
		success = False
		while not success:
			success, accessToken = nike.account_login(email, password, proxy=proxies)
			if success:
				logger.log("Logged into account ({}).".format(email))
			else:
				logger.error("Failed logging into account ({}).".format(email))
		success = False
		while not success:
			success = nike.request_sms("44{}".format(number), accessToken, proxy=proxies)
			if success:
				logger.log("Requested verification code from Nike ({}).".format(email))
			else:
				logger.log("Failed requesting verification code ({}).".format(email))
		success = False
		sleep(10)
		count = 0
		miniCount = 0
		while not success and count < 20:
			if miniCount == 6:
				nike.request_sms("44{}".format(number), accessToken, proxy=proxies)
				miniCount = 0
			success, code = dongle.get_code()
			if success:
				logger.log("Got verification code {} from SIM reader ({}).".format(code, email))
			else:
				sleep(5)
				count += 1
				miniCount += 1
		if not success:
			logger.status("*USER INPUT REQUIRED* - restart modem ({}).".format(email))
			break
		success = False
		while not success:
			success = nike.verify_code(code, accessToken, proxy=proxies)
			if success:
				logger.log("Submitted verification code to Nike ({}).".format(email))
			else:
				logger.log("Failed submitting verification code ({}).".format(email))
		success = False
		while not success:
			success = nike.check_verification(accessToken, proxy=proxies)
			if success:
				logger.success("Created and verified account: {}".format(email))
				with open('accounts.txt', 'a') as file:
					file.write("\n{}:{}".format(email, password))
					file.close()
			else:
				logger.error("Error verifying account: {}".format(email))
		input("Press to continue...")