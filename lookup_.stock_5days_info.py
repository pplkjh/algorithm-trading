import sys
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
import time
import pandas as pd
import numpy as np
 
class AlgorithmTrading(QMainWindow):
    def __init__(self):
        super().__init__()
        # 윈도우가 생성되자마자 자동 로그인 +  OpenAPI 연결
        self.kiwoom = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        self.kiwoom.dynamicCall("CommConnect()")
        self.kiwoom.OnEventConnect.connect(self.event_connect)
        self.kiwoom.OnReceiveTrData.connect(self.receive_trdata)

        self.codelist=[]
        self.namelist=[]
        
        ###### 화면 구성 ###################################
        # 윈도우 설정
        self.setGeometry(200, 300, 400, 150)
        self.setWindowTitle("Time-series")

        # 변경 불가능한 없는 Text
        label1 = QLabel('종목코드 ', self)
        label1.move(25, 20)

        # 변경 가능한 Text 입력창
        self.code_edit1 = QLineEdit(self)
        self.code_edit1.move(80, 20)

        # 변경 불가능한 없는 Text
        label2 = QLabel('기간 ', self)
        label2.move(25, 60)

        # 변경 가능한 Text 입력창
        self.code_edit2 = QLineEdit(self)
        self.code_edit2.move(80, 60)

        # 종목 정보 조회 버튼
        btn1 = QPushButton("기간별 종목 주가", self)
        btn1.move(20, 100)
        btn1.clicked.connect(self.btn1_clicked)

        #  코스닥 20거래일 매매 상위 10개의 기간별(5거래일) 종목 주가 조회 버튼
        btn2 = QPushButton("매매 상위 기간별", self)
        btn2.move(140, 100)
        btn2.clicked.connect(self.btn2_clicked)
        
        #self.code_list=[]
        #self.cost=[]
        
    def event_connect(self, err_code):
        if err_code == 0:
            print("연결 완료")

    def btn1_clicked(self):
        code = self.code_edit1.text()

        # SetInputValue
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)

        # CommRqData
        self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "Request1", "opt10005", 0, "0101")

        self.kiwoom.tr_event_loop = QEventLoop()
        self.kiwoom.tr_event_loop.exec_()
        
    #######################  코스닥 20거래일 매매 상위 10개의 기간(5거래일)별 종목 주가 조회 버튼 #################
    def btn2_clicked(self):
        # SetInputValue
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "시장구분", 101)
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "기간", 20)
        # CommRqData
        namenum=0
        self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "Request2", "OPT10036", 0, "0101")
        self.kiwoom.tr_event_loop = QEventLoop()
        self.kiwoom.tr_event_loop.exec_()


        #print(self.codelist)          ----- arrange codelist

        for code in self.codelist :

            print("종목 코드: ", code,"  종목 이름: ",self.namelist[namenum] ,'------------------ ')
            # SetInputValue
            self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
            
            # CommRqData
            self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "Request3", "opt10005", 0, "0101")
            self.kiwoom.tr_event_loop = QEventLoop()
            self.kiwoom.tr_event_loop.exec_()
            namenum=namenum+1
            time.sleep(1)
    ##################################################################################################################
    ##################################################################################################################


    def receive_trdata(self, screen_no, rqname, trcode, recordname, prev_next, data_len, err_code, msg1, msg2):
        if rqname == "Request1":
            for i in range(int(self.code_edit2.text())):
                _date = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "날짜")
                name = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "종목명")
                price = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname,i, "종가")
                volume = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "거래량")

                print("날짜 : ", _date.strip())
                print("종목명 : " , name.strip(),"   종가 : " , price.strip().replace('+','').replace('-',''),"   거래량 : " , volume.strip())


        ####################### 코스닥 20거래일 매매 상위 10개의 기간(5거래일)별 종목 주가 조회 버튼 #################
            # 코드 추가, 단 필요하다면 주석 영역 밖의 코드를 변경해도 됨
        elif rqname == "Request2":
            for i in range(10):
                code = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "종목코드").strip()
                name = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "종목명").strip()

                self.codelist.append(code)
                self.namelist.append(name)
        elif rqname == "Request3":
            for i in range(5):
                
                _date = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "날짜")
                price = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname,i, "종가")
                volume = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "거래량")

                print("날짜 : ", _date.strip())
                print(" 종가 : " , price.strip().replace('+','').replace('-',''),"   거래량 : " , volume.strip())

        try:
            self.kiwoom.tr_event_loop.exit()
        except AttributeError:
            pass
        ##################################################################################################################
        ##################################################################################################################
        ##################################################################################################################

if __name__ == "__main__":
    app = QApplication(sys.argv)
    Window_lec10 = AlgorithmTrading()
    Window_lec10.show()
    app.exec_()
