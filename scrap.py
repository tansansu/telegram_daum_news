"""
m.daum.net 메인화면의 뉴스페이지 링크 수집
"""

import requests
from bs4 import BeautifulSoup
import re
import random
import time
import csv
from datetime import datetime
import sys
sys.path.append('/Users/tansansu/Google Drive/Python/Telegram_Bot/')
sys.path.append('/home/revlon/Codes/Telegram_Bot/')
sys.path.append('/home/tansan/Codes/Telegram_Bot/')
sys.path.append('/root/Codes/Telegram_Bot/')
# sys.path.append('C://Users//tansansu//Google 드라이브//Python//Telegram_Bot')
from TelegramBot import TelegramBot


# 0. 기본 정보
URL = 'https://m.daum.net/'
AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
REFERER = 'https://m.daum.net'
dir = '/root/Codes/Bots/Daum_News'
#dir = '/home/tansan/Codes/Bots/Daum_News'


# 1. 뉴스 수집 함수
def get_news():
    # 게시판 주소를 요청할 세션 생성
    session = requests.Session()
    # User-Agent와 Referer 헤더 정보 업데이트
    session.headers.update({'User-Agent': AGENT, 'Referer': REFERER})
    resp = session.get(URL)
    resp.encoding = 'utf-8'
    soup = BeautifulSoup(resp.text, 'lxml')
    # extracting news
    news_pannel = soup.select('div.out_ibox')[0]
    text_articles = news_pannel.select('li.ta_txt')[:15]
    #pic_articles = news_pannel.findAll('li', {'class': 'size_t1'})[:2]
    # parsing
    articles = []
    for i, article in enumerate(text_articles):
        l = []
        title = article.find('a').text
        url = article.find('a')['href']
        if url.__contains__('auto') | url.__contains__('new'):
            continue
        try:
            link_re = re.search(r'^https://.+[0-9]', url)
            if link_re is not None:
                link = link_re.group()
            else:
                continue
        except Exception as e:
            print("Exception error: " + e)
            continue
        print(i, link)
        unique_id = re.search(r'[0-9]+', link).group()
        l.append(title)
        l.append(link)
        l.append(unique_id)
        articles.append(l)
    # 링크 추출
    #for article in pic_articles:
    #    l = []
    #    title = article.find('strong').text
    #    unique_id = re.search(r'[0-9]{12,}', article.find('a')['href']).group()
    #    link = "https://news.v.daum.net/v/" + unique_id
    #    l.append(title)
    #    l.append(link)
    #    l.append(unique_id)
    #    articles.append(l)
    # filtering
    result = [article for article in articles if len(article[2]) > 12]
    return result


# 2. 과거 기사와 중복 비교
def compare_id(ids):
    #f = open("/Users/tansansu/Google Drive/Python/Crawling/Daum_News/ids.log", "r")
    f = open(dir + "/ids.log", "r")
    old_ids = f.readlines()
    f.close()
    old_cnt = len(old_ids)
    adjusted_ids = trim_old_ids(old_ids)
    result = [new_id+"\n" for new_id in ids if new_id+"\n" not in adjusted_ids]
    return result, old_cnt, adjusted_ids


# 3. 뉴스 ID 저장
def save_id(articles):
    ids = []
    for article in articles:
        ids.append(article[2])
    new_ids, old_cnt, old_ids = compare_id(ids)
    # id 추가 저장
    to_save_ids = old_ids + new_ids
    print('관리 기사 개수: %d개' % len(to_save_ids))
    #with open("/Users/tansansu/Google Drive/Python/Crawling/Daum_News/ids.log", "w") as f:
    with open(dir + "/ids.log", "w") as f:
        for new_id in to_save_ids:
            f.write(new_id)
    return new_ids


# 4. 새로운 기사 추출
def new_articles(articles, ids):
    final_articles = [article for article in articles if article[2]+'\n' in ids]
    return final_articles


# 5. 기사 ID 리스트 정리
def trim_old_ids(old_ids):
    return old_ids[-300:]


# 6. 임시 저장 기사 불러오기
def restore_articles():
    temp_articles = []
    with open(dir+'/temp_articles.csv', 'r') as f:
        rdr = csv.reader(f, delimiter='^')
        for line in rdr:
            print(line)
            temp_articles.append(line)
    return temp_articles


if __name__ == "__main__":
    # random delay
    # time.sleep(random.randrange(25, 85))
    time_log = datetime.now().strftime('%Y-%m-%d %H:%M')
    print('===== %s =====' % time_log)
    # scrap news
    articles = get_news()
    # choice articles to send into telegram channel
    new_ids = save_id(articles)
    print('신규 기사 ID수: %s' % len(new_ids))
    if len(new_ids) > 0:
        # 이전 저장된 발송 기사 불러오기
        temp_articles = restore_articles()
        print('임시 기사 수: %d' % len(temp_articles))
        current_articles = new_articles(articles, new_ids)
        final_articles = temp_articles + current_articles
        if len(final_articles) > 5:
            # Creating Message
            message = ''
            for i, article in enumerate(final_articles):
                print(article[0])
                if i == len(final_articles)-1:
                    message += '%d. %s\n%s' % (i + 1, article[0], article[1])
                else:
                    message += '%d. %s\n%s\n\n' % (i+1, article[0], article[1])
                time.sleep(random.randrange(1, 4))
            # To send telegram
            TelegramBot().daum_news(message)
            # Report Send
            TelegramBot().log_to_me(
                "%s\n%d개의 뉴스가 전송되었습니다!" % \
                (time_log, len(final_articles))
            )
            # 임시 기사 리스트 비우기
            with open(dir + '/temp_articles.csv', 'w') as f:
                f.write('')
        else:
            # 현재 기사를 임시 기사에 추가
            with open(dir+'/temp_articles.csv', 'a') as f:
                wr = csv.writer(f, delimiter='^')
                for i, article in enumerate(current_articles):
                    print("new article save into temp: %d - %s" % (i, article))
                    wr.writerow(article)
    else:
        # Report Send
        TelegramBot().daum_news_log("신규 기사 수가 아직 0개 입니다!")
