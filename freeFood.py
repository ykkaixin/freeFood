from selenium import webdriver
from bs4 import BeautifulSoup
import time
import re
from uuid import uuid1
from datetime import date, datetime, time, timedelta, timezone
import calendar
from icalendar import Calendar, Event
from selenium.webdriver.chrome.options import Options
import oss

last_path = os.path.abspath('..')
print(last_path)
driver_path = last_path + '/freeFood/chromedriver'
print(driver_path)
chrome_options=Options()
chrome_options.add_argument('--headless')
driver = webdriver.Chrome(executable_path=driver_path,options=chrome_options)
driver.get("https://www.binghamton.edu/apps/calendar/event/index?range=month")

# search key word
# food, pizza 
url =''

class ProcessWeb:
    # location time  
    location = []
    day = []
    content = []
    title = []
    time = []
    url = ''
    newlist = []

    def __init__(self, url, driver):
        super().__init__()
        self.url = url
        self.driver = driver
        self.cal = Calendar()
        self.cal['version'] = '2.0'
        self.cal['prodid'] = '-//CQUT//Syllabus//EN'

    
# this the event search accroding the key word
# key word
# <input type="search" id="q" 
#                     name="keyword" 
#                     value="" 
#                     placeholder="Search:">
#
    def start(self):
        input = driver.find_element_by_id('q')
        try:
            input.send_keys(self.url)
            print('Tool start')
        except Exception as e:
            print('fail')
        self.click_searchButton()
        self.click_event()
# search button
# <input type="submit" id="search_submit" 
#                      name="search_submit" 
#                      value="Search" class="button">
    def click_searchButton(self):
        button = driver.find_element_by_id('search_submit')
        try:
            button.click()
            print('continue')
        except Exception as e:
            print('fail')

# click the event 
# get all the href from the html and get
# <div class="evTitle">ASU Movie Night: "The Farewell"</div>
# "//form[@id='loginForm']/input[1]"

# get source page and filter to get href
    def click_event(self):
        soup_result = BeautifulSoup(driver.page_source,'html.parser')
        aTag = soup_result.find_all("a")
        href_list = []
        pre = "https://www.binghamton.edu"
        for t2 in aTag:
            t3 = t2.get('href')
            if 'details' in t3:
                href_list.append(pre + t3)

        for href in href_list:
            driver.get(href)

            locationE = driver.find_element_by_class_name('evLocation')
            timeE = driver.find_element_by_class_name('evTime')
            dateE = driver.find_element_by_class_name('evDate')
            titleE = driver.find_element_by_xpath("//div[@class='event-details']/h1")
            contentE = driver.find_element_by_xpath("//div[@class='event-details']/p")

            self.location.append(locationE.get_attribute('textContent'))
            self.time.append(timeE.get_attribute('textContent'))
            self.day.append(dateE.get_attribute('textContent'))
            #str1 = titleE.get_attribute('textContent')
            self.title.append(titleE.get_attribute('textContent'))
            #upper_url = self.url.upper()
            #self.title.append(upper_url + ":" + str1)
            self.content.append(contentE.get_attribute('textContent'))

            driver.back()

    def time_trans(self, timing):
        #timing = timing.strip()
        timelist = re.split(' |:', timing)
        timelist[0] = int(timelist[0])
        timelist[1] = int(timelist[1])
        timelist[-3] = int(timelist[-3])
        timelist[-2] = int(timelist[-2])
        if timelist[2] == 'PM' and timelist[0] != 12:
            timelist[0] = timelist[0] + 12
        if timelist[-1] == 'PM' and timelist[0] != 12:
            timelist[-3] = timelist[-3] + 12
        return timelist
    def day_trans(self, day):
        daylist = re.split(' |, ', day)
        daylist[1] = list(calendar.month_name).index(daylist[1])
        daylist[2] = int(daylist[2])
        return daylist

    def to_ics(self, outstr):
        for li in self.newlist:
            event = Event()
            # 添加事件
            event.add('uid', str(uuid1()) + '@CQUT')
            event.add('summary', outstr.upper() + li[0])
            event.add('description', li[1].strip())
            timelist = self.time_trans(li[4].strip())
            daylist = self.day_trans(li[3].strip())
            dst = date(2020, daylist[1], daylist[2])
            tst = time(timelist[0], timelist[1])
            datestart = datetime.combine(dst,tst)
            ded = date(2020, daylist[1], daylist[2])
            ted = time(timelist[-3], timelist[-2])
            dateend= datetime.combine(ded,ted)
            event.add('dtstamp', datetime.now())
            event.add('dtstart', datestart)
            event.add('dtend', dateend)
            event.add('location', li[2])
            self.cal.add_component(event)
        with open(outstr+'_output.ics', 'w+', encoding='utf-8') as file:
            file.write(self.cal.to_ical().decode('utf-8'.replace('\r\n', '\n').strip()))

    def newlist(self):
        self.newlist = []
        i = 0
        for t in self.title:
            one = []
            one.append(t)
            one.append(self.content[i])
            one.append(self.location[i])
            one.append(self.day[i])
            one.append(self.time[i])
            i = i + 1
            self.newlist.append(one)

    def remove_repeat(self,list1,list2):
        for li in list2:
            if li in list1:
                list2.remove(li)
                self.remove_repeat(list1,list2)

if __name__ == "__main__":
    browse1 = ProcessWeb("pizza",driver)
    browse1.start()
    browse1.newlist()
    browse1.to_ics("pizza")
    # list1 = [[1,2],[3,5],[4,6]]
    # list2 = [[3,5],[1,2],[8,9]]
    # browse1.remove_repeat(list1,list2)

    browse2 = ProcessWeb("food",driver)
    browse2.start()
    browse2.newlist()
    browse2.remove_repeat(browse1.newlist, browse2.newlist)
    browse2.to_ics("food")

    browse3 = ProcessWeb("snack", driver)
    browse3.start()
    browse3.newlist()
    browse3.remove_repeat(browse1.newlist, browse3.newlist)
    browse3.remove_repeat(browse2.newlist, browse3.newlist)
    browse3.to_ics("snack")

# class = 'evDate' for Day 
# class = 'evTime' for Time
# class = 'evLocation' for location
# div class = 'event-details' h1 for title
# get location = [] 
# Day = []
# content = []
# title = []
# Time = []

