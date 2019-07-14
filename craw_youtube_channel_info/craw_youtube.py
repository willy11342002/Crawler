import time, re, datetime, sys
from selenium import webdriver
import configparser
import selenium
import pandas as pd

config = configparser.ConfigParser()
config.read('config.property', encoding='utf8')

now = lambda :datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')

driver = webdriver.Chrome('../chromedriver.exe')
driver.minimize_window()
driver.maximize_window()

df = pd.DataFrame(columns=['頻道名', '訂閱數', '影片名', '發布日期', '喜歡', '不喜歡', '影片網址', '影片流量'])

log = open(f'log/{datetime.date.today().strftime("%Y%m%d")}.log', 'w', encoding='utf8')
err = open(f'log/{datetime.date.today().strftime("%Y%m%d")}.err.log', 'w', encoding='utf8')
try:
    log.write(f'{now()} Step 0 ... 讀取config.property\n')
    log.write(f'{now()} 完成，共計讀取到 {len(config["CHANNEL"])} 筆資料\n')
    log.write('=======================================\n')
    log.write(f'{now()} Step 1 ... 根據設定檔逐一爬取資料\n')
    for idx, line in enumerate( config['CHANNEL'].items() ):
        name, url = line
        max_slice = int(config['BASE']['max'])
        log.write('----------------------------------\n')
        log.write(f'{now()} Step 1.{idx}.1 ... {name}，跳轉到網址進行爬取\n')
        driver.get(url)

        log.write(f'{now()} Step 1.{idx}.2 ... {name}，針對瀑布流網站進行頁面跳轉\n')
        while max_slice != 0:
            max_slice -= 1
            scrollHeight = driver.execute_script("return document.getElementsByTagName('ytd-app')[0].scrollHeight")
            driver.execute_script(f"window.scroll(0,{scrollHeight})")
            time.sleep(1)
            if scrollHeight == driver.execute_script("return document.getElementsByTagName('ytd-app')[0].scrollHeight"):
                break
                
        log.write(f'{now()} Step 1.{idx}.3 ... {name}，訂閱者數量抓取\n')
        cnt = driver.find_element_by_css_selector('#subscriber-count').text
        cnt = re.search('[0-9]+', cnt.replace(',', '')).group()
        
        log.write(f'{now()} Step 1.{idx}.4 ... {name}，頁面元素解析\t')
        elements = driver.find_elements_by_css_selector('ytd-grid-video-renderer')
        v_subscriber = driver.find_element_by_css_selector('#subscriber-count').text
        v_subscriber = re.search('[0-9]+', v_subscriber.replace(',', '')).group()
        v_names = [e.find_element_by_css_selector('h3').text for e in elements]
        v_hrefs = [e.find_element_by_css_selector('a').get_attribute('href') for e in elements]
        
        log.write(f'，完成，共計讀取到 {len(v_hrefs)} 筆資料\n')
        for i,href in enumerate(v_hrefs):
            driver.get(href)
            for t in range(5):
                log.write(f'{now()} Step 1.{idx}.4.{i} .. {v_names[i]}，第{t}次嘗試內容解析\t')
                try:    
                    time.sleep(1)
                    
                    v_view = driver.find_element_by_xpath('//*[@id="count"]/yt-view-count-renderer/span[1]').text
                    v_view = re.search('[,0-9]+', v_view).group().replace(',', '')
                    
                    v_hate = driver.find_element_by_xpath('//*[@id="top-level-buttons"]/ytd-toggle-button-renderer[2]/a').text.replace(',', '')
                    
                    v_like = driver.find_element_by_xpath('//*[@id="top-level-buttons"]/ytd-toggle-button-renderer[1]/a').text.replace(',', '')
                    
                    v_date = driver.find_element_by_xpath('//*[@id="upload-info"]/span').text
                    v_date = '/'.join(re.search('發佈日期：(?P<yyyy>[0-9]+)年(?P<mm>[0-9]+)月(?P<dd>[0-9]+)日', v_date).groups())
                    
                    df.loc[len(df)] = [name, v_subscriber, v_names[i], v_date, v_like, v_hate, href, v_view]
                    log.write('成功。\n')
                    break
                except selenium.common.exceptions.NoSuchElementException as e:
                    log.write('失敗。\n')
                    err.write(str(e))
                    continue
                except Exception as e:
                    log.write('失敗。\n')
                    err.write(str(e))
                    continue
                    

    
    log.write('=======================================')
    log.write(f'{now()} Step 2 ... 輸出文字檔\n')
    df.to_csv('output.csv', index=None, encoding='utf8')
    log.write(f'{now()} 完成，共計輸出 {len(df)} 筆資料\n')
    driver.close()
    log.write('=======================================\n')
except Exception as e:
    err.write(str(e))
finally:
    log.close()
    err.close()