#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 17 00:51:16 2018

@author: kindy

@modify: zdaiot

python 调用baidu api实现简单翻译软件

https://abrahum.link/2017/01/27/Pyinstaller%E6%89%93%E5%8C%85PyQt5%E8%B8%A9%E7%9A%84%E5%9D%91%E4%BB%AC/

pip install tencentcloud-sdk-python

前往http://api.fanyi.baidu.com/api/trans/product/index注册账号， 登录后台创建应用
"""
import http.client as httplib
from hashlib import md5
import urllib
import random
import json
import sys
import time
from PyQt5 import QtCore, QtGui, uic
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QMessageBox
from PyQt5.QtWidgets import QFileDialog, QAction, qApp
from PyQt5.QtGui import QIcon, QPixmap

from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.tmt.v20180321 import tmt_client, models

qtCreatorFile = "zdict.ui"
# 使用uic加载
# 使用uic加载
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)


class MyApp(QMainWindow, Ui_MainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        super().__init__()
        self.initUI()  # 调用自定义的UI初始化函数initUI()
        self.initBaiDu()
        self.initQQ()

    def initBaiDu(self):
        self.appKey = '20180317000136787'  # 就是应用ID
        self.secretKey = 'jkwmEFzkfdHdmMy3Q2RR'  # 就是应用密钥
        self.httpClient = None
        self.myurl = '/api/trans/vip/translate'

        self.salt = random.randint(1, 65536)  # 随机数


    def initQQ(self):
        cred = credential.Credential("AKIDjLfWmLkSxnwN7ClhNNgJFYsVoRMerQkB", "pq3T4mcYGV8ngbnNGY8BXDGbIV2xLugk")
        httpProfile = HttpProfile()
        httpProfile.endpoint = "tmt.tencentcloudapi.com"

        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        self.client = tmt_client.TmtClient(cred, "ap-chengdu", clientProfile)

        self.req = models.TextTranslateRequest()

    def lang_transform(self, lang):
        '''
        tranform the language into correct format that ai.youdao.com accepted
        中文	zh-CHS
        日文	ja
        英文	EN
        韩文	ko
        法文	fr
        俄文	ru
        葡萄牙文	pt
        西班牙文	es
        '''
        if lang == "Chinese":
            return "zh"
        if lang == "Japanease":
            return "ja"
        if lang == "English":
            return "en"
        if lang == "Korea":
            return "kor"
        if lang == "Russia":
            return "ru"
        if lang == "French":
            return "fra"
        if lang == "Auto":
            return "auto"

    def initUI(self):
        '''
        Initialize the window's UI
        '''
        self.setupUi(self)
        self.setWindowTitle("Dict Translate")
        self.setWindowIcon(QIcon("image/translate.png"))  # 设置图标，linux下只有任务栏会显示图标

        self.initMenuBar()  # 初始化菜单栏
        self.initToolBar()  # 初始化工具栏
        self.initButton()  # 初始化按钮

        self.show()  # 显示

    def initMenuBar(self):
        '''
        初始化菜单栏
        '''
        menubar = self.menuBar()
        # self.actionExit.triggered.connect(qApp.quit)    # 按下菜单栏的Exit按钮会退出程序
        # self.actionExit.setStatusTip("退出程序")         # 左下角状态提示
        # self.actionExit.setShortcut('Ctrl+Q')           # 添加快捷键
        exitAct = QAction(QIcon('image/exit.png'), 'Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.triggered.connect(qApp.quit)

        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAct)

        fileMenu = menubar.addMenu('&Help')

    def initToolBar(self):
        '''
        初始化工具栏
        创建一个QAction实例exitAct，然后添加到designer已经创建的默认的工具栏toolBar里面
        '''
        exitAct = QAction(QIcon('image/exit.png'), 'Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.triggered.connect(qApp.quit)

        self.toolBar.addAction(exitAct)

    def initButton(self):
        '''

        '''
        self.btnClear.clicked.connect(self.clearButton_callback)  # 按下按钮调用回调函数
        self.btnClear.setToolTip("清除文本输入内容")  # 设置提示

        # self.btnBrowse.setStyleSheet("{border-image: url(/home/kindy/Files/python/gui/pyq/play.ico);}") # 此代码没有效果
        self.btnExchange.clicked.connect(self.exchangeButton_callback)  # 一旦按下按钮，连接槽函数进行处理
        self.btnExchange.setToolTip("转换翻译语言")

        self.btnTranslate.clicked.connect(self.transButton_callback)
        self.btnTranslate.setToolTip("翻译内容")

        self.btnCopy1.clicked.connect(self.btnCopy1_callback)
        self.btnCopy1.setToolTip("复制转换内容")

        self.btnCopyBaidu.clicked.connect(self.btnCopyBaidu_callback)
        self.btnCopyBaidu.setToolTip("复制百度翻译内容")

        self.btnCopyQQ.clicked.connect(self.btnCopyQQ_callback)
        self.btnCopyQQ.setToolTip("复制QQ翻译内容")

        self.clipboard = QApplication.clipboard()

    def clearButton_callback(self):
        self.transInput.clear()
        self.transInput.setFocus()

    def exchangeButton_callback(self):
        tmp1 = self.transFrom.currentText()
        if tmp1 != 'Auto':
            self.transFrom.setCurrentText(self.transTo.currentText())
            self.transTo.setCurrentText(tmp1)
        else:
            pass

    def btnCopy1_callback(self):
        self.clipboard.setText(self.transform.toPlainText())

    def btnCopyBaidu_callback(self):
        self.clipboard.setText(self.transOutputBaidu.toPlainText())

    def btnCopyQQ_callback(self):
        self.clipboard.setText(self.transOutputQQ.toPlainText())

    def transButton_callback(self, filename):
        '''
        按钮分别调用百度和QQAPI进行文字识别
        '''

        start = time.time()
        end = time.time()

        self.toLang = self.lang_transform(self.transTo.currentText())  # 目标语言
        self.fromLang = self.lang_transform(self.transFrom.currentText())  # 源语言
        self.content = self.transInput.toPlainText().replace('\n', '')

        # 显示去掉换行符后的文本
        self.transform.setPlainText(self.content)
        self.clipboard.setText(self.content)

        # 调用百度 API识别并显示
        transBaidu = self.get_translation_baidu(self.content)
        self.transOutputBaidu.setPlainText(transBaidu)
        self.transOutputBaidu.setStatusTip("翻译时间：%.2fs" % (end - start))

        # 调用QQ API识别并显示
        transQQ = self.get_translation_qq(self.content)
        self.transOutputQQ.setPlainText(transQQ)
        self.transOutputQQ.setStatusTip("翻译时间：%.2fs" % (end - start))


    def get_translation_baidu(self, query):
        sign = self.appKey + query + str(self.salt) + self.secretKey  # 签名
        m1 = md5()
        m1.update(sign.encode())
        sign = m1.hexdigest()  # 计算签名的哈希值
        self.myurl = self.myurl + '?appid=' + self.appKey + '&q=' + urllib.parse.quote(
            query) + '&from=' + self.fromLang + '&to=' + self.toLang + '&salt=' + str(self.salt) + '&sign=' + sign

        try:
            httpClient = httplib.HTTPConnection('api.fanyi.baidu.com')
            httpClient.request('GET', self.myurl)

            # response是HTTPResponse对象
            response = httpClient.getresponse()
            res = response.read().decode('unicode-escape')

            hjson = json.loads(res)
            exp = str(hjson['trans_result'][0]["dst"])

            return exp

        except Exception as e:
            print(e)
        finally:
            if httpClient:
                httpClient.close()


    def get_translation_qq(self, trans):
        # https://console.cloud.tencent.com/api/explorer?Product=tmt&Version=2018-03-21&Action=TextTranslate&SignVersion=

        # trans = "Pattern recognition has its origins in engineering"
        # params = '{"SourceText": "Pattern recognition has its origins in engineering","Source":"en","Target":"zh", "ProjectId":"1"}'

        params = '{' + '"SourceText": ' + '"' + trans + '"' + ',"Source":"en","Target":"zh", "ProjectId":"1"}'
        self.req.from_json_string(params)

        resp = self.client.TextTranslate(self.req)
        resp = resp.to_json_string()
        decode_json = json.loads(resp)
        result = decode_json['TargetText']
        return result


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyApp()
    sys.exit(app.exec_())
