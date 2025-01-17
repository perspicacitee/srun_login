import time
import getpass
from apis import LoginManager


def always_login(username, password, checkinterval):
    lm = LoginManager()
    login = lambda: lm.login(username=username, password=password)
    timestamp = lambda: print(time.asctime(time.localtime(time.time())))

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

    always_login(username, password, checkinterval)
