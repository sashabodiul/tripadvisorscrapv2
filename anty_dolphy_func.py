from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import requests
import subprocess
import time

API_TOKEN='eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIxIiwianRpIjoiZjY3Zjc1ZTkzNzBkODQ0M2M0MmUxNmRjZDM3MmUwNzhhNjk2OTljNTg2M2E4M2ZkZjc1MjAwMzg2ZmQwMzhkNzY4YzQxNmQzMmVkODFjZmIiLCJpYXQiOjE3MTk4NTI2NjguMDc0NTM5LCJuYmYiOjE3MTk4NTI2NjguMDc0NTQyLCJleHAiOjE3MjI0NDQ2NjguMDU3NzIxLCJzdWIiOiIzNTI3MzE1Iiwic2NvcGVzIjpbXX0.huVaQE41qrNB-sPfIFrK-me1_puykHERCgPE6f6RTQagRDLwzpu84jK7p8oFnnKJbcIJmP_zGcbaID61q0bYXQZhtYJuQzhIeb-VZ7mjefmFbC7XyBS3eHgkWsK8r4JVezM4v4VYdilvnyVlwe2uuPFvb4Y7ebJzQVY91a3A1edz53IKswhwmkFGJZT0UAOyXXAfrfCACFZHBrX5dRtZpIjAuLHI5STv3vRPXYeCpXN4KDDAUfIu_KkKVEzJOFbxsYddB4kunkWwLdttJQ0gjAxWls15fjWAfsoBrgksUdvwr2KMbY1vH9MnW6uhek3UpQIw3EczK9fpU_dbnxgd6QD-bbie9OGGGPp9txb_seKxPCFSLWs8DO979cRp5cZAbgmcpL5P-jvHvH3OJDodW2m13NZZz0as3g_A78gcVfzHRLIxDhkwT2UlDiqXz05OpbhIOh2QpfePtosdX9nP6BJK3Wz0MD7JWkB95Oq0hywkaflNPH-C4UcGBOZRvcA22L96tZ5UqgmgBPqjIIgPJCOCusMSQXaV-ckyRhmTV_-HX_IxZ00xFEw6FokK4HA2YAR-3bSEjMJGIl2uVSDiNBaB3Cd2WdsJ-b1eF89j-_-S1SnVeJZ-mhBbVGomKbQqIMLkLCV55uVB7ZxzMezdtQz3UQMLIqqYJnSypOmy7sk'

def get_browser_profile(profile_id:str):
    url = f'https://dolphin-anty-api.com/browser_profiles/{profile_id}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.0; en-US; rv:1.5a) Gecko/20030718',
        'Authorization': f'Bearer {API_TOKEN}',  # Replace YOUR_ACCESS_TOKEN with your actual token
    }
    response = requests.request("GET", url, headers=headers)

    if response.status_code == 200:
        data = response.json()  # Convert response to JSON format
        # Process the JSON data here as per your application's needs
        return data
    else:
        return None

def get_browser_profiles():

    url = 'https://dolphin-anty-api.com/browser_profiles'
    params = {
        'limit': '',            # Set your limit value if needed
        'query': '',            # Your query parameter if needed
        'tags[]': [],           # List of tags to filter by
        'statuses[]': [],       # List of statuses to filter by
        'mainWebsites[]': [],   # List of main websites to filter by
        'users[]': [],          # List of users to filter by
        'page': '',             # Page number for pagination
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.0; en-US; rv:1.5a) Gecko/20030718',
        'Authorization': f'Bearer {API_TOKEN}',  # Replace YOUR_ACCESS_TOKEN with your actual token
    }

    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        data = response.json()  # Convert response to JSON format
        # Process the JSON data here as per your application's needs
        data = [{'name':profile['name'],'id':profile['id']} for profile in data['data']]
        return data
    else:
        return None

def get_listening_ports(process_name):
    command = f"lsof -i -P -n | grep LISTEN | grep {process_name}"
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    output = result.stdout.strip()
    return output

def extract_port_number(listening_ports_output):
    # Разделение строки по пробелам и извлечение второго элемента (номера порта)
    port_number = listening_ports_output.split()[-2]
    return port_number


def main():
    profiles_id = get_browser_profiles()

    if profiles_id:
        req_url = f"http://localhost:3001/v1.0/browser_profiles/{profiles_id[0]['id']}/start?autonation-1"
        response = requests.get(url=req_url)
        response_json = response.json()
        print(response_json)
        current_profile = get_browser_profile(profiles_id[0]['id'])
        time.sleep(4)
        
        process_name = "Anty"
        listening_ports = get_listening_ports(process_name)
        listen_ip = extract_port_number(listening_ports)
        print(f"Listen ip for {process_name}: {listen_ip.strip()}")
        port = listen_ip[-5:]
        print(f"Port: {port}")
        
        chrome_drive_path = Service(executable_path="chromedriver/chromedriver")
        options = webdriver.ChromeOptions()
        options.debugger_address = listen_ip.strip()
        
        try:
            driver = webdriver.Chrome(service=chrome_drive_path, options=options)
            
            driver.get("https://www.mcdonalds.com/ua/uk-ua/product/200390.html#accordion-29309a7a60-item-9ea8a10642")
            
            time.sleep(3)
            
            driver.get("https://whatismyipaddress.com/")
            
            time.sleep(2)
            
        except Exception as e:
            print(f"Exception occurred: {str(e)}")
        
        finally:
            if 'driver' in locals():
                driver.quit()

if __name__ == "__main__":
    main()