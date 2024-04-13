import aiohttp
from datetime import datetime
import asyncio
import aiofiles
import random
import string

async def scrape_data(proxy, old_domain, new_domain, user_agent, url, key_file_path, cert_file_path,interaction_count):
    try:
        url = url.replace(old_domain,new_domain)
        other_chunk_url = url.split('/')[-1]
        random_three_number = random.randint(100, 999)
        # Определяем символы, которые могут быть использованы для генерации строки
        characters = string.ascii_letters + string.digits
        # Генерируем случайную строку из 10 символов
        random_string = ''.join(random.choices(characters, k=10))
        headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'accept-language': 'en-US,en;q=0.6',
        'cache-control': 'max-age=0',
        'cookie': f'TASameSite=1; TAUnique=%1%enc%3AR{random_string}RK9qtQ92%2F{random_string}xu9boTKBqB8E3smlfpu%2BS23{random_string}VNox8JbUSTxk%3D; TASSK=enc%3AAIYXoM0CO0t4IyvUWtEtCsw{random_string}o8YeSUyprlazNIK3PW7swWvCko9KkWnyHnzmAXzHNiqjZdsUAiS6IJnTz%2F%2BXna6xRjReTfc5Hgunr1WMu3rX7BSoNyxRVLtlQ%3D%3D; ServerPool=X; G_AUTH2_MIGRATION=informational; TATrkConsent=eyJvdXQiOiJ{random_string}UFMX01FRElBIiwiaW4iOiJBTkEsRlVOQ1RJT05BTCJ9; TATravelInfo=V2*AY.2024*AM.4*AD.14*DY.2024*DM.4*DD.15*A.2*MG.-1*HP.2*FL.3*DSM.1712018799988*AZ.1*RS.1*RY.2024*RM.3*RD.30*RH.20*RG.2; TAReturnTo=%1%%2F{other_chunk_url}; TADCID=IJR3ePM9teLUJgN3ABQCmq6he{random_string}Xn9Wv5HzaqZbXSk8mtnqY3JMuC21PBGuJXPtGuoslRSaWuZVTcxttgO57AGtw_8M; TAAUTHEAT=GewofqlUVI25xqtTABQCNrrFLZA9QSOijcELs1dvVzyxqYgCZWN43F5JmMkaFo8P12z50lneHPYjXbKT5THPkp0JLU9bVj0egkt0Mpx0AcLbZeD3mx_rAvxsBjU9dT3HJLRH7qyZMSH84JY_4N76wHBWBr2n_NlEMtAK00eBUegQZFmaE8jqS0DET1Eczkz1Kr2ToQs01dWwEV3ntEZurK-OhoTF-0gpSft6; OptanonAlertBoxClosed=2024-04-12T22:20:33.913Z; PMC=V2*MS.88*MD.20240306*LD.20240412; TART=%1%enc%3AtYcH6QSNFOVV3RchUwlO9Ree8kItXK0YrKpiISPvTbX2jLe7ZVoSGZJK0I6Qtccvyx9HjuV9fk0%3D; PAC=AFAdY43L22x8fW2YmYvF-pigpTVY4O1URrbnbvIr2LENPNPXRxhfyd_qlS599ywKpx9EsrXHwra4oI5YV9bXg9Ft1w4RrtIwCOIc3Nr7DTIEWd6n_Piqkl6QHOsyybzgZ40fEChoCUamVCdPfGpcRS7M4EjZcMQwCmS5sVsArSWmtcHFBvXfERjQDdAXWP-rUlwr3Tplf3yhW1GlbMY5bMs%3D; __vt=XWsf4fezjWeo2qktABQCwRB1grfcRZKTnW7buAoPsSy5SouAgLVQIeACKUF1B0SEx1dFaVMZkeX428FPDPRdTFN2Oj9u9vYSGAJGxkaZNonlMw_mzwwyB3nQktc2kJRUGIrXyV6WnaDODoqbgSeK2z_sBpI; SRT=TART_SYNC; TASID=BC765BD03B58486F97135A4220BE180E; TAUD=LA-1709725299052-1*RDD-1-2024_03_06*HD-973295-2024_03_13.2024_04_11*VRD-973296-2024_03_13.2024_04_11*G-973297-2.1.-1.*VRG-973298-2.0*FO-307447455-CWC*FD-307447456-KBL*ARC-604252030*ARDD-1088536248-2024_03_31.2024_04_01*RD-2112629250-2024_03_30.481965*HDD-2293500841-2024_04_14.2024_04_15*LG-3250711718-2.1.T.*LD-3250711719-.....; datadome=oVxV06wpk4rDna2KcgnIcKAKjy2SsABwWINRUIGTQ8alJ1EWltuGTwUNmqn9hV9V4bS53Qm4eTW7Ze4TmZv~yAMnSU2lUZQYtVdsGbBnN8U9m81_pRmQXNGWJ7XuVinY; bm_sz=5FB80B59FD2183CD314C5F08ED46AE4F~YAAQXjYQYIhip{random_string}T1RcTKg2J32kj0y1Dj1fg2Wnh6bZdkMBEkADOs7VPLd+CJyAWk6NgSq0RYcZ9LwUa5+cP/6EEDVTeJ4icWxerbgD9xAESYDYgyuJLhGKNG2LMDrgDWi3TNdnFjUmMozHkEgvQctExKDrDjGAFSUCU8Mb7Yoe+iGaRjYf/n7oPCoc29zLmNoVudXBnBqM3NGY2pOq3Gp4XG5Tg8ykJTyXNfEP1VPFIW/Db1d/wdGPh6LUVUppeIBaleCTKtKjlt3PeUSDgZvwzhtt68EMI+dauHDUlSb/EPWw/VUjCZNmNPIWLfxM0Be9/wzb9gj8ul7uxXsC5tnQCKJ2fqXvZOsm0O0/5B1lX99pMW7mQOKiyBB1YgqSwJvsJqpTajCGbpCOIn8HXIdq690BrBp60jJV2k5SIYbTLCs/YHQdGAiBOIa1nHpBhJHVFRD2n7o6nZcJQfHPXMqRMUs5VL84McqhzPB6LlARKORtwmaNAJGh1oRCS4o/0OEKoVbpuRJ/RDsDcYzos74CYbtP7tBFrV8FKwEzUIcudKl0MgllCWVFPt07Q4JB1KL0AG39DlEULcw==~3617335~3686961; OptanonConsent=isGpcEnabled=0&datestamp=Sat+Apr+13+2024+05%3A40%3A11+GMT%2B0300+(Eastern+European+Summer+Time)&version=202310.2.0&browserGpcFlag=1&isIABGlobal=false&hosts=&consentId=1B32A4EB{random_string}79F7754BEA64F2&interactionCount={interaction_count}&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A0%2CBG23%3A0&AwaitingReconsent=false&geolocation=US%3BCA; TASession=V2ID.BC{random_three_number}BD13B58486F97135A4220BE180E*SQ.1402*LS.Restaurant_Review*HS.recommended*ES.popularity*DS.5*SAS.popularity*FPS.oldFirst*TS.1B32A4EB67F120{random_three_number}C79F{random_three_number}4BEA64F2*FV.T*LF.en*FA.1*DF.0*TRA.false*LD.1079658*EAU.o; _abck=B5E8EB88F4793A85F7D0DB43DEDB5DBA~-1~YAAQXjYQYJtip9GOAQAABLBT1QsuyT6Jamw+8Es4W5FSFX4VwsJ2HayynGE2p7hGHcybSublmSIns4WghT+tOuDvVE3iuF3dwSJysqTvMXfRfXS5resFNL25OzcDmPjovegJ8mKUpJKV3CQ4Axa3VewQh7f5PTmaXAtwjqqMMv5T0HAcwG53Eu36ItVBqSE3n1pyWd0qmpqTvqVbPFXf0uWpYlq4dkITCOmsowRwvcdF/hShWTpzBZnM5v+JD08i8sAV9KuJkBaJ9DSclTJ8zr99qhz9GbJlTO55JW/haLCES5KbPJe69PxwobIJyKrO/zD8uA8X1HyledluAFffoIeG+jcv+qPHd5/gmuiAEBgL1p9IEg==~-1~-1~-1',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'sec-gpc': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': f"{user_agent}"
        }

        async with aiohttp.ClientSession(trust_env=False) as session:
            async with session.get(url=url, headers=headers, proxy=proxy, timeout=6) as response:
                return await response.text()
    except Exception as e:
        log_filename = 'data/logs/logfile.log'
        log_message = f':[ERROR] scrap page: {url} with error: {e}'
        async with asyncio.Lock():
            async with aiofiles.open(log_filename, mode='a') as logfile:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                log_entry = f"[{timestamp}] {log_message}\n"
                await logfile.write(log_entry)
        