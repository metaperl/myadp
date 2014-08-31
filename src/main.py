#!/usr/bin/env python


from __future__ import print_function
import os
import sys
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

# system
from collections import defaultdict, Counter

from datetime import datetime, timedelta
from functools import wraps
import itertools
import pdb
import pprint
import random
import re
import sys
import time
import traceback

# pypi
import argh
from clint.textui import progress
import numpy
from splinter import Browser

from selenium.common.exceptions import TimeoutException, UnexpectedAlertPresentException
from selenium.webdriver.common.by import By
import selenium.webdriver.support.expected_conditions as EC
import selenium.webdriver.support.ui as ui

# local
import timer


random.seed()

pp = pprint.PrettyPrinter(indent=4)

base_url = 'http://www.myadvertisingpays.com/'

action_path = dict(
    login = "Dot_memberlogin.asp?referURL=Dot_MembersPage.asp",
    viewads = 'viewAds.asp'
)

one_minute    = 60
three_minutes = 3 * one_minute
ten_minutes   = 10 * one_minute
one_hour      = 3600


def url_for_action(action):
    return "{0}/{1}".format(base_url, action_path[action])

def loop_forever():
    while True: pass

def wait_visible(driver, locator, by=By.XPATH, timeout=30):
    try:
        return ui.WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((by, locator)))
    except TimeoutException:
        return False

class Entry(object):

    def __init__(
            self, username, password, second_password, browser, action
    ):
        self._username = username
        self._password = password
        self._second_password = second_password
        self.browser = browser
        self.action = action

    def login(self):
        print("Logging in...")

        self.browser.visit(url_for_action('login'))

        self.browser.find_by_name('username').type(self._username)
        self.browser.find_by_name('password').type(self._password)
        self.browser.find_by_value('Login').first.click()

        time.sleep(1)

        self.browser.find_by_name('password2').type(self._second_password)

        self.browser.find_by_value('Login').first.click()

    def view_ads(self):
        for i in xrange(1,11):
            while True:
                result = self.view_ad()
                if result == 0:
                    continue

    def view_ad(self):

        self.browser.visit(url_for_action('viewads'))
        time.sleep(random.randrange(2,15))

        try:
            buttons = self.browser.find_by_css('.text_button')
        except UnexpectedAlertPresentException:
            return 255


        #print("Found {0} buttons".format(buttons))

        buttons[0].click()

        self.solve_captcha()

        for i in progress.bar(range(40)):
            time.sleep(1)

        return 0

    def calc_time(self):

        time.sleep(3)

        elem = self.browser.find_by_xpath(
            '//table[@width="80%"]/tbody/tr/td[1]'
        )

        remaining = elem.text.split()
        print(remaining)

        indices = dict(
            hours=17,
            minutes=19
        )

        hours = int(remaining[indices['hours']])
        minutes = int(remaining[indices['minutes']])

        next_time  = datetime.now() + timedelta(
            hours=hours, minutes=minutes)

        print("Next time to click is {0}".format(
            next_time.strftime("%Y-%m-%d %H:%M")))

        loop_forever()

    def solve_captcha(self):
        time.sleep(3)
        elem = self.browser.find_by_xpath(
            "/html/body/form[@id='form1']/table/tbody/tr/td/table/tbody/tr[1]/td/font"
        )
        time.sleep(3)

        (x, y, captcha) = elem.text.split()

        print("CAPTCHA = {0}".format(captcha))

        self.browser.find_by_name('codeSb').fill(captcha)

        time.sleep(6)
        button = self.browser.find_by_name('Submit')
        button.click()

def main(username, password, second_password,random_delay=False,action='click'):

    if random_delay:
        random_delay = random.randint(1,15)
        print("Random delay = {0}".format(random_delay))
        time.sleep(one_minute * random_delay)


    with Browser() as browser:

        browser.driver.set_window_size(1200,1100)

        e = Entry(username, password, second_password, browser, action)

        e.login()

        if action == 'click':
            e.view_ads()
        if action == 'time':
            e.calc_time()

def conda_main():
    argh.dispatch_command(main)

if __name__ == '__main__':
    argh.dispatch_command(main)
