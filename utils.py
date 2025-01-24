import logging


class LoginLogger:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(LoginLogger, cls).__new__(cls)
        return cls._instance

    def __init__(self, logger_name="LoginManager", logger_file="default.log", debug=False) -> None:
        if not hasattr(self, 'initialized'):  # 防止重复初始化
            self.logger = logging.getLogger(logger_name)
            handler = logging.FileHandler(logger_file)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            if debug:
                console_handler = logging.StreamHandler()
                console_handler.setFormatter(formatter)
                self.logger.addHandler(console_handler)
                self.logger.setLevel(logging.DEBUG)
            else:
                self.logger.setLevel(logging.INFO)
            self.initialized = True

    def info(self, msg):
        self.logger.info(msg)

    def debug(self, msg):
        self.logger.debug(msg)
    
    def error(self, msg):
        self.logger.error(msg)
