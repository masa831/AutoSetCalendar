import logging
from logging import getLogger, StreamHandler, Formatter
from datetime import datetime

class CstmLogger:
    """logging用クラス

    Attributes:
        output_file_flg(boolean): logファイル出力のON/OFF
        log_file(str): logファイル名を意図的に指定したい場合に入力

    Examples:
        インスタンス生成時
        # 標準出力のみ
        log = cstm_logging.CstmLogger()
        # 標準出力 & ファイル出力 ファイル名はデフォルト定義
        log = cstm_logging.CstmLogger(output_file_flg=True)
        # 標準出力 & ファイル出力 ファイル名を指定
        log = cstm_logging.CstmLogger(output_file_flg=True, log_file="test.log")
        
        インスタンス生成後
        # 開始時
        log.set_handler()
        # 任意の場所でdebug関数を使用
        log.debug("hello")
        log.debug("日本語文字化けの確認用：[林檎, 檸檬, 葡萄]")
        log.debug("world")
        # 終了時
        log.release_handler()

    """

    def __init__(self, output_file_flg=False, log_file=""):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.output_file_flg = output_file_flg
        self.formatter = logging.Formatter('%(asctime)s - %(message)s')
        if log_file=="":
            self.log_file = datetime.now().strftime("%Y%m%d%H%M%S") + "log.log"
        else:
            self.log_file = log_file


    def set_handler(self):
        """ハンドラーのセット関数
        """
        self.handler_stream = logging.StreamHandler()
        self.handler_stream.setLevel(logging.DEBUG)
        self.handler_stream.setFormatter(self.formatter)
        self.logger.addHandler(self.handler_stream)

        if self.output_file_flg==1:
            self.handler_file = logging.FileHandler(filename=self.log_file, mode="a", encoding="utf-8")
            self.handler_file.setLevel(logging.DEBUG)
            self.handler_file.setFormatter(self.formatter)
            self.logger.addHandler(self.handler_file)

    def debug(self, message):
        """ログ関数
        """
        self.logger.debug(message)

    def release_handler(self):
        """ハンドラーのリリース関数
        """
        if self.handler_stream in self.logger.handlers:
            self.logger.removeHandler(self.handler_stream)
            self.handler_stream.close()
        if self.output_file_flg==1 and self.handler_file in self.logger.handlers:
            self.logger.removeHandler(self.handler_file)
            self.handler_file.close()

