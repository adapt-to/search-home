#coding:utf-8
from bs4 import BeautifulSoup
import requests
import sys
import time
from math import radians, cos, sin, asin, sqrt
import threading
import html5lib
# 需要安装lxml库
# 全局变量
CITY = ''
WORK = ''
NUM = ''
AK = [] # 加入ak码
MONEY = ''
JULI = ''
HOMES = '' # 查询公寓页数
HOUSES = '' # 每个公寓查询页数
HOUSE_NUMBER = 0 # 记录检索到的房子数目
MYHOUSE_NUMBER = 0 # 符合要求的房子数目
HOUSE_NUMBER_SET = 0 # 查找的公寓数量（一页20个还是太多了，可以在这里筛选）
starttime = ''
from juli_style_relode import *
try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s
try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)
class slot_con(QtGui.QWidget, Ui_Form):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setupUi(self)
        self.calibration_status = False
        self.parameter_status = False
        self.lineEdit_city.setPlaceholderText('支持所有一线及部分二线城市')
        self.lineEdit_work.setPlaceholderText('工作地点,精确到街道号或楼名')
        self.lineEdit_home.setPlaceholderText('例如:一居、二居等')
        self.lineEdit_juli.setPlaceholderText('注意是与工作地点的直线距离')
        self.lineEdit_ak.setPlaceholderText('填入高德地图ak码，多个可用英文逗号隔开')
        self.lineEdit_ak.setEchoMode(QtGui.QLineEdit.PasswordEchoOnEdit) # 失焦则为圆点显示
        self.lineEdit_money.setPlaceholderText('只填入数字')
        self.lineEdit_homes.setPlaceholderText('填入页数')
        self.lineEdit_HOUSE_NUMBER_SET.setPlaceholderText('若20太多则写其他数字')
        self.lineEdit_houses.setPlaceholderText('查找的房型页数')
        self.progressBar_play.setRange(0, 100)
        self.step = 0
        #self.timer = QtCore.QBasicTimer()
        #pixMap = QtGui.QPixmap("wechat.png").scaled(self.label.width(), self.label.height())
        #self.label_img.setPixmap(pixMap)

    def search_coordinate(self, address,ak):
        parameters = {'address': address, 'key': ak}
        base = 'http://restapi.amap.com/v3/geocode/geo'
        try:
            response = requests.get(base, parameters)
            json_data = response.json()
            lng = float(json_data['geocodes'][0]['location'].split(',')[0]) # 经度
            lat = float(json_data['geocodes'][0]['location'].split(',')[1]) # 纬度
            return lng, lat
        except KeyError:
            raise RuntimeError
    def Haversine(self, add_1, add_2,ak):
        # lon1, lat1, lon2, lat2 分别代表：经度1，纬度1，经度2，纬度2
        try:
            lon1, lat1 = self.search_coordinate(add_1,ak[0])
            lon2, lat2 = self.search_coordinate(add_2,ak[0])
        except RuntimeError:
            try:
                lon1, lat1 = self.search_coordinate(add_1,ak[1])
                lon2, lat2 = self.search_coordinate(add_2,ak[1])
            except RuntimeError: #Runtimeout
                try:
                    lon1, lat1 = self.search_coordinate(add_1,ak[2])
                    lon2, lat2 = self.search_coordinate(add_2,ak[2])
                except RuntimeError:
                    try:
                        lon1, lat1 = self.search_coordinate(add_1,ak[3])
                        lon2, lat2 = self.search_coordinate(add_2,ak[3])
                    except RuntimeError:
                        try:
                            lon1, lat1 = self.search_coordinate(add_1,ak[4])
                            lon2, lat2 = self.search_coordinate(add_2,ak[4])
                        except RuntimeError:
                            #print('ak码额度已用完！请等待')
                            #self.textBrowser_display.append('ak码额度已用完！请添加ak码或第二天再试！')
                            self.con_serial('ak码额度已用完！请添加ak码或第二天再试！',0)
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])  # 将十进制度数转化为弧度
        # Haversine公式，求球面两点距离
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371 # 地球平均半径，单位为公里
        d = '%0.4f' %(c * r) # 保留3位小数
        #print("两点间直线相距：{}km".format(d))
        return d
    def con_serial_house(self,message):
        self.textBrowser_play.append(message)

    def con_jindu(self,timers):
        self.step += timers
        self.progressBar_play.setTextVisible(self.step)
        self.progressBar_play.setValue(self.step)
    def search_house(self,ak, address='广州', work='珠江城大厦',pages=1, huxin = '一居', home_page=1,juli_1='6',money_house='2600'):
        global starttime
        starttime = time.strftime("%Y-%M-%d-%H-%M-%S", time.localtime(time.time()))
        global HOUSE_NUMBER
        global MYHOUSE_NUMBER
        HOUSE_NUMBER = 0
        house = dict()  # 存储查找的 公寓title和link
        home_all = dict() # 符合要求的房子
        timers = 2*int(pages)*int(home_page)*int(HOUSE_NUMBER_SET) / 100
         # pages公寓数，一页是20个公寓
         # home_page公寓查找多少页，一页是20个房型
        URL_TOP = 'https://m.ke.com/' # 头部地址
        ADDRESS = {'广州':'chuzu/gz/brand/pg',
                '上海':'chuzu/sh/brand/pg',
                '北京':'chuzu/bj/brand/pg',
                '深圳':'chuzu/sz/brand/pg',
                '杭州':'chuzu/hz/brand/pg',
                '武汉':'chuzu/wh/brand/pg',
                '苏州':'chuzu/sz/brand/pg',
                '惠州':'chuzu/hui/brand/pg',
                '成都':'chuzu/cd/brand/pg',
                '白山':'chuzu/bs/brand/pg',
                '白城':'chuzu/bc/brand/pg',
                '重庆':'chuzu/cq/brand/pg',
                '长沙':'chuzu/cs/brand/pg',
                '大连':'chuzu/dl/brand/pg',
                '德阳':'chuzu/dy/brand/pg',
                '达州':'chuzu/dz/brand/pg',
                '济南':'chuzu/jn/brand/pg',
                '厦门':'chuzu/xm/brand/pg',
                '福州':'chuzu/fz/brand/pg',
                '海口':'chuzu/hk/brand/pg',
                '合肥':'chuzu/hf/brand/pg',
                '哈尔滨':'chuzu/hrb/brand/pg',
                '荆州':'chuzu/jingzhou/brand/pg',
                '昆明':'chuzu/km/brand/pg',
                '大理':'chuzu/dali/brand/pg',
                '南昌':'chuzu/nc/brand/pg',
                '南京':'chuzu/nj/brand/pg',
                '青岛':'chuzu/qd/brand/pg',
                }
        HUXIN = {
            '一居':'l0',
            '二居':'l1',
            '三居':'l2',
            '四居':'l3',
            '五居':'l4'
        }
        headers = requests.utils.default_headers()
        headers['User-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
        for page in range(pages):
            url = '{0}{1}{2}'.format(URL_TOP,ADDRESS[str(address)],page+1) # NUM是多少就爬第几页的
            beike_data = requests.get(url)
            soup = BeautifulSoup(beike_data.text,'lxml') # lxml格式
            links = soup.select('div.content__item > a') # 处理异步加载数据
            for link, in zip(links):
                house_link = link.get('href') # 获取link
                house_title = link.get('data-event_action') # 获取title
                title = house_title.split('brand_name=')[-1].split('&')[0] # 对title进行处理，剔除html
                house[title] = '{}{}'.format(URL_TOP, house_link) # 放入dict
        house_list = 0 # 自如是点进去就有房子，其他公寓进去都是每个区域的房屋列表
        house_number_set = 0
        for title,link in house.items():
            if house_number_set >= HOUSE_NUMBER_SET:# 这里是几就是只搜索几个公寓的房子
                break
            if house_list == 0:
                for m in range(home_page):
                    link = link + 'pg' + str(m+1) + HUXIN[huxin]
                    house_data = requests.get(link)
                    soup = BeautifulSoup(house_data.text,'lxml')
                    home_titles = soup.select('div.content__item__main > p:nth-of-type(1)') # nth-of-type(1)表示找到该div下的第一个p
                    home_addresss = soup.select('div.content__item__main > p:nth-of-type(2)')
                    home_moneys = soup.select('div.content__item__main > p:nth-of-type(4)')
                    home_xinxi = soup.select('div.content__item > a')
                    for home_title,home_address,home_money,home_url in zip(home_titles,home_addresss,home_moneys,home_xinxi):
                        one_home_title = home_title.get_text().strip() # 每个房子 题目
                        one_home_money = home_money.get_text().strip() # 房子价格
                        one_home_url = home_url.get('href')
                        juli = float(self.Haversine(address+'市'+one_home_title.split(' ')[0].split('·')[-1],address+'市'+work,ak))
                        self.con_jindu(timers)
                        if juli < float(juli_1) and float(one_home_money.split(' ')[0]) < float(money_house):
                            home_all[one_home_title] = ['url直达：'+ URL_TOP + one_home_url,
                                                        '直线距离:'+str(juli)+'KM',
                                                        one_home_money.split(' ')[0]+'元/月']
                            self.con_serial_house('{0}-{1}'.format(one_home_title, 'url直达：'+ URL_TOP + one_home_url+'-'+'直线距离:'+str(juli)+'KM'+one_home_money.split(' ')[0]+'元/月'))

                            with open('D:/户型查找'+CITY+str(MONEY)+str(NUM)+starttime+'.txt','a') as fg:
                                fg.write(str(one_home_title)+'-'+str('url直达：'+ URL_TOP + one_home_url+'-'+'直线距离:'+str(juli)+'KM'+one_home_money.split(' ')[0]+'元/月')+'\n')                        
                        HOUSE_NUMBER += 1
            else: #在这里处理除开自如，其他的房屋
                apartment_links = {} #每个公寓的各个区域的url
                for m in range(home_page):
                    link = link + 'pg' + str(m+1) # 这里是公寓的区域分布
                    house_data = requests.get(link)
                    soup = BeautifulSoup(house_data.text,'lxml')
                    apartment_urls = soup.select('div.flat_item_card > a:nth-of-type(1)') # 第一个a标签
                    apartment_titles = soup.select('p.flat_item_card_title')
                    for apartment_url,apartment_title in zip(apartment_urls,apartment_titles):
                        apartment_link = apartment_url.get('href')
                        my_apartment_title = apartment_title.get_text().strip()
                        apartment_links[my_apartment_title] = URL_TOP + apartment_link
                for a_title,a_url in apartment_links.items(): #每个区域具体公寓的地址
                    for m in range(home_page):
                        apartment_data = requests.get(a_url)
                        html = apartment_data.text
                        bf = BeautifulSoup(html,features="html5lib")
                        apartment_texts = bf.find_all("div", class_ = "flat_detail_renting_item")
                        list_home_title = []
                        for xx in range(len(apartment_texts)):
                            nn = BeautifulSoup(str(apartment_texts[xx]), features="html5lib")
                            aa = nn.find_all('h3')
                            for fd in aa:
                                list_home_title.append(fd.text) # 获取具体公寓中户型的title和url
                        for index,fff in enumerate(list_home_title):
                                list_home_title[index] = fff.strip('\n ')
                        apartment_prices = bf.find_all('p',class_='flat_detail_renting_price')
                        paartment_address = bf.find_all('p',class_='flat_detail_address',limit=1) # 区域具体公寓的地址
                        juli = float(self.Haversine(address+'市'+str(paartment_address[0].text),address+'市'+work,ak))
                        if juli > float(juli_1): # 距离大于设定值就continue
                            continue
                        apartment_ul = bf.find_all('ul', class_='flat_detail_renting_list') # 空
                        list_name = [] #存储每个具体区域的公寓中每一个房型的url
                        for y in range(len(apartment_ul)):
                            n = BeautifulSoup(str(apartment_ul[y]), features="html5lib")
                            aa = n.find_all('li')
                            for m in range(len(aa)):
                                ew = BeautifulSoup(str(aa[m]), features="html5lib")
                                fdaa = ew.find_all('a')
                                for jj in fdaa:
                                    list_name.append(jj.get("href"))
                        zz = 0 #list_home_title索引
                        for apartment_price in apartment_prices:
                            price = apartment_price.text
                            price = price.split('元')[0]
                            if '-' in price:
                                price = (int(price.split('-')[0]) + int(price.split('-')[-1]))/2
                            else:
                                try:
                                    price = float(price)
                                except ValueError:
                                    price = 0 # 0表示无价格，所以房型已经被租满了。
                                    zz += 1 # 房屋title加1
                                    continue # 舍去没有价格的
                            address_apartment = address+'市'+str(paartment_address[0].text)

                            juli = float(self.Haversine(address_apartment,address+'市'+work,ak))
                            self.con_jindu(timers)
                            if juli < float(juli_1) and float(price) < float(money_house):
                                if ' ' in list_home_title[zz]:
                                    home_title_zz = '-[{0}]-[{1}]'.format(list_home_title[zz].split(' ')[0],list_home_title[zz].split(' ')[-1])
                                else: # list_home_title[zz]
                                    home_title_zz = '-[{0}]-[仅{1}]'.format(list_home_title[zz].split('仅')[0],list_home_title[zz].split('仅')[-1])
                                #print(address_apartment+home_title_zz) # 房屋名称
                                home_all[str(paartment_address[0].text)+home_title_zz] = ['url直达：'+ URL_TOP + list_name[zz],
                                                        '直线距离:'+str(juli)+'KM',
                                                        str(price)+'元/月']
                                #self.textBrowser_other_show.append(_translate("From", starttime + message, None))
                                #self.textBrowser_play.append(_translate("From", '{0}-{1}'.format(str(paartment_address[0].text)+home_title_zz, 'url直达：'+ URL_TOP + list_name[zz]+'-'+'直线距离:'+str(juli)+'KM'+ str(price)+'元/月'), None))
                                self.con_serial_house('{0}-{1}'.format(str(paartment_address[0].text)+home_title_zz, 'url直达：'+ URL_TOP + list_name[zz]+'-'+'直线距离:'+str(juli)+'KM'+ str(price)+'元/月'))

                                with open('D:/户型查找'+CITY+str(MONEY)+str(NUM)+starttime+'.txt','a') as fg:
                                        if '\u2764' in str(paartment_address[0].text)+home_title_zz:
                                            str(paartment_address[0].text)+home_title_zz.replace('\u2764','')
                                        fg.write(str(str(paartment_address[0].text)+home_title_zz)+'-'+str('url直达:'+ URL_TOP + list_name[zz]+' '+'直线距离约:'+str(juli)+'公里'+' '+'租金:'+ str(price)+'元/月')+'\n')
                            zz += 1
                            HOUSE_NUMBER += 1
            house_list = 1
            house_number_set += 1
        MYHOUSE_NUMBER = len(home_all)
        self.con_serial('共检索到{0}套房屋，其中{1}套符合设置的要求，已在右侧显示！'.format(HOUSE_NUMBER,MYHOUSE_NUMBER),0)
        self.con_serial('或者您也可以查看本地文件，房屋文件保存在:{}'.format('D:/户型查找'+CITY+str(MONEY)+str(NUM)+starttime+'.txt'),0)

    def con_serial(self,message,flag=1):
        if flag:
            self.textBrowser_display.append(message + '：保存成功\n')
        else:
            self.textBrowser_display.append(message)


    @QtCore.pyqtSignature("")
    def on_pushButton_city_clicked(self):
        global CITY

        city = self.lineEdit_city.text()
        if city[-1] == '市':
            self.textBrowser_display.append('保存失败，城市名不需要添加 ‘市’ ！\n')
        else:
            self.con_serial(city)
            CITY = city

    @QtCore.pyqtSignature("")
    def on_pushButton_work_clicked(self):
        global WORK
        work = self.lineEdit_work.text()
        self.con_serial(work)
        WORK = work

    @QtCore.pyqtSignature("")
    def on_pushButton_home_clicked(self):
        global NUM
        num = self.lineEdit_home.text()
        self.con_serial(num)
        NUM = num

    @QtCore.pyqtSignature("")
    def on_pushButton_juli_clicked(self):
        global JULI
        juli = self.lineEdit_juli.text()
        self.con_serial(juli)
        JULI = juli

    @QtCore.pyqtSignature("")
    def on_pushButton_ak_clicked(self):
        global AK
        ak = self.lineEdit_ak.text()
        ak = ak.split(',')
        self.con_serial(ak)
        AK = ak

    @QtCore.pyqtSignature("")
    def on_pushButton_money_clicked(self):
        global MONEY
        money = self.lineEdit_money.text()
        self.con_serial(money)
        MONEY = money

    @QtCore.pyqtSignature("")
    def on_pushButton_homes_clicked(self):
        global HOMES,HOUSES,HOUSE_NUMBER_SET
        homes = self.lineEdit_homes.text()
        houses = self.lineEdit_houses.text()
        house_set = self.lineEdit_HOUSE_NUMBER_SET.text()
        if int(homes) < 1 or int(houses) < 1 or int(house_set) < 1:
            self.textBrowser_display.append('公寓页数和房屋页数必须为整数且大于等于1 ！\n')
        else:
            self.con_serial(homes)
            self.con_serial(houses)
            self.con_serial(house_set)
            HOMES = int(homes)
            HOUSES = int(houses)
            HOUSE_NUMBER_SET = int(house_set)

    @QtCore.pyqtSignature("")
    def on_pushButton_jindutiao_clicked(self):
        #self.timer.start(1, self)
        pass

    @QtCore.pyqtSignature("")
    def on_pushButton_search_clicked(self):
        po = threading.Thread(target=self.search_house,args=[AK, CITY, WORK, HOMES, NUM, HOUSES, JULI, MONEY],daemon=True) # 多线程
        po.start()




class slot(QtGui.QMainWindow):
    def __init__(self,ui,tab):
        QtGui.QMainWindow.__init__(self)
        self.tab = tab
    def graphical_intf(self):
        self.con = slot_con(self.tab)
        self.con.setGeometry(QtCore.QRect(0, 0, 1200, 800))


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    widget = QtGui.QTabWidget()
    widget.resize(1200,800)
    a = QtGui.QFrame(widget)
    a.setGeometry(QtCore.QRect(0, 0, 1200, 800))
    w = slot(widget, a)
    w.graphical_intf()
    widget.show()
    sys.exit(app.exec_())






