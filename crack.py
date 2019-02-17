import time
from io import BytesIO
from PIL import Image
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from chaojiying import Chaojiying


CHAOJIYING_USERNAME = 'xxxx'
CHAOJIYING_PASSWORD = 'xxxx'
CHAOJIYING_SOFT_ID = 893590
CHAOJIYING_KIND = 9102


class CrackCode:


    def __init__(self,driver,class_name,identifying_name):
        """

        :param driver: 浏览器对象
        :param class_name: 图片元素的class属性名称
        :param identifying_name: 判断是否登陆成功的验证信息
        """
        self.browser = driver
        self.chaojiying = Chaojiying(CHAOJIYING_USERNAME, CHAOJIYING_PASSWORD, CHAOJIYING_SOFT_ID)
        self.name = class_name
        self.wait = WebDriverWait(self.browser,15)
        self.identifying_name = identifying_name

    def get_touclick_element(self):
        """
        获取验证图片对象
        :return: 图片对象
        """
        element = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, self.name)))
        return element
    
    def get_position(self):
        """
        获取验证码位置
        :return: 验证码位置元组
        """
        element = self.get_touclick_element()
        time.sleep(2)
        location = element.location
        size = element.size
        top, bottom, left, right = location['y'], location['y'] + size['height'], location['x'], location['x'] + size[
            'width']
        return (top, bottom, left, right)
    
    def get_screenshot(self):
        """
        获取网页截图
        :return: 截图对象
        """
        screenshot = self.browser.get_screenshot_as_png()
        screenshot = Image.open(BytesIO(screenshot))
        return screenshot
    
    def get_touclick_image(self, name='captcha.png'):
        """
        获取验证码图片
        :return: 图片对象
        """
        top, bottom, left, right = self.get_position()
        print('验证码位置', top, bottom, left, right)
        screenshot = self.get_screenshot()
        captcha = screenshot.crop((left, top, right, bottom))
        captcha.save(name)
        return captcha
    
    def get_points(self, captcha_result):
        """
        解析识别结果
        :param captcha_result: 识别结果
        :return: 转化后的结果
        """
        groups = captcha_result.get('pic_str').split('|')
        locations = [[int(number) for number in group.split(',')] for group in groups]
        return locations
    
    def touch_click_words(self, locations):
        """
        点击验证图片
        :param locations: 点击位置
        :return: None
        """
        for location in locations:
            print(location)
            ActionChains(self.browser).move_to_element_with_offset(self.get_touclick_element(), location[0],location[1]).click().perform()
            time.sleep(0.5)

    def crack(self):
        """
        破解入口
        :return: None
        """
        image = self.get_touclick_image() #获得图片对象
        bytes_array = BytesIO()
        image.save(bytes_array, format='PNG') #将图片以bytes形式写入内存
        # 识别验证码
        result = self.chaojiying.post_pic(bytes_array.getvalue(), CHAOJIYING_KIND)  #从内存中读取图片bytes，并传到打码平台解析
        print(result)
        locations = self.get_points(result) #将打码平台返回的结果进行解析，获得坐标
        self.touch_click_words(locations)
        self.browser.find_element_by_class_name('geetest_commit_tip').click()
        time.sleep(5)
        data = self.browser.page_source
        if self.identifying_name in data:     #判断页面是否有个人信息，有就是登陆成功，否则调用自己重新验证
            print('登陆成功')
        else:
            self.crack()





