"""Utilities for testing Kiwoom OpenAPI requests through a tiny UI."""

import sys
from typing import Optional, Tuple

from PyQt5.QAxContainer import QAxWidget
from PyQt5.QtWidgets import (
    QApplication,
    QGridLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QWidget,
)


class AlgorithmTrading(QMainWindow):
    """PyQt window that wraps a subset of Kiwoom OpenAPI functionality."""

    SCREEN_TR_ACCOUNT = "0101"
    SCREEN_TR_BALANCE = "0101"
    SCREEN_SEND_ORDER = "0101"

    def __init__(self) -> None:
        super().__init__()
        self.kiwoom = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        self.account_label: Optional[QLabel] = None
        self.code_edit: Optional[QLineEdit] = None
        self.quantity_edit: Optional[QLineEdit] = None

        self._connect_to_open_api()
        self._setup_signals()
        self._build_ui()

    # ------------------------------------------------------------------
    # UI setup helpers
    # ------------------------------------------------------------------
    def _connect_to_open_api(self) -> None:
        """Trigger the OpenAPI login procedure as soon as the window opens."""

        self.kiwoom.dynamicCall("CommConnect()")

    def _setup_signals(self) -> None:
        """Register event handlers for Kiwoom callbacks."""

        self.kiwoom.OnEventConnect.connect(self.event_connect)
        self.kiwoom.OnReceiveTrData.connect(self.receive_trdata)
        self.kiwoom.OnReceiveChejanData.connect(self.receive_chejan_data)

    def _build_ui(self) -> None:
        """Construct the widget hierarchy for the main window."""

        self.setWindowTitle("Send Order")
        central_widget = QWidget(self)
        layout = QGridLayout(central_widget)

        layout.addWidget(QLabel("계좌번호", self), 0, 0)
        self.account_label = QLabel("-", self)
        layout.addWidget(self.account_label, 0, 1)

        layout.addWidget(QLabel("종목코드", self), 1, 0)
        self.code_edit = QLineEdit(self)
        self.code_edit.setPlaceholderText("A000660")
        layout.addWidget(self.code_edit, 1, 1)

        layout.addWidget(QLabel("수량", self), 2, 0)
        self.quantity_edit = QLineEdit(self)
        self.quantity_edit.setPlaceholderText("1")
        layout.addWidget(self.quantity_edit, 2, 1)

        account_btn = QPushButton("계좌 조회", self)
        account_btn.clicked.connect(self.btn1_clicked)
        layout.addWidget(account_btn, 3, 0)

        balance_btn = QPushButton("잔고 조회", self)
        balance_btn.clicked.connect(self.btn2_clicked)
        layout.addWidget(balance_btn, 3, 1)

        holdings_btn = QPushButton("보유종목", self)
        holdings_btn.clicked.connect(self.btn3_clicked)
        layout.addWidget(holdings_btn, 4, 0)

        buy_btn = QPushButton("매수 테스트", self)
        buy_btn.clicked.connect(self.btn4_clicked)
        layout.addWidget(buy_btn, 4, 1)

        sell_btn = QPushButton("매도 테스트", self)
        sell_btn.clicked.connect(self.btn5_clicked)
        layout.addWidget(sell_btn, 5, 1)

        self.setCentralWidget(central_widget)

    # ------------------------------------------------------------------
    # Kiwoom callbacks
    # ------------------------------------------------------------------
    def event_connect(self, err_code: int) -> None:
        if err_code == 0:
            print("연결 완료")
        else:
            QMessageBox.critical(self, "오류", f"OpenAPI 연결 실패 (code: {err_code})")

    def btn1_clicked(self) -> None:
        """Fetch the logged-in account number and show it in the UI."""

        acc_num = self.kiwoom.dynamicCall("GetLoginInfo(QString)", ["ACCNO"])
        if self.account_label:
            self.account_label.setText(acc_num.replace(";", ""))

    def btn2_clicked(self) -> None:
        """Request the account balance summary (예수금)."""

        account = self._current_account()
        if not account:
            return

        self.kiwoom.dynamicCall(
            "SetInputValue(QString, QString)", "계좌번호", account
        )
        self.kiwoom.dynamicCall(
            "CommRqData(QString, QString, int, QString)",
            "Request19-1",
            "opw00001",
            0,
            self.SCREEN_TR_ACCOUNT,
        )

    def btn3_clicked(self) -> None:
        """Request the list of holdings for the selected account."""

        account = self._current_account()
        if not account:
            return

        self.kiwoom.dynamicCall(
            "SetInputValue(QString, QString)", "계좌번호", account
        )
        self.kiwoom.dynamicCall(
            "CommRqData(QString, QString, int, QString)",
            "Request19-2",
            "opw00018",
            0,
            self.SCREEN_TR_BALANCE,
        )

    def btn4_clicked(self) -> None:
        """Submit a market buy order with the provided code and quantity."""

        self._send_order(order_type=1)

    def btn5_clicked(self) -> None:
        """Submit a market sell order with the provided code and quantity."""

        self._send_order(order_type=2)

    def receive_trdata(
        self,
        screen_no,
        rqname,
        trcode,
        recordname,
        prev_next,
        data_len,
        err_code,
        msg1,
        msg2,
    ):
        if rqname == "Request19-1":
            deposit = self.kiwoom.dynamicCall(
                "CommGetData(QString, QString, QString, int, QString)",
                trcode,
                "",
                rqname,
                0,
                "d+2추정예수금",
            )
            print("D+2 예수금 : ", deposit.lstrip("0"))
        elif rqname == "Request19-2":
            p_price = self._clean_number(
                self.kiwoom.dynamicCall(
                    "CommGetData(QString, QString, QString, int, QString)",
                    trcode,
                    "",
                    rqname,
                    0,
                    "총매입금액",
                )
            )
            e_price = self._clean_number(
                self.kiwoom.dynamicCall(
                    "CommGetData(QString, QString, QString, int, QString)",
                    trcode,
                    "",
                    rqname,
                    0,
                    "총평가금액",
                )
            )
            profit = self._clean_number(
                self.kiwoom.dynamicCall(
                    "CommGetData(QString, QString, QString, int, QString)",
                    trcode,
                    "",
                    rqname,
                    0,
                    "총평가손익금액",
                )
            )
            ret = self._clean_rate(
                self.kiwoom.dynamicCall(
                    "CommGetData(QString, QString, QString, int, QString)",
                    trcode,
                    "",
                    rqname,
                    0,
                    "총수익률(%)",
                )
            )
            balance = self._clean_number(
                self.kiwoom.dynamicCall(
                    "CommGetData(QString, QString, QString, int, QString)",
                    trcode,
                    "",
                    rqname,
                    0,
                    "추정예탁자산",
                )
            )

            print(
                "총매입금액 : ",
                p_price,
                "  총평가금액 : ",
                e_price,
                "  평가손익 : ",
                profit,
                "  수익률 : ",
                ret,
                "  추정자산 : ",
                balance,
            )

            n = self.kiwoom.dynamicCall(
                "GetRepeatCnt(QString, QString)", trcode, rqname
            )
            for i in range(n):
                name = self.kiwoom.dynamicCall(
                    "CommGetData(QString, QString, QString, int, QString)",
                    trcode,
                    "",
                    rqname,
                    i,
                    "종목명",
                ).rstrip(" ")
                quantity = self._clean_number(
                    self.kiwoom.dynamicCall(
                        "CommGetData(QString, QString, QString, int, QString)",
                        trcode,
                        "",
                        rqname,
                        i,
                        "보유수량",
                    )
                )
                price1 = self._clean_number(
                    self.kiwoom.dynamicCall(
                        "CommGetData(QString, QString, QString, int, QString)",
                        trcode,
                        "",
                        rqname,
                        i,
                        "매입가",
                    )
                )
                price2 = self._clean_number(
                    self.kiwoom.dynamicCall(
                        "CommGetData(QString, QString, QString, int, QString)",
                        trcode,
                        "",
                        rqname,
                        i,
                        "현재가",
                    )
                )
                profit1 = self._clean_number(
                    self.kiwoom.dynamicCall(
                        "CommGetData(QString, QString, QString, int, QString)",
                        trcode,
                        "",
                        rqname,
                        i,
                        "평가손익",
                    )
                )
                ret1 = self._clean_rate(
                    self.kiwoom.dynamicCall(
                        "CommGetData(QString, QString, QString, int, QString)",
                        trcode,
                        "",
                        rqname,
                        i,
                        "수익률(%)",
                    )
                )
                jongcode1 = self.kiwoom.dynamicCall(
                    "CommGetData(QString, QString, QString, int, QString)",
                    trcode,
                    "",
                    rqname,
                    i,
                    "종목번호",
                ).replace("A", "").lstrip(" ")

                print(
                    f"[보유종목{i + 1}] 종목코드 : {jongcode1} 종목명 : {name}  "
                    f"보유수량 : {quantity} 매입가 : {price1} 현재가 : {price2} "
                    f"평가손익 : {profit1} 수익률 : {ret1}"
                )

    def receive_chejan_data(self, gubun, item_cnt, fid_list):
        print(gubun)
        print("주문번호 : ", self.kiwoom.dynamicCall("GetChejanData(int)", 9203))
        print("종목명 : ", self.kiwoom.dynamicCall("GetChejanData(int)", 302))
        print("주문수량 : ", self.kiwoom.dynamicCall("GetChejanData(int)", 900))
        print("주문가격 : ", self.kiwoom.dynamicCall("GetChejanData(int)", 901))

    # ------------------------------------------------------------------
    # Helper methods
    # ------------------------------------------------------------------
    def _current_account(self) -> Optional[str]:
        if not self.account_label:
            return None

        account = self.account_label.text().strip()
        if not account or account == "-":
            QMessageBox.warning(self, "계좌 조회", "먼저 계좌 조회를 실행해 주세요.")
            return None
        return account

    def _code_and_quantity(self) -> Optional[Tuple[str, int]]:
        if not self.code_edit or not self.quantity_edit:
            return None

        code = self.code_edit.text().strip()
        quantity_text = self.quantity_edit.text().strip()

        if not code or not quantity_text:
            QMessageBox.warning(self, "입력값 오류", "종목코드와 수량을 모두 입력해 주세요.")
            return None

        try:
            quantity = int(quantity_text)
        except ValueError:
            QMessageBox.warning(self, "입력값 오류", "수량은 정수로 입력해야 합니다.")
            return None

        return code, quantity

    def _send_order(self, order_type: int) -> None:
        account = self._current_account()
        if not account:
            return

        code_quantity = self._code_and_quantity()
        if not code_quantity:
            return

        code, quantity = code_quantity
        try:
            self.kiwoom.dynamicCall(
                "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                [
                    "Request19-3",
                    self.SCREEN_SEND_ORDER,
                    account,
                    order_type,
                    code,
                    quantity,
                    0,
                    "03",
                    "",
                ],
            )
        except Exception as exc:  # pragma: no cover - defensive catch for COM errors
            QMessageBox.critical(self, "주문 실패", f"주문 중 오류가 발생했습니다:\n{exc}")

    @staticmethod
    def _clean_number(value: str) -> str:
        """Remove extra whitespace and leading zeros while keeping signs."""

        value = str(value).strip()
        if value.startswith("-"):
            return "-" + value[1:].lstrip("0")
        return value.lstrip("0")

    @staticmethod
    def _clean_rate(value: str) -> str:
        value = AlgorithmTrading._clean_number(value)
        if value.startswith("."):
            return "0" + value
        if value.startswith("-."):
            return value.replace("-.", "-0.")
        return value


def main() -> None:
    app = QApplication(sys.argv)
    window = AlgorithmTrading()
    window.show()
    app.exec_()


if __name__ == "__main__":
    main()
