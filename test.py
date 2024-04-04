from datetime import datetime, timedelta
from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.x509.oid import NameOID
import tempfile
import uuid
import asyncio
from bs4 import BeautifulSoup
import ssl
from aiohttp import TCPConnector
import re
import base64
import aiohttp
import brotli
from data.config import *
import random


async def get_all_data_from_restaurants(content,url):
    try:
        soup = BeautifulSoup(content, 'html.parser')
        # Извлечение информации о местоположении ресторана
        breadcrumbs = soup.find('ul', class_='breadcrumbs')
        menu_text = name = None
        if breadcrumbs:
            menu = breadcrumbs.find_all('li')
            menu_text = ';'.join([li.text for li in menu])
            if menu_text:  # Проверяем, что menu_text не пустой
                name = menu_text.split(';')[-1].strip()
        # Извлечение информации о рейтинге и количестве отзывов
        rating = reviews_count = None
        block_a = soup.find('a', href='#REVIEWS')
        if block_a:
            svg_tag = block_a.find('svg')
            if svg_tag:
                title_tag = svg_tag.find('title')
                if title_tag:
                    try:
                        rating = title_tag.text.split(" ")[0]
                    except IndexError:
                        pass
            span_tag = block_a.find('span')
            if span_tag:
                try:
                    reviews_count = span_tag.text.split(" ")[0]
                    # Создаем таблицу перевода, которая удаляет все непечатаемые символы и пробелы
                    translation_table = str.maketrans('', '', '\u202f ')
                    # Применяем таблицу перевода к строке
                    reviews_count = reviews_count.translate(translation_table)
                    # Оставляем только цифры
                    reviews_count = ''.join(filter(str.isdigit, reviews_count))
                except IndexError:
                    pass
        all_rating = soup.find_all('span', class_='vzATR')
        if all_rating is not None:
            food_rating = float(all_rating[0].find('span').get('class')[1][-2:])/10 if len(all_rating) > 0 else "NULL"
            service_rating = float(all_rating[1].find('span').get('class')[1][-2:])/10 if len(all_rating) > 1 else "NULL"
            value_rating = float(all_rating[2].find('span').get('class')[1][-2:])/10 if len(all_rating) > 2 else "NULL"
            atmosphere_rating = float(all_rating[3].find('span').get('class')[1][-2:])/10 if len(all_rating) > 3 else "NULL"
        else:
            food_rating = service_rating = value_rating = atmosphere_rating = "NULL"
        # Извлечение информации о ценах, телефоне, местоположении и веб-ссылке
        email = prices = telephone = location = website_link = decoded_url = None
        mailto_link = soup.find('a', href=lambda href: href and href.startswith("mailto:"))
        if mailto_link:
            # Получаем значение атрибута href
            href = mailto_link.get('href')
            # Находим индекс символа "?subject="
            subject_index = href.find('?subject=')
            if subject_index != -1:
                # Обрезаем href, чтобы получить только email
                email = href[len("mailto:") : subject_index]
        location_tag = soup.find('a', href="#MAPVIEW")
        if location_tag:
            location = location_tag.text
        website_link_tag = soup.find('a', class_="YnKZo Ci Wc _S C AYHFM")
        if website_link_tag:
            href = website_link_tag.get('data-encoded-url')
            if href:
                decoded_url = base64.b64decode(href).decode('utf-8')
                # Удаление первых четырех символов
                decoded_url = decoded_url[4:]
                # Удаление последних четырех символов
                decoded_url = decoded_url[:-4]
        prices_tags = soup.find_all('a', class_='dlMOJ')
        if prices_tags:
            prices = prices_tags[0].text
        telephone_tag = soup.find('a', href=lambda href: href and href.startswith('tel:'))
        if telephone_tag:
            telephone = telephone_tag.text
        # Извлечение информации о позиции в рейтинге
        position_in_rating = []
        span_tags_with_b = soup.find_all(lambda tag: tag.name == 'span' and tag.find('b'))
        for span_tag in span_tags_with_b:
            span_text = ''.join(span_tag.stripped_strings).strip()
            if '#' in span_text:
                position_in_rating.append(span_text)
        pattern = r"g(\d+)-"
        # Поиск совпадений в строке
        matches = re.search(pattern, url)
        g_code = None
        if matches:
            # Извлечение найденной части
            g_code = matches.group(1)
        else:
            print(datetime.now(),":[ERROR] No match fount for g code")

        return {
            'breadcrumbs':menu_text,
            'name':name,
            'rating': rating,
            'reviews_count': reviews_count,
            'prices': prices,
            'telephone': telephone,
            'location': location,
            'website_link': decoded_url,
            'position_in_rating': set(position_in_rating),
            'email': email,
            'food_rating': food_rating,
            'service_rating': service_rating,
            'value_rating': value_rating,
            'atmosphere_rating': atmosphere_rating,
            'g_code': g_code,
            'link': url
        }
    except Exception as e:
        print(datetime.now(),':[ERROR] with BeautifulSoup get response: ',e)

