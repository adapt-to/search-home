#coding:utf-8
from bs4 import BeautifulSoup
import requests
import sys
import time
from math import radians, cos, sin, asin, sqrt
import html5lib
# 需要安装lxml库


# 全局变量
CITY = ''
WORK = ''
NUM = ''
AK = ['填写自己申请的ak码']
MONEY = ''
JULI = ''
HOMES = '' # 查询公寓页数
HOUSES = '' # 每个公寓查询页数
HOUSE_NUMBER = 0 # 记录检索到的房子数目
MYHOUSE_NUMBER = 0 # 符合要求的房子数目
HOUSE_NUMBER_SET = 0 # 查找的公寓数量（一页20个还是太多了，可以在这里筛选）

from juli_style import *
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

    def search_coordinate(self, address,ak): # ak # 计算某地经纬度坐标,需加上市级地名

        parameters = {'address': address, 'key': ak}
        base = 'http://restapi.amap.com/v3/geocode/geo'
        try:
            response = requests.get(base, parameters)
            json_data = response.json()
            #print('json_data = ',json_data)
            #print(address + "的经纬度：", json_data['geocodes'][0]['location'])
            lng = float(json_data['geocodes'][0]['location'].split(',')[0]) # 经度
            lat = float(json_data['geocodes'][0]['location'].split(',')[1]) # 纬度
            #print('经纬度',lng, lat)
            return lng, lat
        except KeyError:
            raise RuntimeError
        #url = 'http://api.map.baidu.com/geocoder/v2/?address='+ address +'&output=json&ak='+ak
        #web_data = requests.get(url)
        #time.sleep(0.01)
        #json_data = web_data.json()
        #time.sleep(0.01)
        #print('json_data=',json_data)


    def Haversine(self, add_1, add_2,ak):
        # lon1, lat1, lon2, lat2 分别代表：经度1，纬度1，经度2，纬度2
        '''
        def digui(ak,i=0):
            nonlocal lon1, lat1, lon2, lat2
            try:
                lon1, lat1 = self.search_coordinate(add_1,ak[i])
                lon2, lat2 = self.search_coordinate(add_2,ak[i])
            except TimeoutException:
                i+=1
                if i<=len(ak):
                    digui(ak,i)
                else:
                    print('ak码额度已用完！请等待')
        '''
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
                            print('ak码额度已用完！请等待')
                            self.textBrowser_display.append('ak码额度已用完！请添加ak码或第二天再试！')


        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])  # 将十进制度数转化为弧度
        # Haversine公式
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371 # 地球平均半径，单位为公里
        d = '%0.4f' %(c * r) # 保留3位小数
        #print("该两点间直线相距：{}km".format(d))
        return d
    def search_house(self,ak, address='广州', work='珠江城大厦',pages=1, huxin = '一居', home_page=1,juli_1='6',money_house='2600'):
        global HOUSE_NUMBER
        global MYHOUSE_NUMBER
        HOUSE_NUMBER = 0
        house = dict()  # 存储查找的 公寓title和link
        home_all = dict() # 符合要求的房子
        home_else = dict() # 未符合要求的房子
         # pages表示查找多少页的公寓数，一页是20个公寓
         # home_page表示一个公寓查找多少页，一页是20个房型
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
        #print(house,len(house))
        house_list = 0 # 发现只有自如是点进去就有房子，其他公寓进去都是每个区域的房屋列表

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
                        #one_home_address = home_address.get_text().strip() # 房子 地址
                        one_home_money = home_money.get_text().strip() # 房子价格
                        one_home_url = home_url.get('href')

                        #print('传入api的地址：',address+'市'+one_home_title.split(' ')[0].split('·')[-1])
                        #try:
                        juli = float(self.Haversine(address+'市'+one_home_title.split(' ')[0].split('·')[-1],address+'市'+work,ak))
                        #except KeyError:
                            
                            #juli = float(self.Haversine(address+'市'+one_home_title.split(' ')[0].split('·')[-1],address+'市'+work))

                        if juli < float(juli_1) and float(one_home_money.split(' ')[0]) < float(money_house):
                            HOUSE_NUMBER += 1
                            home_all[one_home_title] = ['url直达：'+ URL_TOP + one_home_url,
                                                        '直线距离:'+str(juli)+'KM',
                                                        one_home_money.split(' ')[0]+'元/月']
                        else:
                            HOUSE_NUMBER += 1
                            home_else[one_home_title] = ['url直达：'+ URL_TOP + one_home_url,
                                                        '直线距离:'+str(juli)+'KM',
                                                        one_home_money.split(' ')[0]+'元/月']
            else: #在这里处理除开自如，其他的房屋
                apartment_links = {} #每个公寓的各个区域的url
                #apartment_link = ''
                #my_apartment_title = ''
                #print('home_page=',home_page)
                for m in range(home_page):
                    #print('m=',m)
                    link = link + 'pg' + str(m+1) # 这里是公寓的区域分布
                    #print(link)
                    house_data = requests.get(link)
                    soup = BeautifulSoup(house_data.text,'lxml')
                    apartment_urls = soup.select('div.flat_item_card > a:nth-of-type(1)') # 第一个a标签
                    #print(apartment_urls)
                    apartment_titles = soup.select('p.flat_item_card_title')
                    #print(apartment_titles)
                    for apartment_url,apartment_title in zip(apartment_urls,apartment_titles):
                        apartment_link = apartment_url.get('href')
                        my_apartment_title = apartment_title.get_text().strip()
                        apartment_links[my_apartment_title] = URL_TOP + apartment_link

                #print('除开自如公寓的其他公寓的每个区域的url地址',apartment_links,len(apartment_links))

                for a_title,a_url in apartment_links.items(): #每个区域具体公寓的地址
                    for m in range(home_page):
                        apartment_data = requests.get(a_url)
                        html = apartment_data.text
                        bf = BeautifulSoup(html,features="html5lib")

                        apartment_texts = bf.find_all("div", class_ = "flat_detail_renting_item")
                        list_home_title = []
                        for xx in range(len(apartment_texts)):
                            #print(apartment_texts[xx].h3.text())
                            nn = BeautifulSoup(str(apartment_texts[xx]), features="html5lib")
                            aa = nn.find_all('h3')
                            for fd in aa:
                                #print(fd.text)
                                list_home_title.append(fd.text)

                        for index,fff in enumerate(list_home_title):
                                list_home_title[index] = fff.strip('\n ')
                        #print(list_home_title)
                        apartment_prices = bf.find_all('p',class_='flat_detail_renting_price')
                        paartment_address = bf.find_all('p',class_='flat_detail_address',limit=1) # 区域具体公寓的地址


                        juli = float(self.Haversine(address+'市'+str(paartment_address[0].text),address+'市'+work,ak))
                        if juli > float(juli_1): # 只要距离大了
                            continue

                        apartment_ul = bf.find_all('ul', class_='flat_detail_renting_list') # 空
                        #print('apartment_ul = ',apartment_ul)
                        for i_title in apartment_texts:
                            pass
                        #for paartment_address in paartment_addresss:
                        list_name = [] #存储每个具体区域的公寓中每一个房型的url
                        for y in range(len(apartment_ul)):
                            n = BeautifulSoup(str(apartment_ul[y]), features="html5lib")
                            aa = n.find_all('li')
                            for m in range(len(aa)):
                                ew = BeautifulSoup(str(aa[m]), features="html5lib")
                                fdaa = ew.find_all('a')
                                for jj in fdaa:
                                    list_name.append(jj.get("href"))
                        #print('list_name = ',list_name) # 空
                        zz = 0
                        #print('price',apartment_prices,type(apartment_prices))
                        for apartment_price in apartment_prices:
                            price = apartment_price.text
                            #print(price)
                            price = price.split('元')[0]
                            if '-' in price:
                                price = (int(price.split('-')[0]) + int(price.split('-')[-1]))/2
                                #print('去掉-后',float(price))
                            else:
                                try:
                                    price = float(price)
                                except ValueError:
                                    price = 0 # 0表示无价格，所以房型已经被租满了。
                                    zz += 1 # 房屋title加1
                                    continue # 舍去没有价格的

                            #print(address+'市'+str(paartment_address[0].text))
                            juli = float(self.Haversine(address+'市'+str(paartment_address[0].text),address+'市'+work,ak))
                            if juli < float(juli_1) and float(price) < float(money_house):
                                HOUSE_NUMBER += 1
                                home_all[list_home_title[zz]] = ['url直达：'+ URL_TOP + list_name[zz],
                                                        '直线距离:'+str(juli)+'KM',
                                                        str(price)+'元/月']
                            else:
                                HOUSE_NUMBER += 1
                                pass
                                '''
                                home_else[list_home_title[zz]] = ['url直达：'+ URL_TOP + list_name[zz],
                                                        '直线距离:'+str(juli)+'KM',
                                                        str(price)+'元/月']
                                '''
                            zz += 1
                #print('除开自如的其他公寓的具体区域的具体户型的具体内容',home_all)



            house_list = 1
            house_number_set += 1
        #print(home_all)
        #print(home_else)
        MYHOUSE_NUMBER = len(home_all)
        return home_all
    #search_house()# 不加参数默认查找广州的前20位公寓

    def con_serial(self,message):
        self.textBrowser_display.append(message + '：保存成功\n')


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
    def on_pushButton_search_clicked(self):
        #self.textBrowser_display.append('请稍等片刻')
        '''
        def on_pushButton_search():
            dict_house = self.search_house(AK, address= CITY, work=WORK, pages=HOMES, huxin=NUM, home_page=HOUSES,juli_1=JULI,money_house=MONEY)
            for title,data in dict_house.items():
                all_data = title + ' '.join(data) + '\n'
                self.textBrowser_display.append(all_data)
            self.textBrowser_display.append('共检索到{0}套房屋，其中{1}套符合设置的要求，已在上述显示！'.format(HOUSE_NUMBER,MYHOUSE_NUMBER))

        t = threading.Thread(target=on_pushButton_search, name='LoopThread')
        t.start()

        '''
        dict_house = self.search_house(AK, address= CITY, work=WORK, pages=HOMES, huxin=NUM, home_page=HOUSES,juli_1=JULI,money_house=MONEY)
        for title,data in dict_house.items():
            all_data = title + ' '.join(data) + '\n'
            self.textBrowser_display.append(all_data)
        self.textBrowser_display.append('共检索到{0}套房屋，其中{1}套符合设置的要求，已在上述显示！'.format(HOUSE_NUMBER,MYHOUSE_NUMBER))
        starttime = time.strftime("%Y-%M-%d-%H-%M-%S - ", time.localtime(time.time()))
        with open('D:/户型查找'+CITY+str(MONEY)+str(NUM)+starttime+'.txt','a') as fg:
            for title, data in dict_house.items():
                fg.write(title+'-'+data+'\n')
        self.textBrowser_display.append('租房信息保存在:{}'.format('D:/户型查找'+CITY+str(MONEY)+str(NUM)+starttime+'.txt'))



class slot(QtGui.QMainWindow):
    def __init__(self,ui,tab):
        QtGui.QMainWindow.__init__(self)
        self.tab = tab

    def graphical_intf(self):
        self.con = slot_con(self.tab)
        self.con.setGeometry(QtCore.QRect(0, 0, 1400, 800))
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    widget = QtGui.QTabWidget()
    widget.resize(1400, 800)
    a = QtGui.QFrame(widget)
    a.setGeometry(QtCore.QRect(0, 0, 1400, 800))
    w = slot(widget, a)
    w.graphical_intf()
    widget.show()
    #pg.QtGui.QApplication.exec_()
    sys.exit(app.exec_())






