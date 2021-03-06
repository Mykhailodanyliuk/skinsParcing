import requests
import lxml
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time

weapons = ['CZ75-Auto', 'Desert Eagle', 'Dual Berettas', 'Five-SeveN', 'Glock-18', 'P2000', 'P250', 'R8 Revolver',
           'Tec-9', 'USP-S', 'AK-47', 'M4A4',
           'AUG', 'AWP', 'FAMAS', 'G3SG1', 'Galil AR', 'M4A1-S']


def find_sale_weapon():
    for weapon in weapons:
        print(weapon)
        weapon = weapon.replace(' ', '+')
        site = requests.get(f'https://csgostash.com/weapon/{weapon}')
        soup = BeautifulSoup(site.text, 'lxml')
        items = soup.find_all('div', class_='col-lg-4 col-md-6 col-widen text-center')
        for item in items:
            ua = UserAgent()
            header = {'User-Agent': str(ua.chrome)}
            name_skin = (item.find('h3').text)
            steam_link = f'https://steamcommunity.com/market/search?q={weapon}+%7C+{name_skin}'
            steam_site = requests.get(steam_link, headers=header)
            steam_soup = BeautifulSoup(steam_site.text, 'lxml')
            searchResultsRows = steam_soup.find('div', id='searchResultsRows')
            try:
                result_weapons = searchResultsRows.find_all('a')
            except:
                print('No site')
                continue
            for result_weapon in result_weapons:
                name_weapon = result_weapon.find('div')['data-hash-name'].replace(' ','+')
                price_weapon = result_weapon.find('span', class_='sale_price')\
                    .text.replace('$', '').replace(' USD','').replace(',', '')
                bitskins_link = f'https://bitskins.com/?appid=730&page=1&market_hash_name={name_weapon}&advanced=1&is_stattrak=0&has_stickers=0&is_souvenir=-1&show_trade_delayed_items=0&sort_by=price&order=asc'
                bitskins_search = requests.get(bitskins_link)
                bitskins_soup = BeautifulSoup(bitskins_search.text, 'lxml')
                items = bitskins_soup.find('div', class_='col-lg-3 col-md-4 col-sm-5 col-xs-12 item-solo')
                try:
                    m1 = items.find('div', class_='panel panel-default')
                    m2 = m1.find('div', class_='item-icon lazy')
                except:
                    continue
                m3 = m2.find('h5')
                bitskins_seller_price = m3.find('span', class_='item-price-display').text.replace('$', '').replace(',','')
                # print(name_weapon, price_weapon,bitskins_seller_price)
                if float(price_weapon) / float(bitskins_seller_price) > 1.05 and float(price_weapon) > 0.3:
                    try:
                        service = Service("chromedriver.exe")
                        service.start()
                        option = webdriver.ChromeOptions()
                        option.add_argument('headless')
                        driver = webdriver.Remote(service.service_url, options=option)
                        steam_weapon_link = f'{result_weapon["href"]}'
                        driver.get(steam_weapon_link)
                        time.sleep(2)
                        gun_soup = BeautifulSoup(driver.page_source, 'lxml')
                        price_block = gun_soup.find_all('span', class_='market_commodity_orders_header_promote')
                        real_price = price_block[1].text
                        real_price = float(real_price.replace('$', ''))
                        driver.close()
                        if real_price / float(bitskins_seller_price) > 1.1 and float(price_weapon) > 0.3:
                            discount = (real_price - float(bitskins_seller_price)) / float(bitskins_seller_price)
                            print('//////////////////////////////////////////')
                            print('Discount' , weapon, name_weapon, real_price, bitskins_seller_price, str(discount * 100) + '%')
                            print(bitskins_link)
                            print(steam_weapon_link)
                            print('///////////////////////////////////////////')
                    except:
                        print('Error')
                        continue


def main():
    find_sale_weapon()


if __name__ == '__main__':
    main()
