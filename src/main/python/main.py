from fbs_runtime.application_context.PyQt5 import ApplicationContext
from core.amazon_scraper.scraper import Scraper
from ui.keetext import KeetextGui

import sys


def test():
    my_scraper = Scraper()
    categories_soup = my_scraper.make_categories_soup()
    categories = my_scraper.get_categories(categories_soup)
    subcategories = my_scraper.get_subcategories(categories, categories_soup)
    my_scraper.chosen_subcategories = subcategories

    my_scraper.get_not_available_subcategory_page(3)
    my_scraper.find_valid_items()

if __name__ == '__main__':
    # test()
    appctxt = ApplicationContext()       # 1. Instantiate ApplicationContext
    window = KeetextGui()
    window.show()
    exit_code = appctxt.app.exec_()      # 2. Invoke appctxt.app.exec_()
    sys.exit(exit_code)

    