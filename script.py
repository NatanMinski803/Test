import requests
import json

COOKIES_IN_FILE = "input_files/cookies.json"  # Путь к входным файлам
COOKIES_OUT_FILE = "output_files/cookies_out.json"  # Путь к выходным файлам
URL = "https://donschool115.eljur.ru/journal-app"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

def load_cookies_from_json(filename):
    with open(filename, encoding="utf-8") as f:
        cookies_data = json.load(f)

    jar = requests.cookies.RequestsCookieJar()
    for cookie in cookies_data:
        jar.set(
            name=cookie["name"],
            value=cookie["value"],
            domain=cookie.get("domain", ""),
            path=cookie.get("path", "/"),
            secure=cookie.get("secure", False),
            rest={"HttpOnly": cookie.get("httpOnly", False)},
            expires=cookie.get("expirationDate"),
        )
    return jar, cookies_data

def save_cookies(session, path, original_cookies):
    original_map = {c["name"]: c for c in original_cookies}
    cookie_list = []

    for c in session.cookies:
        original = original_map.get(c.name, {})
        domain = c.domain or original.get("domain", "")
        origin = f"https://{domain.lstrip('.')}" if domain else "https://"

        cookie_list.append({
            "domain": domain,
            "name": c.name,
            "value": c.value,
            "path": c.path,
            "secure": c.secure,
            "httpOnly": c._rest.get("HttpOnly", False),
            "sameSite": c._rest.get("SameSite", "unspecified"),
            "expirationDate": c.expires if c.expires else None,
            "session": c.expires is None,
            "storeId": "0",
            "hostOnly": False,
            "origin": origin
        })

    with open(path, "w", encoding="utf-8") as f:
        json.dump(cookie_list, f, indent=2, ensure_ascii=False)

def refresh_session():
    print("🔄 Запуск обновления сессии...")
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    cookies, original_cookie_data = load_cookies_from_json(COOKIES_IN_FILE)
    session.cookies.update(cookies)

    try:
        r = session.get(URL)
        if r.status_code == 200:
            print("✅ Успешный запрос, обновление куки...")
        else:
            print(f"⚠️ Ответ сервера: {r.status_code}")
    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")
        return

    save_cookies(session, COOKIES_OUT_FILE, original_cookie_data)
    print(f"💾 Куки сохранены в {COOKIES_OUT_FILE}")

if __name__ == "__main__":
    refresh_session()  # Запускаем скрипт один раз
