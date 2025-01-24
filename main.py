import time
import getpass
from utils import LoginLogger


def always_login(username, password, checkinterval):
    logger = LoginLogger()
    lm = LoginManager()
    login = lambda: lm.login(username=username, password=password)
    timestamp = lambda: logger.info(time.asctime(time.localtime(time.time())))

    timestamp()
    try:
        login()
    except Exception:
        pass
    
    while True:
        time.sleep(checkinterval)
        try:
            login()
        except Exception:
            pass


if __name__ == "__main__":
    username = "421542"
    password = getpass.getpass("Please enter your password (will not show): ")
    checkinterval = 5 * 60
    debug=False
    logger_file = "default.log"
    logger = LoginLogger(logger_file=logger_file, debug=debug)

    from apis import LoginManager
    always_login(username, password, checkinterval)
