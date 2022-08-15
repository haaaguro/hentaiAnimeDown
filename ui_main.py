import requests
import re
from threading import Thread
from queue import Queue
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread ,  pyqtSignal
import sys
from qt.layout import Ui_MainWindow as UIM
from urllib import request
import os
import time
from bs4 import BeautifulSoup

tasks =Queue(maxsize = 50)

class BackendThread(QThread):
    update_date = pyqtSignal(str)

    def __init__(self, http_url):
        super(BackendThread, self).__init__()
        self.http_url = http_url
        

    def run(self):
        global tasks
        while not tasks.empty():
            url = tasks.get()
            print("开始下载")
            self.get_img(url)
        print("下载完成")
        self.exit()
    # @excute_time_decorator
    def get_img(self,http_url):
        global tasks
        proxies = {
            'http': 'http://127.0.0.1:1080',
            'https': 'https://127.0.0.1:1080'
        }
        request.ProxyHandler(proxies)
        opener = request.build_opener(request.ProxyHandler(proxies))
        request.install_opener(opener)
        r = request.Request(http_url)
        r.add_header('User-Agent',
                     'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36')
        with request.urlopen(r) as f:
            soup = BeautifulSoup(f, features='lxml')
            img_list = soup.find_all('img')
            url = img_list[2]
            url = url.get('data-srcset')
            html = url[:-6]
            html = list(html)
            html[8] = 'i'
            html = ''.join(html)
            name1 = soup.find_all('span', attrs={"class": "before"})[1].contents[0]
            name2 = soup.find_all('span', attrs={"class": "pretty"})[1].contents[0]
            dir_name = name1 + name2
            div_list = soup.find_all('div', attrs={"class": "no-select"})
            ranges = div_list[div_list.__len__() - 2].contents[0].get_text()
            ranges = int(ranges)+1
            moudle = ".jpg"
        try:
            photo = "1.jpg"
            h = html + photo
            requests = request.Request(h)
            requests.add_header('User-Agent',
                            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36')
            request.urlopen(requests)
        except Exception as e:
            moudle =".png"
        if os.path.exists(dir_name):
            return
        else:
            try:
                os.mkdir(dir_name)
            except Exception as e:
                self.update_date.emit(dir_name+"文件夹创建失败")
                return
        self.update_date.emit("开始下载：  "+dir_name)
        for i in range(1, ranges):
            photo = str(i) + moudle
            h = html + photo
            requests = request.Request(h)
            requests.add_header('User-Agent',
                                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36')
            f=request.urlopen(requests)
            info = f.read()
            save = dir_name + "/" + photo
            with open(save, 'wb') as f:
                f.write(info)
            if i==ranges/4+1 :
                self.update_date.emit("已完成25%")
            if i==ranges/2 +1 :
                self.update_date.emit("已完成50%")
            if i==ranges*3/4 +1 :
                self.update_date.emit("已完成75%")
            time.sleep(0.1)
        self.update_date.emit(dir_name+"  下载完成")
        self.update_date.emit("剩余任务数量：" + str(tasks.qsize()))



        
class UIM_Version(UIM,QtWidgets.QWidget):
    send_args = pyqtSignal(str , int)

    def __init__(self):
        QtWidgets.QWidget.__init__(self)#因为继承关系，要对父类初始化
        
    def setupFunction(self):
        self.pushButton.clicked.connect(self.send)
        self.pushButton_2.clicked.connect(self.onButtonClick) 
        self.pushButton_3.clicked.connect(self.start_download)
        self.pushButton_4.clicked.connect(self.open_dir) 

    def onButtonClick(self ):  
        #此处发送信号的对象是button1按钮        
        qApp = QtWidgets.QApplication.instance()
        qApp.quit()

    def send(self):
        global tasks
        http_url = self.lineEdit.text()    # 获取第一个文本框中的内容
        if http_url == '':
            self.msg("提示","请输入简介页url")
        else:
            tasks.put(http_url)
            self.textBrowser.append("任务添加成功,"+str(tasks.qsize())+"个任务待下载")

        
    def msg(self,title,msg):
        QtWidgets.QMessageBox.information(self, title, msg,QtWidgets.QMessageBox.Yes)

    def handleDisplay(self,data):
        self.textBrowser.append(data)   #在指定的区域显示提示信息
        self.cursor=self.textBrowser.textCursor()
        self.textBrowser.moveCursor(self.cursor.End)  #光标移到最后，这样就会自动显示出来
        QtWidgets.QApplication.processEvents()  #一定加上这个功能，不然有卡顿

    def open_dir(self):
        path = os.getcwd()
        os.system("explorer.exe %s" % path)

    def start_download(self):
        global tasks
        if tasks.empty():
            self.handleDisplay("任务队列为空")
            return
        self.backend = BackendThread("http_url")
        self.backend.update_date.connect(self.handleDisplay)
        self.backend.start()


if __name__ == "__main__":
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = UIM_Version()
    ui.setupUi(MainWindow)
    ui.setupFunction()
    ui.handleDisplay("下载地址：https://hanime1.me/comics，进入简介页后复制当页url")
    MainWindow.show()
    sys.exit(app.exec_())

    


     

