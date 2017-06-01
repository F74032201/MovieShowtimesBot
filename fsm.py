#-*- coding: utf-8 -*-

from transitions.extensions import GraphMachine
import telegram
import re
import json
import requests
import random
from bs4 import BeautifulSoup

API_TOKEN = '352682097:AAH_jBdxJr-Tt8i0pPP19ujfyKeG2iuUT2U'
bot = telegram.Bot(token=API_TOKEN)
html =''
m_html= ''
MovieTheater = []
Movies = []
The_movie = ''

class TocMachine(GraphMachine):
    def __init__(self, **machine_configs):
        self.machine = GraphMachine(
            model = self,
            **machine_configs
        )

    '''
    def is_going_to_user(self,update):
        text = update.message.text
        print("going user")
        if text == u"重新查詢":
            return True
    '''
    def is_going_to_state1(self, update):
        global html
        res = requests.post(u"http://www.atmovies.com.tw/showtime/a01/")

        soup = BeautifulSoup(res.text, 'html.parser')

        region = []
        theater = soup.select(".theaterArea")[0]
        rows = theater.find_all('a')
        for i in rows:
            region.append([i.text.replace(' ',''),i['href']])

        text = update.message.text
        print("going state1")
        for i in region:
            #save html of region
            if text == i[0]:
                html = i[1]
                return True
        
        custom_keyboard = []
        for i in range(1,len(region)-1,2):
            custom_keyboard.append([region[i][0],region[i+1][0]])
            
        reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard,one_time_keyboard=True)
        update.message.reply_text("請選擇您想觀看電影的城市",reply_markup=reply_markup)

        

    def is_going_to_state2(self, update):
        text = update.message.text
        print("going state2")
        if (text == u"戲院時間查詢(今日)"):
            return True
        
    
    def is_going_to_state3(self,update):
        global MovieTheater
        text = update.message.text
        for i in MovieTheater:
            if i[0]==text:
                #print information
                htm = 'http://www.atmovies.com.tw' + i[1]
                res = requests.post(htm)
                soup = BeautifulSoup(res.text, 'html.parser')
                re_text = ''
                showtime = soup.find_all(id="theaterShowtimeTable")

                for x in showtime:
                    ul = x.find_all("ul")
                    li = ul[1].find_all("li")   
                    re_text = re_text + x.find('a').text + "\n"
                    for i in range(0,len(li)-1):
                        re_text = re_text + li[i].text + "\n"
                    re_text = re_text + "\n"
                update.message.reply_text(re_text)
                return True
        
    def is_going_to_state4(self,update):
        text = update.message.text
        print("going state4")
        if text==u"電影時間查詢(今日)":
            return True

    def is_going_to_state5(self,update):
        #首輪電影
        text = update.message.text
        if text == u"首輪電影":
            return True

    def is_going_to_state6(self,update):
        #二輪電影
        text = update.message.text
        if text == u"二輪電影":
            return True

    def is_going_to_state7(self,update):
        global Movies,m_html,The_movie
        text = update.message.text
        for x in Movies:
            if x[0] == text:
                print('going state7')
                The_movie = text
                m_html = "http://www.atmovies.com.tw" + x[1]
                res = requests.post(m_html)
                p = re.compile('(<li class=\"filmV.+?<li>)')
                new = p.findall(res.text)
                n = res.text
                for i in new:   
                    n = re.sub('(<li class=\"filmV.+?<li>)','',n)

                soup = BeautifulSoup(n, 'html.parser')
                re_text = ''
                showtime = soup.find_all(id="filmShowtimeBlock")
                ul = showtime[0].find_all("ul")
                #print(ul)
                for x in ul:
                    re_text = re_text + x.find_all("li" ,{"class":"theaterTitle"})[0].text + '\n'
                    li = x.find_all("li")
                    for i in range(1,len(li)):
                        re_text = re_text +li[i].text + '\n'
                    re_text = re_text + '\n'
                 
                if len(re_text)>=4096:
                    for j in range(0,len(re_text)-1,4096):
                        if j>=len(re_text):
                            update.message.reply_text(re_text[j-4096:len(re_text)-1])
                            break
                        else:
                            update.message.reply_text(re_text[j:j+4095])
                else:
                    update.message.reply_text(re_text)
                    #record the movie
                    res = requests.post(m_html)
                    soup = BeautifulSoup(res.text, 'html.parser')
                    h2 = soup.select('h2')
                    m_html = h2[0].find('a')['href']
                return True
    def is_going_to_state8(self,update):
        print('going state8')
        text = update.message.text
        if text == u"返回":
            return True

    def is_going_to_state9(self,update):
        print('going state9')
        global m_html
        text = update.message.text
        if text == u'預告片(隨機)':
            m = m_html.replace('/movie/','')
            filmMoreTrailer = 'http://app2.atmovies.com.tw/filmMoreTrailer/'+m
            res = requests.post(filmMoreTrailer)
            soup = BeautifulSoup(res.text, 'html.parser')
            div = soup.find_all("div" ,{"style":"margin:10px 0;"})
            random_film = random.randint(0,len(div)-1)
            re_text = '<a href="'+div[random_film].find('iframe')['src']+'">'+div[random_film].text.replace('\n','').replace('\t','').replace('\r','')+'</a>'
            update.message.reply_text(re_text,parse_mode=telegram.ParseMode.HTML)
            return True

    def is_going_to_state10(self,update):
        print('going state10')
        global m_html
        text = update.message.text
        if text == u'劇情簡介':
            m = 'http://www.atmovies.com.tw'+m_html
            res = requests.post(m)
            n = re.sub('(<img src=.+?劇情簡介)','',res.text)
            soup = BeautifulSoup(n, 'html.parser')
            div = soup.find_all("div",{"style":"width:90%;font-size: 1.1em;"})
            re_text = div[0].text
            update.message.reply_text(re_text)
            return True

    def is_going_to_state11(self,update):
        print('going state11')
        global m_html
        text = update.message.text
        if text == u'IMDb評分查詢':
            m = 'http://www.atmovies.com.tw'+m_html
            res = requests.post(m)
            p = re.compile('<LI><a  href="(.+?)" target=_blank>IMDb</a>')
            IMDb = p.findall(res.text)
            res = requests.post(IMDb[0])
            soup = BeautifulSoup(res.text, 'html.parser')
            div = soup.find_all("div" ,{"class":"ratingValue"})
            re_text = '<b>' + div[0].text.replace('\n','')+ '</b>' + '\n' + div[0].find('strong')['title']
            update.message.reply_text(re_text,parse_mode=telegram.ParseMode.HTML)
            return True


    def on_enter_state1(self, update):
        print('on state1')
        custom_keyboard = [['戲院時間查詢(今日)','電影時間查詢(今日)'],['重新查詢']]
        reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard,one_time_keyboard=True)
        update.message.reply_text("請選擇查詢方式", reply_markup=reply_markup)
        
        

    def on_enter_state2(self, update):
        global html,MovieTheater
        print('on state2')
        res = requests.post(html)
        soup = BeautifulSoup(res.text, 'html.parser')
        MovieTheater = []

        theater = soup.find_all("select")
        rows = theater[0].find_all("option")
        for i in range(1,len(rows)-1):
            if rows[i].text[0]=='▓':
                continue
            MovieTheater.append([rows[i].text,rows[i]['value']])
        
        custom_keyboard = []
        for i in MovieTheater:
            custom_keyboard.append([i[0]])
        custom_keyboard.append(['重新查詢'])
        reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard,one_time_keyboard=True)
        update.message.reply_text("請選擇您欲查詢之戲院",reply_markup=reply_markup)

        #back to user
        '''
        text = update.message.text
        print("going user")
        if text == u"重新查詢":
            self.go_back(update)
        '''
        #update.message.reply_text(text="Custom Keyboard Test", reply_markup=reply_markup)
        #self.go_back(update)



    def on_enter_state3(self,update):
        print('on state3')
        self.go_back_32(update)

    def on_enter_state4(self,update):
        print('on state4')
        custom_keyboard = [['首輪電影','二輪電影'],['重新查詢']]
        reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard,one_time_keyboard=True)
        update.message.reply_text("請選擇您想欲查詢之電影種類",reply_markup=reply_markup)

    def on_enter_state5(self,update):
        global html,Movies
        print('on state5')
        res = requests.post(html)
        soup = BeautifulSoup(res.text, 'html.parser')
        Movies = []
        theater = soup.find_all("select")
        rows = theater[1].find_all("option")
        custom_keyboard = []
        for i in range(2,len(rows)-1):
            if rows[i]['value']=="/movie/now2/":
                break;
            Movies.append([rows[i].text.replace('\n','').replace('\r','').replace(' ',''),rows[i]['value']])
            custom_keyboard.append([rows[i].text.replace('\n','').replace('\r','').replace(' ','')])
        custom_keyboard.append(['重新查詢'])
        reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard,one_time_keyboard=True)
        update.message.reply_text("請選擇您欲查詢之電影",reply_markup=reply_markup)

    def on_enter_state6(self,update):
        global html,Movies
        print('on state6')
        res = requests.post(html)
        soup = BeautifulSoup(res.text, 'html.parser')
        Movies = []
        theater = soup.find_all("select")
        rows = theater[1].find_all("option")
        custom_keyboard = []
        flag = 0
        for i in range(2,len(rows)-1):
            if flag == 1:       
                Movies.append([rows[i].text.replace('\n','').replace('\r','').replace(' ',''),rows[i]['value']])
                custom_keyboard.append([rows[i].text.replace('\n','').replace('\r','').replace(' ','')])
            if rows[i]['value']=="/movie/now2/":
                flag = 1
        custom_keyboard.append(['重新查詢'])
        reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard,one_time_keyboard=True)
        update.message.reply_text("請選擇您欲查詢之電影",reply_markup=reply_markup)

    def on_enter_state7(self,update):
        global m_html
        print('on state7')
        custom_keyboard = [['預告片(隨機)','劇情簡介','IMDb評分查詢'],['返回','重新查詢']]
        reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard,one_time_keyboard=True)
        update.message.reply_text("請選擇",reply_markup=reply_markup)
        text = update.message.text

    def on_enter_state8(self,update):
        print('on state8')
        self.go_back_84(update)

    def on_enter_state9(self,update):
        print('on state9')
        self.go_back_97(update)

    def on_enter_state10(self,update):
        print('on state10')
        self.go_back_107(update)

    def on_enter_state11(self,update):
        print('on state11')
        self.go_back_117(update)

    def on_exit_state1(self, update):
        print('Leaving state1')
    

    def on_exit_state2(self, update):
        print('Leaving state2')

    def on_exit_state3(self,update):
        print('Leaving state3')

    def on_exit_state4(self,update):
        print('Leaving state4')  

    def on_exit_state5(self,update):
        print('Leaving state5')    

    def on_exit_state6(self,update):
        print('Leaving state6') 
    
    def on_exit_state7(self,update):
        print('Leaving state7') 

    def on_exit_state8(self,update):
        print('Leaving state8') 

    def on_exit_state9(self,update):
        print('Leaving state9') 

    def on_exit_state10(self,update):
        print('Leaving state10') 

    def on_exit_state11(self,update):
        print('Leaving state11') 