async def scrape_data(proxy, old_domain, new_domain, user_agent, url):
    try:
        other_chunk_url = url.split('/')[-1]
        url = url.replace(old_domain,new_domain)
        domain = new_domain.split('/')[-2]
        dom2 = domain.split('.')[1:]
        domain2 = '.'.join(dom2)
        
        payload = {}
        headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:125.0) Gecko/20100101 Firefox/125.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br',
        # 'Referer': 'https://www.tripadvisor.com/Search?searchSessionId=0018c9c919e7838d.ssid&searchNearby=false&ssrc=e&q=sdf&sid=78CC9C4AF47BCD9445496B93729EB1871712254600097&blockRedirect=true&geo=1',
        'Connection': 'keep-alive',
        # 'Cookie': '_ga_QX0Q50ZC9P=GS1.1.1712266949.5.0.1712266951.58.0.0; TAUnique=%1%enc%3Ae6Cz0rUi9CvCNhsL5v8u%2FFtiYE3%2FyiW0EDOi7KVvePPj8LiWKc8Y4XNH0tB%2BAHD7Nox8JbUSTxk%3D; TADCID=Xn7Jb2QmHVL_1mvOABQCmq6heh9ZSU2yA8SXn9Wv5Hyss8rDw6GFnZUAsWjOAxNX7NXutKXkhP23-PApbL3XqtUtg67YPp614lY; TASSK=enc%3AAOGDuBT%2FymKdYEewgCgOJdl99kP6jM2iEOjmh8FdqfAtqEkAEu%2BRiaiBb7Y6YQt9SYEhsDB3HXIokx0C2K31V7EGiEAJGH3FwvqAZCc24Heu5w3tmrF94AnWKcK2GhB%2BLQ%3D%3D; PMC=V2*MS.4*MD.20240330*LD.20240404; TART=%1%enc%3AtYcH6QSNFOVAY45YC%2FX3%2FA1KaaCn7tT6ha4SjYT217fEYItjIFrFi65H%2FrSFOqrVkagyFvowwb0%3D; TATravelInfo=V2*AY.2024*AM.4*AD.14*DY.2024*DM.4*DD.15*A.2*MG.-1*HP.2*FL.3*DSM.1712020178488*RS.1*RY.2024*RM.4*RD.1*RH.20*RG.2; TAUD=LA-1711838732794-1*RDD-1-2024_03_30*RD-176991627-2024_04_01.919129*HDD-415867561-2024_04_14.2024_04_15*ARC-416825301*LG-428222524-2.1.F.*LD-428222525-.....; _abck=E423D2A3711F6B3092A32DF16AEAB4F2~-1~YAAQXhdlX/wWNpuOAQAAK/lRqgsBjtvoLD7V3rYxPexlFtvw5Kl5Ykk13J3Eq4PZCScSEun8Xe+Ats4J0jLrb77X5t9/HA+0Uj2GvZURBKdBCDTrO2cauc/wxe8L2b27bi8BmYcR8ueTcwgsO6sYmD9SURZkFR3G8D+N0OL6pakM7asbEDuAPdXAfDk2lEmIGhzXctu5nSXYlcUewJQgToKFcF2YjUOZpzmMGI/Mm4DNqASs9DiMLXiYBWc0NoCaFpzJwIovTz9px73kkLyUy39+tVMbrgJ0uO0W+tMQGPZPDwgwda2b8O9wWvntj9mX8XGMEWKBCSQgnNPOjS4U5MMRh4oaGyJqKz8P+hXjpWng0pnDahiMxmyBrGe8jpqBFVuugATZv6PftzQNLbZfVCn7Uzdcq6cKD7IbGA==~-1~-1~-1; datadome=JVXJ8xZQYuf_XhoUZWP2eaGxR7ztBTb9UDRy6eSDqyDb~8RXuemaKhw2XF4lmX22vpXiQ6UkyJGH6LXnFEQ68SE_90nYzCQp08L1qubw8U56IM8Sca1U95~O1oOCzuNz; TASameSite=1; PAC=ACNAXVPPqBIKOXT64rZiFEvlStHcv5mU6r-BOZtY-atGHLT53T0rBfgvfZgAYS1Ui_4-C4j7ziPF71CGHTEGY6FL81XpTc2m2Zb4dr3ivF-Z8eMJS22NRXoACZd_gJt9cA%3D%3D; OptanonConsent=isGpcEnabled=0&datestamp=Fri+Apr+05+2024+00%3A42%3A29+GMT%2B0300+(%D0%92%D0%BE%D1%81%D1%82%D0%BE%D1%87%D0%BD%D0%B0%D1%8F+%D0%95%D0%B2%D1%80%D0%BE%D0%BF%D0%B0%2C+%D0%BB%D0%B5%D1%82%D0%BD%D0%B5%D0%B5+%D0%B2%D1%80%D0%B5%D0%BC%D1%8F)&version=202310.2.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=0d1b6f8b-25fb-4129-8570-f901a1d419c8&interactionCount=2&landingPath=NotLandingPage&groups=C0001%3A1%2CC0004%3A1%2CC0002%3A1%2CC0003%3A1%2CV2STACK42%3A1&AwaitingReconsent=false; TATrkConsent=eyJvdXQiOiJTT0NJQUxfTUVESUEiLCJpbiI6IkFEVixBTkEsRlVOQ1RJT05BTCJ9; ab.storage.sessionId.6e55efa5-e689-47c3-a55b-e6d7515a6c5d=%7B%22g%22%3A%2218b23d23-c83d-0cb8-407e-8f429e85379e%22%2C%22e%22%3A1712266964793%2C%22c%22%3A1712266949716%2C%22l%22%3A1712266949793%7D; ab.storage.deviceId.6e55efa5-e689-47c3-a55b-e6d7515a6c5d=%7B%22g%22%3A%224475cc90-d597-3b2b-3c8d-2727d0ac0e76%22%2C%22c%22%3A1712009725648%2C%22l%22%3A1712266949716%7D; _ga=GA1.1.1933623039.1712009726; pbjs_sharedId=d3af9fd2-43e6-4c4f-9f4c-59bc5cff40b0; pbjs_sharedId_cst=CSzfLKsskA%3D%3D; _lc2_fpi=b140173de591--01htdvpjcs55ta01ngct9rpqt1; _lc2_fpi_meta=%7B%22w%22%3A1712009726361%7D; __gads=ID=c3612db02b09ea57:T=1712009727:RT=1712266951:S=ALNI_MZ2vYyYwxsbRZpkVeGKTfakttGpcQ; __gpi=UID=00000d8767181424:T=1712009727:RT=1712266951:S=ALNI_MYdsnII3IZuqwvvhJE8ReYpzn6SCA; __eoi=ID=959e08674f2f0073:T=1712009727:RT=1712266951:S=AA-AfjaD3N0V71grRuZguVsGgqs5; _lr_env_src_ats=false; pbjs_unifiedID=%7B%22TDID_LOOKUP%22%3A%22FALSE%22%2C%22TDID_CREATED_AT%22%3A%222024-03-10T01%3A47%3A13%22%7D; pbjs_unifiedID_cst=CSzfLKsskA%3D%3D; bm_sz=1837A757A6BCB957D4464AA672D38003~YAAQXhdlX0rZOJuOAQAA2G5iqhfVKvuEDu9gpcbamEgTsPa5rUFDIarJdZ35lNmlll6zueZhU3+fev4Ydgtp/M8AXH11lDDaarSU9eL3KkYXHby1f6O9afmbQGRHF1UI00VXP+EaxvZzfehwEWcYqA38I0VvEzAzHAHAHbxUVoNiWOP2n7JmEsjjpBbRwlpKntkrZd5C1+DxfIBfJ4xHP5gECi0MJ3TNAmU5Rn3hhc3Iu5djpZbC9OazPcCHTf0tJw3rRGxlMFk9z7AN2iS0jYEB1eIZU+cUvLJX59jewJBfYE/8O+hLBnqpkxqRvEriFjf9QIHQibQuOJRRGfvrZyqFJtaQUPbefUsfP8+jwvy6r3+xtsjupCwLmAMgxQ255AAOuoaSxvc1MpyhCgvaU5fOvywWm6oqjT8nZ2onv+xm4qsWc2q5cX6Wje3Y2BPUO59J7ogi~3229239~4337989; TASession=V2ID.E609C2FE0C7F4DEBA2D18531B3D60163*SQ.18*LS.DemandLoadAjax*HS.recommended*ES.popularity*DS.5*SAS.popularity*FPS.oldFirst*LF.en*FA.1*DF.0*TRA.false*LD.7803737*EAU._; _li_dcdm_c=.tripadvisor.com; pbjs_li_nonid=%7B%7D; pbjs_li_nonid_cst=zix7LPQsHA%3D%3D; _lr_sampling_rate=100; ServerPool=C; TAReturnTo=%1%%2FRestaurant_Review-g39604-d7803737-Reviews-Yummy_Pollo-Louisville_Kentucky.html; __vt=yxmXydrce26qlHnhABQCwRB1grfcRZKTnW7buAoPsSyLI6_g0v55uGiDLwZfht5QtNv2pGApqxG4USxqc5VXQugsK-wwnvtNaBLY6cMMDew_l2nezBeA5uB8OB3EL3ccR58BIeLibUCwIZegMkGX2JhYVg; SRT=%1%enc%3AtYcH6QSNFOVAY45YC%2FX3%2FA1KaaCn7tT6ha4SjYT217fEYItjIFrFi65H%2FrSFOqrVkagyFvowwb0%3D; TASID=E609C2FE0C7F4DEBA2D18531B3D60163; roybatty=TNI1625!AFR0y1E5VQ9ViaCjbIiqd3PcX8CKCyelxa9aStiatz0%2FgtzycDEUVFokkNWGxNoUr4JJBHsUrbj9qHX50pkmLUPOAMlnIIUTwUgJtXFTkoUPD71YmIo3bx2sF596UW13a3YUTuSYqMivBFVjYzqE8aMKkVIGVJBQYcPV0N%2Fi8os1dHogZqshYilliKCoqOh4tA%3D%3D%2C1; OptanonAlertBoxClosed=2024-04-04T21:42:29.460Z; eupubconsent-v2=CP8iaEgP8iaEgAcABBENAuEsAP_gAEPgACiQg1NX_D5ebWti8XZUIbtkaYwP55izokQhBhaIEewFwAOG7BgCB2EwNAV4JiACGBAEkiLBAQNlHABUCQAAAIgRiSCMYkWMgTNKJKBAiFMRO0NYCBxmmgFDWQCY5kosszdxmDeAAAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAAAAAAAAAAAAAAAAAAA_cff79LgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEQaoMoACIAFAAXAA4ADwAKgAXAA4AB4AEAAJAAXwAxADKAGgAagA8AB-AEQAJgAUwAqwBcAF0AMQAaAA3gB-AEJAIgAiQBHACWAE0AMAAYYAywBmgDZAHIAPiAfYB-wD_AQAAg4BEYCLAIwARqAjgCOgEiAJKAT8AqABcwC8gF9AMUAZ8A0QBrwDaAG4AOkAdsA-wB_wEIAImAReAj0BIgCVgExQJkAmUBOwCh4FIAUiApMBUgCrAFZAK7gWIBYoC0YFsAWyAt0BcgC6AF2gLvgXkBeYC-gGCANsgm2CbkE3gTfAnDBOUE5gJ0gTrgnaCdwE8AJ5gT7gn6CfwFAAKCBBqAKBACQAdABcAGyARAAwgCdAFyANsAgcEADAA6AFcARAAwgCdAIHBgA4AOgAuADZAIgAYQBcgEDhAAcAHQA2QCIAGEAToAuQCBwoAGAFwAwgEDhgAIAwgEDhwAYAHQBEADCAJ0AgcBFcgACAMIBA4kADAIgAYQCBxQAKADoAiABhAE6AQO.f_wACHwAAAAA; OTAdditionalConsentString=1~43.46.55.61.70.83.89.93.108.117.122.124.135.136.143.144.147.149.159.192.196.202.211.228.230.239.259.266.286.291.311.320.322.323.327.338.367.371.385.394.397.407.413.415.424.430.436.445.453.486.491.494.495.522.523.540.550.559.560.568.574.576.584.587.591.737.802.803.820.821.839.864.899.904.922.931.938.979.981.985.1003.1027.1031.1040.1046.1051.1053.1067.1085.1092.1095.1097.1099.1107.1135.1143.1149.1152.1162.1166.1186.1188.1205.1215.1226.1227.1230.1252.1268.1270.1276.1284.1290.1301.1307.1312.1345.1356.1364.1365.1375.1403.1415.1416.1421.1423.1440.1449.1455.1495.1512.1516.1525.1540.1548.1555.1558.1570.1577.1579.1583.1584.1591.1603.1616.1638.1651.1653.1659.1667.1677.1678.1682.1697.1699.1703.1712.1716.1721.1725.1732.1745.1750.1765.1782.1786.1800.1810.1825.1827.1832.1838.1840.1842.1843.1845.1859.1866.1870.1878.1880.1889.1899.1917.1929.1942.1944.1962.1963.1964.1967.1968.1969.1978.1985.1987.2003.2008.2027.2035.2039.2047.2052.2056.2064.2068.2072.2074.2088.2090.2103.2107.2109.2115.2124.2130.2133.2135.2137.2140.2145.2147.2150.2156.2166.2177.2183.2186.2205.2213.2216.2219.2220.2222.2225.2234.2253.2279.2282.2292.2299.2305.2309.2312.2316.2322.2325.2328.2331.2334.2335.2336.2337.2343.2354.2357.2358.2359.2370.2376.2377.2387.2392.2400.2403.2405.2407.2411.2414.2416.2418.2425.2440.2447.2461.2462.2465.2468.2472.2477.2481.2484.2486.2488.2493.2498.2499.2501.2510.2517.2526.2527.2532.2535.2542.2552.2563.2564.2567.2568.2569.2571.2572.2575.2577.2583.2584.2596.2604.2605.2608.2609.2610.2612.2614.2621.2628.2629.2633.2636.2642.2643.2645.2646.2650.2651.2652.2656.2657.2658.2660.2661.2669.2670.2677.2681.2684.2687.2690.2695.2698.2713.2714.2729.2739.2767.2768.2770.2772.2784.2787.2791.2792.2798.2801.2805.2812.2813.2816.2817.2821.2822.2827.2830.2831.2834.2838.2839.2844.2846.2849.2850.2852.2854.2860.2862.2863.2865.2867.2869.2873.2874.2875.2876.2878.2880.2881.2882.2883.2884.2886.2887.2888.2889.2891.2893.2894.2895.2897.2898.2900.2901.2908.2909.2916.2917.2918.2919.2920.2922.2923.2927.2929.2930.2931.2940.2941.2947.2949.2950.2956.2958.2961.2963.2964.2965.2966.2968.2973.2975.2979.2980.2981.2983.2985.2986.2987.2994.2995.2997.2999.3000.3002.3003.3005.3008.3009.3010.3012.3016.3017.3018.3019.3024.3025.3028.3034.3038.3043.3048.3052.3053.3055.3058.3059.3063.3066.3068.3070.3073.3074.3075.3076.3077.3078.3089.3090.3093.3094.3095.3097.3099.3100.3106.3109.3112.3117.3119.3126.3127.3128.3130.3135.3136.3145.3150.3151.3154.3155.3163.3167.3172.3173.3182.3183.3184.3185.3187.3188.3189.3190.3194.3196.3209.3210.3211.3214.3215.3217.3219.3222.3223.3225.3226.3227.3228.3230.3231.3234.3235.3236.3237.3238.3240.3244.3245.3250.3251.3253.3257.3260.3270.3272.3281.3288.3290.3292.3293.3296.3299.3300.3306.3307.3309.3314.3315.3316.3318.3324.3328.3330.3331.3531.3731.3831.3931.4131.4531.4631.4731.4831.5231.6931.7031.7235.7831.7931.8931.9731.10231.10631.10831.11031.11531.12831.13632.13731.14237.15731.16831.21233.23031.24431.24533.25731.25931.26031.26831; _lr_retry_request=true',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'TE': 'trailers'
        }

        # Где-то в вашем коде генерируется ключ и сертификат
        key_file_path, cert_file_path = await generate_self_signed_certificate()

        # Создание SSL контекста с использованием сгенерированного ключа и сертификата
        ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        ssl_context.load_cert_chain(certfile=cert_file_path, keyfile=key_file_path)

        # Использование SSL контекста при создании TCPConnector
        connector = TCPConnector(ssl=ssl_context)

        async with aiohttp.ClientSession(connector=connector, headers=headers) as session:
            async with session.get(url) as response:
                if response.content_type == 'application/octet-stream' and response.headers.get('content-encoding') == 'br':
                    # Decode Brotli content
                    content = await response.read()
                    decoded_content = brotli.decompress(content)
                    return decoded_content.decode('utf-8')
                else:
                    return await response.text()
    except Exception as e:
        print(datetime.now(),':[ERROR] scrap page: ', e, 'with url: ', url)


