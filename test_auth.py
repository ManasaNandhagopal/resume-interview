import requests
import time

SIGNUP_URL = 'http://127.0.0.1:8000/api/auth/signup'
LOGIN_URL = 'http://127.0.0.1:8000/api/auth/login'

signup_payload = {
    'email': 'test+ci@example.com',
    'password': 'TestPass123',
    'full_name': 'CI Test',
    'language': 'en'
}

login_payload = {
    'email': 'test+ci@example.com',
    'password': 'TestPass123'
}

def try_signup():
    for i in range(10):
        try:
            r = requests.post(SIGNUP_URL, json=signup_payload, timeout=5)
            print('SIGNUP:', r.status_code, r.text)
            return r
        except Exception as e:
            print('SIGNUP ERR:', e)
            time.sleep(1)
    return None

def try_login():
    try:
        r = requests.post(LOGIN_URL, json=login_payload, timeout=5)
        print('LOGIN:', r.status_code, r.text)
        return r
    except Exception as e:
        print('LOGIN ERR:', e)
        return None

if __name__ == '__main__':
    print('→ Running signup...')
    s = try_signup()
    time.sleep(0.5)
    print('→ Running login...')
    l = try_login()
    if l is None or l.status_code >= 400:
        raise SystemExit(1)
    print('→ Auth test completed')
