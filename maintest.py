import requests

url = "https://www.tripadvisor.com/Restaurant_Review-g186334-d13941837-Reviews-Cafe_Delhi-Leicester_Leicestershire_England.html"

payload = {}
headers = {
  'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:128.0) Gecko/20100101 Firefox/128.0',
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8',
  'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
  'Accept-Encoding': 'gzip, deflate, br, zstd',
  'Connection': 'keep-alive',
  'Cookie': f'_ga_QX0Q50ZC9P=GS1.1.17{random_number4}8517.19.0.17{random_number4}8519.58.0.0; TAUnique=%1%enc%3Ae6Cz0rUi9CvCNhsL5v8u%2FFtiYE3%2FyiW0EDOi7KVvePPj8LiWKc8Y4XNH0tB%2BAHD7Nox8JbUSTxk%3D; TADCID=onpi8zDvsAiiYEj0ABQCmq6heh9ZSU2yA8SXn9Wv5H5692ySPc_EMmCgy_LQgeIugvb8szZr315XyBpUGpEx40ADJ60t12J-EU0; TASSK=enc%3AAOGDuBT%2FymKdYEewgCgOJdl99kP6jM2iEOjmh8FdqfAtqEkAEu%2BRiaiBb7Y6YQt9SYEhsDB3HXIokx0C2K31V7EGiEAJGH3FwvqAZCc24Heu5w3tmrF94AnWKcK2GhB%2BLQ%3D%3D; PMC=V2*MS.33*MD.20240625*LD.20240625; _abck=E423D2A3711F6B3092A32DF16AEAB4F2~-1~YAAQHkx1aBhTKQiQAQAAXSWJUQyEvLGtQqQf4LgNVQxlT657/Zrqyl6w6VoJU7Rq/CsGIyxdPPgVUvBrqTRUhoUee/nnGANe3AxDJHeVcjgtcuZ0PBWeXo97G+5ie+XAvksEtpD1gi7zNU8CGM6W2nLUWFkQdZC7RpYbynsMzSMaTeZmMRSk3X7yNR6KNk/NmcuwTt5azfunmT+ND+KL8TXv7p9an+pePh6kOR2W1ih6LFWdSN37eHEYp3jqWG47cbqEei7BxZjVRs7mYz48A6BFBGBjwnkHYEUo3ln/CcqcLMarn2Nt3Z3iFDQ8bzto5wDs1U60VEOQcWRsmCrsRkMGaXjLaj6GWE9xkye0WPgRt9rvy32J0nXSjjVW6TjCsbWyb9slSUtGIkQKATamRJjtK5QVfo3EFZOl+g==~-1~-1~-1; datadome=F477fB018fo77plvnHYhLjnkOaKINDJsHBOFbEhvvY5HDWQKvNzlO67tj5gfkIZP4uNBSFb46eE0Rg0Lo92OXcQg7ZqulqxXC3n6b7GrKsMq0m2SX1d9yFr8bNrFSJRb; TASameSite=1; PAC=AJbRIlGfNc7xu4MpQN7iJJfvrNf-HmBVJeY4x78GTJv2wfhQCM2IHHXJwrfc0RgYMscVipgd2n0CgazduOOaFHfNX66csSf0qQ8lw__2RTlOkF7Jv4cS-1tbuPxJVLfe2Z6QGIv0Rd8fpHdq7yIeXgZ5DvKuGRAg1VvP3InoCCbz3Fig_PcF8ra-A8QnSHsUwG8-bqH89DI1tXjYKDS1V6qWbC4X9iGCrk3CjeOtVxLers6rfZFfucr-tbURq78C7A%3D%3D; OptanonConsent=isGpcEnabled=0&datestamp=Wed+Jun+26+2024+02%3A35%3A16+GMT%2B0300+(%D0%92%D0%BE%D1%81%D1%82%D0%BE%D1%87%D0%BD%D0%B0%D1%8F+%D0%95%D0%B2%D1%80%D0%BE%D0%BF%D0%B0%2C+%D0%BB%D0%B5%D1%82%D0%BD%D0%B5%D0%B5+%D0%B2%D1%80%D0%B5%D0%BC%D1%8F)&version=202310.2.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=0d1b6f8b-25fb-4129-8570-f901a1d419c8&interactionCount=2&landingPath=NotLandingPage&groups=C0001%3A1%2CC0004%3A1%2CC0002%3A1%2CC0003%3A1%2CV2STACK42%3A1&AwaitingReconsent=false&geolocation=NL%3BNH; TATrkConsent=eyJvdXQiOiJTT0NJQUxfTUVESUEiLCJpbiI6IkFEVixBTkEsRlVOQ1RJT05BTCJ9; ab.storage.sessionId.6e55efa5-e689-47c3-a55b-e6d7515a6c5d=%7B%22g%22%3A%22e509cac5-e1af-46e7-5e4b-9cea11b4b36d%22%2C%22e%22%3A17{random_number4}8532073%2C%22c%22%3A17{random_number4}8516396%2C%22l%22%3A17{random_number4}8517073%7D; ab.storage.deviceId.6e55efa5-e689-47c3-a55b-e6d7515a6c5d=%7B%22g%22%3A%224475cc90-d597-3b2b-3c8d-2727d0ac0e76%22%2C%22c%22%3A1712009725648%2C%22l%22%3A17{random_number4}8516396%7D; _ga=GA1.1.1933623039.1712009726; _lc2_fpi=b140173de591--01htdvpjcs55ta01ngct9rpqt1; _lc2_fpi_meta=%7B%22w%22%3A1712009726361%7D; __gads=ID=c3612db02b09ea57:T=1712009727:RT=17{random_number4}8518:S=ALNI_MZ2vYyYwxsbRZpkVeGKTfakttGpcQ; __gpi=UID=00000d8767181424:T=1712009727:RT=17{random_number4}8518:S=ALNI_MYdsnII3IZuqwvvhJE8ReYpzn6SCA; __eoi=ID=959e08674f2f0073:T=1712009727:RT=17{random_number4}8518:S=AA-AfjaD3N0V71grRuZguVsGgqs5; _lr_env_src_ats=false; OptanonAlertBoxClosed=2024-04-04T21:42:29.460Z; eupubconsent-v2=CP8iaEgP8iaEgAcABBENAuEsAP_gAEPgACiQg1NX_D5ebWti8XZUIbtkaYwP55izokQhBhaIEewFwAOG7BgCB2EwNAV4JiACGBAEkiLBAQNlHABUCQAAAIgRiSCMYkWMgTNKJKBAiFMRO0NYCBxmmgFDWQCY5kosszdxmDeAAAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAAAAAAAAAAAAAAAAAAA_cff79LgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEQaoMoACIAFAAXAA4ADwAKgAXAA4AB4AEAAJAAXwAxADKAGgAagA8AB-AEQAJgAUwAqwBcAF0AMQAaAA3gB-AEJAIgAiQBHACWAE0AMAAYYAywBmgDZAHIAPiAfYB-wD_AQAAg4BEYCLAIwARqAjgCOgEiAJKAT8AqABcwC8gF9AMUAZ8A0QBrwDaAG4AOkAdsA-wB_wEIAImAReAj0BIgCVgExQJkAmUBOwCh4FIAUiApMBUgCrAFZAK7gWIBYoC0YFsAWyAt0BcgC6AF2gLvgXkBeYC-gGCANsgm2CbkE3gTfAnDBOUE5gJ0gTrgnaCdwE8AJ5gT7gn6CfwFAAKCBBqAKBACQAdABcAGyARAAwgCdAFyANsAgcEADAA6AFcARAAwgCdAIHBgA4AOgAuADZAIgAYQBcgEDhAAcAHQA2QCIAGEAToAuQCBwoAGAFwAwgEDhgAIAwgEDhwAYAHQBEADCAJ0AgcBFcgACAMIBA4kADAIgAYQCBxQAKADoAiABhAE6AQO.f_wACHwAAAAA; OTAdditionalConsentString=1~43.46.55.61.70.83.89.93.108.117.122.124.135.136.143.144.147.149.159.192.196.202.211.228.230.239.259.266.286.291.311.320.322.323.327.338.367.371.385.394.397.407.413.415.424.430.436.445.453.486.491.494.495.522.523.540.550.559.560.568.574.576.584.587.591.737.802.803.820.821.839.864.899.904.922.931.938.979.981.985.1003.1027.1031.1040.1046.1051.1053.1067.1085.1092.1095.1097.1099.1107.1135.1143.1149.1152.1162.1166.1186.1188.1205.1215.1226.1227.1230.1252.1268.1270.1276.1284.1290.1301.1307.1312.1345.1356.1364.1365.1375.1403.1415.1416.1421.1423.1440.1449.1455.1495.1512.1516.1525.1540.1548.1555.1558.1570.1577.1579.1583.1584.1591.1603.1616.1638.1651.1653.1659.1667.1677.1678.1682.1697.1699.1703.1712.1716.1721.1725.1732.1745.1750.1765.1782.1786.1800.1810.1825.1827.1832.1838.1840.1842.1843.1845.1859.1866.1870.1878.1880.1889.1899.1917.1929.1942.1944.1962.1963.1964.1967.1968.1969.1978.1985.1987.2003.2008.2027.2035.2039.2047.2052.2056.2064.2068.2072.2074.2088.2090.2103.2107.2109.2115.2124.2130.2133.2135.2137.2140.2145.2147.2150.2156.2166.2177.2183.2186.2205.2213.2216.2219.2220.2222.2225.2234.2253.2279.2282.2292.2299.2305.2309.2312.2316.2322.2325.2328.2331.2334.2335.2336.2337.2343.2354.2357.2358.2359.2370.2376.2377.2387.2392.2400.2403.2405.2407.2411.2414.2416.2418.2425.2440.2447.2461.2462.2465.2468.2472.2477.2481.2484.2486.2488.2493.2498.2499.2501.2510.2517.2526.2527.2532.2535.2542.2552.2563.2564.2567.2568.2569.2571.2572.2575.2577.2583.2584.2596.2604.2605.2608.2609.2610.2612.2614.2621.2628.2629.2633.2636.2642.2643.2645.2646.2650.2651.2652.2656.2657.2658.2660.2661.2669.2670.2677.2681.2684.2687.2690.2695.2698.2713.2714.2729.2739.2767.2768.2770.2772.2784.2787.2791.2792.2798.2801.2805.2812.2813.2816.2817.2821.2822.2827.2830.2831.2834.2838.2839.2844.2846.2849.2850.2852.2854.2860.2862.2863.2865.2867.2869.2873.2874.2875.2876.2878.2880.2881.2882.2883.2884.2886.2887.2888.2889.2891.2893.2894.2895.2897.2898.2900.2901.2908.2909.2916.2917.2918.2919.2920.2922.2923.2927.2929.2930.2931.2940.2941.2947.2949.2950.2956.2958.2961.2963.2964.2965.2966.2968.2973.2975.2979.2980.2981.2983.2985.2986.2987.2994.2995.2997.2999.3000.3002.3003.3005.3008.3009.3010.3012.3016.3017.3018.3019.3024.3025.3028.3034.3038.3043.3048.3052.3053.3055.3058.3059.3063.3066.3068.3070.3073.3074.3075.3076.3077.3078.3089.3090.3093.3094.3095.3097.3099.3100.3106.3109.3112.3117.3119.3126.3127.3128.3130.3135.3136.3145.3150.3151.3154.3155.3163.3167.3172.3173.3182.3183.3184.3185.3187.3188.3189.3190.3194.3196.3209.3210.3211.3214.3215.3217.3219.3222.3223.3225.3226.3227.3228.3230.3231.3234.3235.3236.3237.3238.3240.3244.3245.3250.3251.3253.3257.3260.3270.3272.3281.3288.3290.3292.3293.3296.3299.3300.3306.3307.3309.3314.3315.3316.3318.3324.3328.3330.3331.3531.3731.3831.3931.4131.4531.4631.4731.4831.5231.6931.7031.7235.7831.7931.8931.9731.10231.10631.10831.11031.11531.12831.13632.13731.14237.15731.16831.21233.23031.24431.24533.25731.25931.26031.26831; __vt=mrOdLldpiShvkgTFABQCwRB1grfcRZKTnW7buAoPsS5Y1I1nBR_VaolvRMjIeSb9Ultpi0fXk-9uCxsBIfYaNDh1pwfX2vbNPawoLekXSuuLaJWUzKgnSN3ppoIhJzldb-o1PMbhcQNxJUgouDsvOVVMUw; bm_sz=717CC510853474FF1BF85C0B0EEDBC48~YAAQJpNOUhjB+0mQAQAAlOjAURhWRgYaZrjP07HsQyU5A1QZyj11+3aSqIypI3pL3qJb5vS21apUG61ih8wbkUGDOqh995dgrIDbrWt+sjwqjgPL/4peCHx2MtG5iAy9TGn3GYwIkh62ifgSiodybefB1OzdCCme4O4fWcsCcxu9ZNpas6hE872DeqEdWwNO9hYpGhZsUCgcfN+xi3sYy1Sa/pb4Vf3q8wz33rQ9IJeuA3zSXRnkaKn6ScTO0vxsv6tCElwECKR+4yst385NFIA3QiSgZKbwMr+jzHIcmGwOQBlumAS05Ml7UhHYkjksDqq9ygU4hwLA9C0lmCCSIREC7OIGOOL6D2m2NBo8NilXFWDaHjvmm0YTKzb1DsQGKUNO9a2+rpblD+WEDE+WBVoxyxnYKcmcqCnK0BH/bx/x8YoMzs3sp8BZ7ajoIWFx9yt2qnM8k7xK0mGkqqjlw/lhVGTeVKF9Ez1KGhtQV18lIWXp9jrYhjYP4oxmThBHhQl6xrOE1hA1oC4D~4337733~3359041; TASession=V2ID.339CA6F8C9CA42BE9D8D66043223EDA6*SQ.39*LS.Restaurant_Review*HS.recommended*ES.popularity*DS.5*SAS.popularity*FPS.oldFirst*FA.1*DF.0*TRA.true*LD.13941837*EAU._; TART=%1%enc%3Aow1Pn5NMRnCw%2F9qBT5n2N5qF6dOTKw0Wg2ZRWIAoJ%2BZ2y59yncnj43Rhj7usPIi92DLYSqqkTAk%3D; pbjs_sharedId=d3f7571c-878c-4464-9715-b30c0b066b2c; pbjs_sharedId_cst=CSzfLKsskA%3D%3D; _gcl_aw=GCL.17{random_number4}8517.null; _gcl_au=1.1.1147577779.17{random_number4}4866; _lr_sampling_rate=100; pbjs_unifiedID=%7B%22TDID%22%3A%22ad39d9d0-b46f-4336-9a43-3011dd74070f%22%2C%22TDID_LOOKUP%22%3A%22FALSE%22%2C%22TDID_CREATED_AT%22%3A%222024-06-25T22%3A34%3A37%22%7D; pbjs_unifiedID_cst=CSzfLKsskA%3D%3D; ServerPool=B; TATravelInfo=V2*A.2*MG.-1*HP.2*FL.3*RS.1; TAUD=LA-17{random_number4}4888711-1*RDD-1-2024_06_26*LG-3626527-2.1.F.*LD-3626528-.....; TASID=339CA6F8C9CA42BE9D8D66043223EDA6; _lr_retry_request=true; CM=%1%sesswifi%2C%2C-1%7CPremiumMobSess%2C%2C-1%7Ct4b-pc%2C%2C-1%7CRCPers%2C%2C-1%7Csesstch15%2C%2C-1%7CRestAds%2FRPers%2C%2C-1%7CCYLPUSess%2C%2C-1%7CTheForkMCCPers%2C%2C-1%7Ctvsess%2C%2C-1%7CTBPers%2C%2C-1%7Cperstch15%2C%2C-1%7CRestPremRSess%2C%2C-1%7CCCSess%2C%2C-1%7CCYLSess%2C%2C-1%7CPremRetPers%2C%2C-1%7Cpershours%2C%2C-1%7C%24%2C%2C-1%7Csesssticker%2C%2C-1%7CPremiumORSess%2C%2C-1%7Ct4b-sc%2C%2C-1%7CMC_IB_UPSELL_IB_LOGOS2%2C%2C-1%7CTrayspers%2C%2C-1%7Cb2bmcpers%2C%2C-1%7CPremMCBtmSess%2C%2C-1%7CMC_IB_UPSELL_IB_LOGOS%2C%2C-1%7Csess_rev%2C%2C-1%7Csessamex%2C%2C-1%7CPremiumRRSess%2C%2C-1%7CTADORSess%2C%2C-1%7CMCPPers%2C%2C-1%7Csesshours%2C%2C-1%7CSPMCSess%2C%2C-1%7CTheForkORSess%2C%2C-1%7Cpers_rev%2C%2C-1%7Cmdpers%2C%2C-1%7CTheForkRRSess%2C%2C-1%7CRestAds%2FRSess%2C%2C-1%7CPremiumMobPers%2C%2C-1%7CRCSess%2C%2C-1%7CRestAdsCCSess%2C%2C-1%7Csesslaf%2C%2C-1%7CRestPremRPers%2C%2C-1%7CCYLPUPers%2C%2C-1%7Cperslaf%2C%2C-1%7CRevHubRMPers%2C%2C-1%7Cpssamex%2C%2C-1%7CTheForkMCCSess%2C%2C-1%7CCYLPers%2C%2C-1%7CCCPers%2C%2C-1%7Ctvpers%2C%2C-1%7CTBSess%2C%2C-1%7Cb2bmcsess%2C%2C-1%7Cperswifi%2C%2C-1%7CPremRetSess%2C%2C-1%7CRevHubRMSess%2C%2C-1%7CPremiumRRPers%2C%2C-1%7CRestAdsCCPers%2C%2C-1%7CMCPSess%2C%2C-1%7CTADORPers%2C%2C-1%7CTheForkORPers%2C%2C-1%7CTrayssess%2C%2C-1%7CPremMCBtmPers%2C%2C-1%7CTheForkRRPers%2C%2C-1%7CPremiumORPers%2C%2C-1%7Cperssticker%2C%2C-1%7CSPORPers%2C%2C-1%7Cbooksticks%2C%2C-1%7Cbookstickp%2C%2C-1%7Cmdsess%2C%2C-1%7C; datadome=GltthGER4N0CMKStnmCsaK8NiC9~D09rAu8Ev20MGDFGp3KkjNyOvf8_7zs4Me1s5P0yGMRtevZfzer2_FiKDBhgqjZr66sJGrNbb2f_xb2An_la9_EFYM7wOYRG2_Ff',
  'Upgrade-Insecure-Requests': '1',
  'Sec-Fetch-Dest': 'document',
  'Sec-Fetch-Mode': 'navigate',
  'Sec-Fetch-Site': 'none',
  'Sec-Fetch-User': '?1',
  'Priority': 'u=0, i'
}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)