async def generate_self_signed_certificate():
    # Генерация закрытого ключа RSA
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )

    # Генерация случайного серийного номера для сертификата
    serial_number = int(uuid.uuid4())

    # Генерация случайных атрибутов для имени сертификата
    common_name = str(uuid.uuid4())

    # Генерация самоподписанного сертификата
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, u"US"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"California"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, u"Mountain View"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"OpenAI"),
        x509.NameAttribute(NameOID.COMMON_NAME, common_name),
    ])

    certificate = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        serial_number
    ).not_valid_before(
        datetime.utcnow()
    ).not_valid_after(
        datetime.utcnow() + timedelta(days=365)
    ).add_extension(
        x509.SubjectAlternativeName([
            x509.DNSName(common_name),
        ]),
        critical=False,
    ).sign(private_key, hashes.SHA256())

    # Создание уникальных имен для временных файлов ключа и сертификата
    with tempfile.NamedTemporaryFile(delete=False) as key_file:
        key_filename = key_file.name
        private_key_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )
        key_file.write(private_key_pem)

    with tempfile.NamedTemporaryFile(delete=False) as cert_file:
        cert_filename = cert_file.name
        cert_pem = certificate.public_bytes(serialization.Encoding.PEM)
        cert_file.write(cert_pem)

    return key_filename, cert_filename


# Пример использования:
async def main():
    old_domain = MAIN_DOMAIN.strip()
    new_domain = random.choice(DOMAINS_LIST).strip()
    user_agent = random.choice(USER_AGENTS_LIST).strip()
    rest_url = "https://www.tripadvisor.com/Restaurant_Review-g39604-d7803737-Reviews-Yummy_Pollo-Louisville_Kentucky.html"
    content = await scrape_data(proxy=random.choice(PROXY_LIST),
                                            old_domain=str(old_domain),
                                            new_domain=str(new_domain),
                                            user_agent=str(user_agent),
                                            url=str(rest_url))
    result = await get_all_data_from_restaurants(content,rest_url)
    print(content)
    
asyncio.run(main())
