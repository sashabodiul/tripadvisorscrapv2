import aiohttp
from datetime import datetime
import brotli
import ssl
from aiohttp import TCPConnector

async def scrape_data(proxy, old_domain, new_domain, user_agent, url, key_file_path, cert_file_path):
    try:
        other_chunk_url = url.split('/')[-1]
        url = url.replace(old_domain,new_domain)
        domain = new_domain.split('/')[-2]
        dom2 = domain.split('.')[1:]
        domain2 = '.'.join(dom2)
        
        payload = {}
        headers = {
                'accept': 'text/html',
                'accept-language': 'en-US,en;q=0.6',
                'cache-control': 'max-age=0',
                'cookie': f'TASameSite=1; TAUnique=%1%enc%3AR0ej7L4E8DnRN9qtQ92%2FkeHOgMiyBexu9boTKBqB8E3smifpu%2BS23UpCaVh1IJQVNox8JbUSTxk%3D; TASSK=enc%3AAIYXoM0CO0t4IyvUWtEtCsw22QXCOKdVDo8YeSUyprlazNIK3PW7swWvCko9KkWnyHnzmAXzHNiqjZdsUAiS6IJnTz%2F%2BXna6xRjReTfc5Hgunr1WMu3rX7BSoNyxRVLtlQ%3D%3D; ServerPool=X; G_AUTH2_MIGRATION=informational; TATrkConsent=eyJvdXQiOiJBRFYsU09DSUFMX01FRElBIiwiaW4iOiJBTkEsRlVOQ1RJT05BTCJ9; VRMCID=%1%V1*id.13091*llp.%2FRestaurants-g187275-Germany%5C.html*e.1712444845523; TATravelInfo=V2*AY.2024*AM.4*AD.14*DY.2024*DM.4*DD.15*A.2*MG.-1*HP.2*FL.3*DSM.1712018799988*AZ.1*RS.1*RY.2024*RM.3*RD.30*RH.20*RG.2; TAReturnTo=%1%%2F{other_chunk_url}; TART=%1%enc%3AtYcH6QSNFOVvXZbzIvGyUBW4fWd3qtDpTrNYG7p0UMrm7XED%2B%2FPsIRtj8WFAaXbqZQnMIP2Q3mY%3D; TADCID=IJR3ePM9teLUJgN3ABQCmq6heh9ZSU2yA8SXn9Wv5HzaqZbXSk8mtnqY3JMuC21PBGuJXPtGuoslRSaWuZVTcxttgO57AGtw_8M; TAAUTHEAT=GewofqlUVI25xqtTABQCNrrFLZA9QSOijcELs1dvVzyxqYgCZWN43F5JmMkaFo8P12z50lneHPYjXbKT5THPkp0JLU9bVj0egkt0Mpx0AcLbZeD3mx_rAvxsBjU9dT3HJLRH7qyZMSH84JY_4N76wHBWBr2n_NlEMtAK00eBUegQZFmaE8jqS0DET1Eczkz1Kr2ToQs01dWwEV3ntEZurK-OhoTF-0gpSft6; __vt=yk0hqNbuTRW8rXjLABQCwRB1grfcRZKTnW7buAoPsSy4SSbsvcBOfCDu8FswCj3H9riqch50ZDDOvIHkOfe4wr_PCyHYwfA2ufUddMP_rUGAU9EodLJxxI7gVgbxjEOktbV1LpZXYKT-6csCAbjUcA-kBYk; TASID=1DDC4ACE2BDEB6BDC17D13EE23F1DF92; _abck=B5E8EB88F4793A85F7D0DB43DEDB5DBA~-1~YAAQXjYQYL+spNGOAQAAietl1AthB70pB/ZdGLUouI9SmfZZO4tlgtvNgOdCqGqU8ct71CGTZ7zdH9i86GUc/7ZzSAle2o1ohjpm8W5DmThLSxWORSVaSpBwb4pGcKAG/MvO2FuC+373GT2I9a9J3NqG5BoTInEiBSNTRXEDUpznT+4IUija1y4M7nAuDaQDkgiOefKD5E0uTUmmTTZeoIZzNLLg4m+E0GfJKldyJ8zsnz6cD4duPPs3rUiXU7opD1uOYHx4BjDofuRbukAnPgUQPyr9db/x/dS3ox0R+Gmb23uSyn6e3oF5JxRRe7OevpaFBa7PTOtCZeRfddClQj9jFP+k3MMNJ83YXHvOyaRDeArTg8cNwUQ2dr0RNHeXEzRCGFFQGsQZgowvH4zy~-1~-1~-1; PAC=AJ-AkRhwk6dYwk9A2tJzzIEKjPuC3TvGeqlOBINGaAwWmiQi9mhKydtSpPaN2AEaVjXTA9VRROSrrtPypL5tNICGffessQ-vhmJUsNXrkdo1XYO80Lgb1EQ-VrU5jBT7HA%3D%3D; SRT=TART_SYNC; roybatty=TNI1625!AMj9YlElfJN7pKy%2BC98LfaEePPd5NjvPAgk6%2BGwaUFIz87ObOW2dT9%2BD0XMKHG4dWCZvMWwalS8M4PBdlp0u%2FUvPoeNrL6nCduhw8bnMeyixrIKgkFSorfaVOrN3H5DNc769JCOX3lMEAUHs9jcmDEcWf8zLk%2B1e6hkHxH9F90DlC8mVH2609qZTcFArsnJCNA%3D%3D%2C1; datadome=KzGPkNK_C05CimTIULGK8n9RQqWxosRwueZad5t93nWLbsS1hchxKsnuJIV04bqspV06OE6yIZmvl_M9gv21qmgqvVek~QwwJtFaQmkxo9qc0ujvy0iXub6Kq5AL2UR9; bm_sz=B2FEEA5DC4D2933AE0B640A862622924~YAAQXjYQYM6vpNGOAQAAwF1m1BcLa+cbP9IKIavjnhnKtIB1sMxRVOYPmms2v2K6E9dwEjaVjPtmYRx1j+oOGRUA2barxL78Xat0bOjnIdl0+L9ztzSVzQdJifNxi05FFqiIq1nEO48u9OSGYBlijlzvy1XP/64S5vE7s0mSWQETERAjIMmjBCrt7sdXXcRDw0IiGFh3Y0RbwatFs4+3oxwoxPGDjpmzGqmL8qIyv/ELt/pggcph87fpw+6jOcOqTuPTHsQ4Y/jM+hgb3RtnchHDNhH1j1Qvpv7acfMHakVFo6IIEvSFGxNSYera+kAfAzliDzPd2spWke+6KoZGlngonqeAOKwrC9bomarBRJpfM5+yWc8q9XFTtfJ/xjS92c+FXpDRGRxcGt07Dxv7+f/P2jAWOcPNUcd35nXJ~3553094~4604471; TASession=V2ID.1DDC4ACE2BDEB6BDC17D13EE23F1DF92*SQ.1364*LS.Restaurant_Review*HS.recommended*ES.popularity*DS.5*SAS.popularity*FPS.oldFirst*TS.1B32A4EB67F120996C79F7754BEA64F2*FV.T*LF.en*FA.1*DF.0*TRA.false*LD.1079658*EAU.o',
                'referer': 'https://www.tripadvisor.com/Search?searchSessionId=000a310fbff7fb9f.ssid&searchNearby=false&ssrc=e&q=fdd&sid=1DDC4ACE2BDEB6BDC17D13EE23F1DF921712960458460&blockRedirect=true&geo=1',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-user': '?1',
                'sec-gpc': '1',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1'
                }

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