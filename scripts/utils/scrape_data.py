import aiohttp
from datetime import datetime
import brotli

async def scrape_data(proxy,old_domain,new_domain,user_agent, url):
    try:
        other_chunk_url = url.split('/')[-1]
        url = url.replace(old_domain,new_domain)
        domain = new_domain.split('/')[-2]
        dom2 = domain.split('.')[1:]
        domain2 = '.'.join(dom2)
        
        payload = {}
        headers = {
        'User-Agent': f"{user_agent}",
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://www.tripadvisor.com/Search?searchSessionId=001a73ee724f30c1.ssid&searchNearby=false&q=fds&sid=E5B4EBEFC2C9C7E47EAAE6B3335DCB1E1712020179302&blockRedirect=true&geo=1&ssrc=e&rf=1',
        'Connection': 'keep-alive',
        'Cookie': f'_ga_QX0Q50ZC9P=GS1.1.1712019205.3.1.1712020185.54.0.0; TAUnique=%1%enc%3Ae6Cz0rUi9CvCNhsL5v8u%2FFtiYE3%2FyiW0EDOi7KVvePPj8LiWKc8Y4XNH0tB%2BAHD7Nox8JbUSTxk%3D; TADCID=AOMl4Iect5scyewpABQCmq6heh9ZSU2yA8SXn9Wv5HycxDgQL63WWNqv28c-mJYbS9dXQAvdVyt-AB2YuT5DOAmWshj34wMEMYM; TASSK=enc%3AAOGDuBT%2FymKdYEewgCgOJdl99kP6jM2iEOjmh8FdqfAtqEkAEu%2BRiaiBb7Y6YQt9SYEhsDB3HXIokx0C2K31V7EGiEAJGH3FwvqAZCc24Heu5w3tmrF94AnWKcK2GhB%2BLQ%3D%3D; PMC=V2*MS.4*MD.20240330*LD.20240401; TART=%1%enc%3AtYcH6QSNFOVAY45YC%2FX3%2FA1KaaCn7tT6ha4SjYT217fEYItjIFrFi65H%2FrSFOqrVkagyFvowwb0%3D; TATravelInfo=V2*AY.2024*AM.4*AD.14*DY.2024*DM.4*DD.15*A.2*MG.-1*HP.2*FL.3*DSM.1712020178488*RS.1*RY.2024*RM.4*RD.1*RH.20*RG.2; TAUD=LA-1711838732794-1*RDD-1-2024_03_30*RD-176991627-2024_04_01.919129*HDD-181445589-2024_04_14.2024_04_15*LD-181454076-2024.4.14.2024.4.15*LG-181454078-2.1.F.; _abck=E423D2A3711F6B3092A32DF16AEAB4F2~-1~YAAQdawQApAWPZiOAQAAw0K7mwuTRu1WtXFk/6xpR22lz9qIM+2jPHztk5MxC2Jn459zDIuUmtYsrDCDDRbWLgOqp4pY7Ne3G4IWvdIVirV0M1PE4KTw381ws4fTOHtouFhj2JmWe26nbGGzo5FgW2V7jaoFlA01tVTCeUoxqfBhLca0DeJDdfpaShp6GPVymCmp56D1KCF4vStPw08Po4fQ0XWx590JjoIHoZESZybENz0m8KQ0JtgrZh0GawOIauqPYZ8bQ1cO9TE+1J83gctd9q8FtQuItAaheidcxDwhk5QJhO9dd6bW2D7muX9TzJQBn+QHkSzKY/zi/kPA8oA+J7FgrnuhtV+Ae2ukV30asy4ZraXXzkaylkPrqA0WseBRByvZaDf1h3/5sDE32g==~-1~-1~-1; datadome=UiNbBbQppsjlbq0Twc2HCrWeYAFI5SOg1~KuzeRU0_8w7XZghCo~m9FvNGayF5I43Peoh9wEvt3LCjAbC5cP58T~r~vaPcJlqOHu5iMhnIpxlhXanUImgiQBouk1i0V9; TASameSite=1; bm_sz=9278D204E75DEA041E3412063F3BF78A~YAAQdawQAsMBPpiOAQAAt9hanBeg0Mb6BIEBo3TxXM62TgsBpZ9r6KLOSOHDxwzOML18ly4IW/+Ek2fdoOyQ7RkD1t+DKLaPt/zvb8OTSLLMdmpAtGXssf+bnasbzoEL4U5Z+MuMiZQhKHgot7cs+M8nPTR8qSyvX11NkqJQBJznx6dJ2SO5Mh83Y8+4NHQeezSgME9zVjQmh8o/T4q7pCXEilTPd0u3gM5As++nwaVKvB5+H/cXW34+rgNOD7FXlyUGqiSRreLZRzQD2WB73G7hEEIBLjRzsHGMzit5B7KkdIMSRDi50JPGDrmEkYSIrtOGuJEOc75eBQRWVaBjjZxT2I2ZsLafF77PuOhE2nbjNCay74AeCBNG7fJhUnh3xNyW1PdfxCtiSf+itjqnJp6WOUb8lk7B4xbA+7DmVceC3VWChQD79tXU9odq/HVlmKeTdm/R77eGG+Wgqhyfg+C1EPASkjWA/4/+DYx3Yju7gOz8Cj4Z1aL2Vg==~3359796~4405040; TASession=V2ID.E5B4EBEFC2C9C7E47EAAE6B3335DCB1E*SQ.50*LS.DemandLoadAjax*HS.recommended*ES.popularity*DS.5*SAS.popularity*FPS.oldFirst*LF.en*FA.1*DF.0*TRA.false*LD.6819016*EAU._; PAC=AGH4Kgrp4ekHdC9EXaaK1-_9VORkLmv3ediPoFx3L_3xOd9GBY179Ux2CHJXgn15z1mAqOXlD8UZslPFGfxAOphShkQV03TUYtbSy2WEWfGIAXsPDSBxE3mMaE1IViSUWg%3D%3D; OptanonConsent=isGpcEnabled=0&datestamp=Tue+Apr+02+2024+04%3A09%3A43+GMT%2B0300+(%D0%92%D0%BE%D1%81%D1%82%D0%BE%D1%87%D0%BD%D0%B0%D1%8F+%D0%95%D0%B2%D1%80%D0%BE%D0%BF%D0%B0%2C+%D0%BB%D0%B5%D1%82%D0%BD%D0%B5%D0%B5+%D0%B2%D1%80%D0%B5%D0%BC%D1%8F)&version=202310.2.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=0d1b6f8b-25fb-4129-8570-f901a1d419c8&interactionCount=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1&AwaitingReconsent=false; TATrkConsent=eyJvdXQiOiJTT0NJQUxfTUVESUEiLCJpbiI6IkFEVixBTkEsRlVOQ1RJT05BTCJ9; ab.storage.sessionId.6e55efa5-e689-47c3-a55b-e6d7515a6c5d=%7B%22g%22%3A%22a95cac9a-1638-0006-be57-f913a44e5183%22%2C%22e%22%3A1712020199491%2C%22c%22%3A1712020179732%2C%22l%22%3A1712020184491%7D; ab.storage.deviceId.6e55efa5-e689-47c3-a55b-e6d7515a6c5d=%7B%22g%22%3A%224475cc90-d597-3b2b-3c8d-2727d0ac0e76%22%2C%22c%22%3A1712009725648%2C%22l%22%3A1712020179732%7D; _ga=GA1.1.1933623039.1712009726; pbjs_sharedId=d3af9fd2-43e6-4c4f-9f4c-59bc5cff40b0; pbjs_sharedId_cst=zix7LPQsHA%3D%3D; _li_dcdm_c=.{domain2}; _lc2_fpi=b140173de591--01htdvpjcs55ta01ngct9rpqt1; _lc2_fpi_meta=%7B%22w%22%3A1712009726361%7D; __gads=ID=c3612db02b09ea57:T=1712009727:RT=1712019968:S=ALNI_MZ2vYyYwxsbRZpkVeGKTfakttGpcQ; __gpi=UID=00000d8767181424:T=1712009727:RT=1712019968:S=ALNI_MYdsnII3IZuqwvvhJE8ReYpzn6SCA; __eoi=ID=959e08674f2f0073:T=1712009727:RT=1712019968:S=AA-AfjaD3N0V71grRuZguVsGgqs5; _lr_sampling_rate=100; ServerPool=B; TAReturnTo=%1%%2F{other_chunk_url}; _lr_env_src_ats=false; pbjs_unifiedID=%7B%22TDID_LOOKUP%22%3A%22FALSE%22%2C%22TDID_CREATED_AT%22%3A%222024-03-10T01%3A47%3A13%22%7D; pbjs_unifiedID_cst=zix7LPQsHA%3D%3D; pbjs_li_nonid=%7B%7D; pbjs_li_nonid_cst=zix7LPQsHA%3D%3D; __vt=y-6b4KpjS-ic9Vm0ABQCwRB1grfcRZKTnW7buAoPsSx7D85L4xshLyh1SS2Gp6CNQHEwYSgguLDy1S4uxUKCcZJBcGmXRUQUoNp9uVwr3Y-hPK2DAia06u3Vf1k-gRIB8YPyN_69PWWyoynKrXXbDJEH3Q; TASID=E5B4EBEFC2C9C7E47EAAE6B3335DCB1E; _lr_retry_request=true; SRT=%1%enc%3AtYcH6QSNFOVAY45YC%2FX3%2FA1KaaCn7tT6ha4SjYT217fEYItjIFrFi65H%2FrSFOqrVkagyFvowwb0%3D; roybatty=TNI1625!ALRuzRAUqJw%2BBL2Y%2B4gejQ3%2BP2TgEnRoIjXELsCOK0yM%2FT68YI0DuFtjJXIdc5VaOZs84zKXJYE7QdkDsIOGxsmbmhZrHvliMkVqGXmeMNHG9C4%2BQRUKHtnMlHgNJGWLL2AdDLWdCWWgplNVvIKcq5BD9%2BGZPvgiIPoS%2BWJs%2BC0btgpPJFpD5Gerr8pLoqfoXQ%3D%3D%2C1',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'TE': 'trailers'
        }
        async with aiohttp.ClientSession(headers=headers) as session:
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