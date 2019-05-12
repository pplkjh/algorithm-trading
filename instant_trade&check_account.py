import sys
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *

class AlgorithmTrading(QMainWindow):
    def __init__(self):
        super().__init__()
        # 윈도우가 생성되자마자 자동 로그인 +  OpenAPI 연결
        self.kiwoom = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        self.kiwoom.dynamicCall("CommConnect()")
        #로그인시 onvevent connect이벤트 발생
        self.kiwoom.OnEventConnect.connect(self.event_connect)
        # TR후 이벤트 발생하게 하는거
        self.kiwoom.OnReceiveTrData.connect(self.receive_trdata)
        # 체결 후 이벤트 발생하게 하는거
        self.kiwoom.OnReceiveChejanData.connect(self.receive_chejan_data)

        ###### 화면 구성 ###################################
        # 윈도우 설정
        self.setGeometry(200, 300, 450, 200)
        self.setWindowTitle("Send Order")

        # 변경 불가능한 없는 Text
        label1 = QLabel('계좌번호 : ', self)
        label1.move(25, 20)

        # 계좌 정보 표시 화면
        # 프로그램 실행 중 변경되기 때문에 self에 종속시키는 것을 확인
        self.label2 = QLabel('',self)
        self.label2.move(100, 20)

        # 변경 불가능한 없는 Text
        label3 = QLabel('종목코드', self)
        label3.move(25, 60)

        # 변경 가능한 Text 입력창
        self.code_edit1 = QLineEdit(self)
        self.code_edit1.move(100, 60)

        # 변경 불가능한 없는 Text
        label4 = QLabel('수량', self)
        label4.move(25, 100)

        # 변경 가능한 Text 입력창
        self.code_edit2 = QLineEdit(self)
        self.code_edit2.move(100, 100)

        # 종목 정보 조회 버튼
        btn1 = QPushButton("계좌 조회", self)
        btn1.move(20, 140)
        btn1.clicked.connect(self.btn1_clicked)

        btn2 = QPushButton("잔고 조회 ", self)
        btn2.move(120, 140)
        btn2.clicked.connect(self.btn2_clicked)

        btn3 = QPushButton("보유종목", self)
        btn3.move(220, 140)
        btn3.clicked.connect(self.btn3_clicked)

        btn4 = QPushButton("매수테스트", self)
        btn4.move(320, 140)
        btn4.clicked.connect(self.btn4_clicked)
        
        btn5 = QPushButton("매도테스트", self)
        btn5.move(320, 110)
        btn5.clicked.connect(self.btn5_clicked)


    def event_connect(self, err_code):
        if err_code == 0:
            print("연결 완료")

    def btn1_clicked(self):
        # SetInputValue
        acc_num = self.kiwoom.dynamicCall("GetLoginInfo(QString)", ["ACCNO"])
        self.label2.setText(acc_num.replace(';',''))

    def btn2_clicked(self):
        # SetInputValue
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.label2.text())
        # CommRqData
        self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "Request19-1", "opw00001", 0, "0101")


    def btn3_clicked(self):  # 보유 종목 조회
        # 한 요청에 최대 20개의 보유종목만 조회가능하므로, 20개 이상인 경우 반복문으로 코딩
        # SetInputValue
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.label2.text())
        # CommRqData
        self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "Request19-2", "opw00018", 0, "0101")


    def btn4_clicked(self): # Send order
        if (self.code_edit1.text() == '') | (self.code_edit2.text() == ''):
            print('입력값 오류')
            return
        try: # 시장가(03) 매수(1) 테스트만 진행
            self.kiwoom.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                                    ["Request19-3", "0101", self.label2.text(), 1, self.code_edit1.text(), int(self.code_edit2.text()), 0, "03", ""])
        except:
            print('입력값 오류')
            
    def btn5_clicked(self): # Send order
        if (self.code_edit1.text() == '') | (self.code_edit2.text() == ''):
            print('입력값 오류')
            return
        try: # 시장가(03) 매수(1) 테스트만 진행
            self.kiwoom.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                                    ["Request19-3", "0101", self.label2.text(), 2, self.code_edit1.text(), int(self.code_edit2.text()), 0, "03", ""])
        except:
            print('입력값 오류')

    def receive_trdata(self, screen_no, rqname, trcode, recordname, prev_next, data_len, err_code, msg1, msg2):
        if rqname == "Request19-1":
            deposit = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, 0, "d+2추정예수금")
            print("D+2 예수금 : ",deposit.lstrip("0")) # 0이 포함되어 있기 때문에, 숫자 왼쪽의 0을 제거
        elif rqname == "Request19-2":
            p_price = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, 0, "총매입금액").lstrip("0")
            e_price = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, 0, "총평가금액").lstrip("0")
            profit = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, 0, "총평가손익금액")
            ret = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, 0, "총수익률(%)")
            balance = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, 0, "추정예탁자산").lstrip("0")
            
            ret=str(ret)
            profit=str(profit)
            if (profit.find("-") != -1):  # 0이 포함되어 있기 때문에 앞의 부호를 제거 한 후, 숫자 왼쪽의 0을 제거
                profit = "-" + profit.replace("-","").lstrip("0")
                ret = "-" + ret.replace("-", "").lstrip("0")
            else:
                profit = profit.lstrip("0")
                ret= ret.lstrip("0")
            if ret.find("-.")!=-1:  # 0.x% 를 표현해주기 위함
                ret = ret.replace("-.","-0.")
                #ret=int(ret)
            elif ret.find(".")==0:
                ret = ret.replace(".", "0.")
                #ret=int(ret)
                
            print("총매입금액 : ",p_price,"  총평가금액 : ", e_price, "  평가손익 : ", profit, "  수익률 : ", ret, "  추정자산 : ", balance)

            n = self.kiwoom.dynamicCall("GetRepeatCnt(QString, QString)", trcode, rqname)
            for i in range(n):
                name = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "종목명")
                quantity = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "보유수량").lstrip("0")
                price1 = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "매입가").lstrip("0")
                price2 = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "현재가").lstrip("0")
                profit1 = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "평가손익")
                ret1 = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "수익률(%)")
                jongcode1 = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "종목번호")
                jongcode1 = jongcode1.replace("A","").lstrip(" ")
                
                profit1=str(profit1)
                ret1=str(ret1)
                if (profit1.find("-") != -1):  # 0이 포함되어 있기 때문에 앞의 부호를 제거 한 후, 숫자 왼쪽의 0을 제거
                    profit1 = "-" + profit1.replace("-", "").lstrip("0")
                    ret1 = "-" + ret1.replace("-", "").lstrip("0")
                else:
                    profit1 = profit1.lstrip("0")
                    ret1=ret1.lstrip("0")
                    
                if ret1.find("-.") != -1:
                    ret1 = ret1.replace("-.", "-0.")

                elif ret1.find(".") == 0:
                    ret1 = ret1.replace(".", "0.")
 
                    
                print("[보유종목"+str(i+1)+"]","종목코드 : ",jongcode1, "종목명 : ", name.rstrip(" ") , "  보유수량 : ", quantity , "매입가 : ", price1 , "현재가 : ", price2, "평가손익 : " , profit1, "수익률 : " , ret1)

    def receive_chejan_data(self, gubun, item_cnt, fid_list):
        print(gubun)
        print("주문번호 : ", self.kiwoom.dynamicCall("GetChejanData(int)", 9203))
        print("종목명 : ", self.kiwoom.dynamicCall("GetChejanData(int)", 302))
        print("주문수량 : ", self.kiwoom.dynamicCall("GetChejanData(int)", 900))
        print("주문가격 : ", self.kiwoom.dynamicCall("GetChejanData(int)", 901))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    Window_lec10 = AlgorithmTrading()
    Window_lec10.show()
    app.exec_()
