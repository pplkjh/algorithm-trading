import sys
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *

class AlgorithmTrading(QMainWindow):
    def __init__(self):
        super().__init__()
        # 윈도우가 생성되자마자 자동 로그인 +  OpenAPI 연결
        self.kiwoom = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        self.kiwoom.dynamicCall("CommConnect()")
        self.kiwoom.OnEventConnect.connect(self.event_connect)
        self.kiwoom.OnReceiveTrData.connect(self.receive_trdata)

        ###### 화면 구성 ###################################
        # 윈도우 설정
        self.setGeometry(200, 300, 400, 150)
        self.setWindowTitle("종목조회")

        # 변경 불가능한 없는 Text
        label = QLabel('종목코드 ', self)
        label.move(25, 20)

        # 변경 가능한 Text 입력창
        self.code_edit = QLineEdit(self)
        self.code_edit.move(80, 20)

        # 종목 정보 조회 버튼
        btn1 = QPushButton("기본 정보 조회", self)
        btn1.move(20, 60)
        btn1.clicked.connect(self.btn1_clicked)

        # 매매 상위 10개 조회 버튼
        btn2 = QPushButton("매매 상위 조회", self)
        btn2.move(120, 60)
        btn2.clicked.connect(self.btn2_clicked)

        # 외국인 순매수 상위 10개 조회 버튼
        btn3 = QPushButton("외국인 순매수 상위", self)
        btn3.move(220, 60)
        btn3.clicked.connect(self.btn3_clicked)
        ###### 화면 구성 ###################################

    def event_connect(self, err_code):
        if err_code == 0:
            print("연결 완료")

    def btn1_clicked(self):
        code = self.code_edit.text()
        print("종목코드: " + code)

        # SetInputValue
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)

        # CommRqData
        self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "Request1", "opt10001", 0, "0101")

    def btn2_clicked(self):
        # SetInputValue
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "시장구분", 101)
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "기간", 20)

        # CommRqData
        self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "Request2", "OPT10036", 0, "0101")


    #######################  60 거래일내 코스닥 외국인 순매수 상위 10종목의 종목코드, 종목명, 순매수량 구하기 #################
    # SetInputValue와 CommRqData 채우기
    def btn3_clicked(self):        
        # SetInputValue
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "시장구분", 101)
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "매매구분", 2)        
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "기간", 60)

        # CommRqData
        self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "Request3", "OPT10034", 0, "0101")
    ##############################################################################################################################
    ##############################################################################################################################

    def receive_trdata(self, screen_no, rqname, trcode, recordname, prev_next, data_len, err_code, msg1, msg2):
        if rqname == "Request1":
            name = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, 0, "종목명")
            price = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname,0, "현재가")
            volume = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, 0, "거래량")
            PERv = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname,0, "PER")
            PBRv = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname,0, "PBR")
            ROEv = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname,0, "ROE")
            
            print("종목명 : " , name.strip())
            print("현재가 : " , price.strip().replace('+','').replace('-',''))
            print("거래량 : " , volume.strip())

            print("PER : " , PERv.strip())
            print("PBR : " , PBRv.strip())
            print("ROE : " , ROEv.strip())
        ##############################################################################################################################

        if rqname == "Request2":
            for i in range(10):
                code = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "종목코드")
                name = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "종목명")
                price = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "현재가")

                print(i+1,"번째 상위 매매 종목코드 : ", code.strip() ,
                      '종목명 : ', '  종목코드 : ', name.strip(),
                      "  현재가 : ", price.strip().replace('+','').replace('-','') )


        ####################### 60 거래일내 코스닥 외국인 순매수 상위 10종목의 종목코드, 종목명, 순매수량 구하기 #################
        if rqname == "Request3":
            for i in range(10):
                code = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "종목코드")
                name = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "종목명")
                #price = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "현재가")
                volume = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "순매수량")

                print(i+1,"번째 상위 매매 종목코드 : ", code.strip() ,
                      '종목명 : ', name.strip(),
                      '  순매수량 : ', volume.strip())
                      #"  현재가 : ", price.strip().replace('+','').replace('-','') )            # 코드 추가

        ##############################################################################################################################
        ##############################################################################################################################
        ##############################################################################################################################

if __name__ == "__main__":
    app = QApplication(sys.argv)
    Window_lec9_2 = AlgorithmTrading()
    Window_lec9_2.show()
    app.exec_()
