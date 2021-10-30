import time
import requests
from bs4 import BeautifulSoup as bs4
from discord_webhook import DiscordWebhook, DiscordEmbed
import re
import base64

WEBHOOK = '' # DISCORD WEBHOOK
TIME = 5 # DELAY IN SECONDS
REQUEST = 'steam/?game[]=730&order_by=pdate_to_down' # URL FOR PARSE
XF_SESSION = '' # XF_SESSION COOKIE IF EXIST
XF_TFA_TRUST = '' # XF_SESSION COOKIE IF EXIST
XF_USER = '' # XF_USER

def getXenforoCookie():
    r = requests.get('https://lolz.guru/process-qv9ypsgmv9.js', headers={'User-Agent':'Mozilla/5.0'})
    cookieArray = re.search('^var _0x\w+=(.*?);', r.text).group(1)
    base64DfId = eval(cookieArray)[-1]
    return base64.b64decode(base64DfId).decode()

def GetDivsWithoutBumps(tag):
    return tag.has_attr('class') and 'marketIndexItem' in tag.get('class') and 'sticky' not in tag.get('class')

def GetItems(url):
    headers = {
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'cookie': f'df_id={getXenforoCookie()}; xf_logged_in=1; xf_user={XF_USER}; ' + (f'xf_session={XF_SESSION}' if XF_SESSION else f'xf_tfa_trust={XF_TFA_TRUST}'),
        'user-agent': 'Mozilla/5.0'}
    
    url = 'https://lolz.guru/market/' + url
    r = requests.get(url, headers=headers)
    b = bs4(r.text, 'html.parser')
    items = b.find_all(GetDivsWithoutBumps)
    items = list(map(lambda x: [x.find('a', {'class': 'marketIndexItem--Title'}).text,
                                x.find('a', {'class': 'marketIndexItem--Title'}).get('href'),
                                x.find('span', {'class': 'Value'}).get('data-value'),
                                ' '.join(x.find('div', {'class': 'marketIndexItem--Badges stats'}).text.replace('\n', ' ').replace('\t', ' ').strip().split()),
                                x.find('a', {'class': 'username'}).get('href'),
                                ' '.join(x.find('div', {'class': 'marketIndexItem--otherInfo'}).text.replace('\n', ' ').replace('\t', ' ').strip().split())], items))
    return items

def SendDiscord(item):
    print('[NEW]', item)
    webhook = DiscordWebhook(url=WEBHOOK)
    embed = DiscordEmbed(title=item[0], description=item[3], color='3066993')
    embed.set_author(name=item[5], url='https://lolz.guru/' + item[4])
    embed.set_timestamp()
    embed.set_url('https://lolz.guru/' + item[1])
    embed.add_embed_field(name='Price:', value=item[2] + ' руб.')
    webhook.add_embed(embed)
    webhook.execute()

if __name__ == '__main__':
    ITEMS = []
    for i in GetItems(REQUEST):
        if i[1] not in ITEMS:
            ITEMS.append(i[1])
    print(f'[START] Parse {len(ITEMS)} items')
    while 1:
        for i in GetItems(REQUEST):
            if i[1] not in ITEMS:
                ITEMS.append(i[1])
                SendDiscord(i)
        time.sleep(TIME)