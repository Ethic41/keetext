from fbs_runtime.application_context.PyQt5 import ApplicationContext
from core.amazon_scraper.scraper import Scraper
from ui.keetext import KeetextGui

import sys

def main():
    appctxt = ApplicationContext()       # 1. Instantiate ApplicationContext
    window = KeetextGui()
    window.show()
    exit_code = appctxt.app.exec_()      # 2. Invoke appctxt.app.exec_()
    sys.exit(exit_code)


if __name__ == '__main__':
    main()

    