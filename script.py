import os
import requests
import time
import json
import subprocess

# Пути к файлам куки
COOKIES_IN_FILE = "input_files/cookies.json"
COOKIES_OUT_FILE = "output_files/cookies_out.json"

# Заголовки
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

# URL-адреса для имитации активности
URLS_TO_VISIT = [
    "https://donschool115.eljur.ru/journal-app",       # журнал
    "https://donschool115.eljur.ru/journal-messages-action",          # сообщения
    "https://donschool115.eljur.ru/journal-user-preferences-action",      # профиль
    "https://donschool115.eljur.ru/journal-student-grades-action",             # оценки
    "https://donschool115.eljur.ru/journal-student-ktp-action",          # домашка
    "https://donschool115.eljur.ru/journal-schedule-action"           # расписание
]

def load_cookies_from_json(filename):
    if not os.path.exists(filename):
        print(f"❌ Файл {filename} не найден!")
        return None, None
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

def imitate_user_activity():
    print("🔄 Запуск имитации активности на сайте Eljur...")
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    cookies, original_cookie_data = load_cookies_from_json(COOKIES_IN_FILE)
    if cookies is None:
        return

    session.cookies.update(cookies)

    for url in URLS_TO_VISIT:
        try:
            print(f"🌐 Переход к: {url}")
            r = session.get(url)
            print(f"  ↳ Статус ответа: {r.status_code}")
            time.sleep(1)  # задержка для реалистичности
        except Exception as e:
            print(f"❌ Ошибка при переходе к {url}: {e}")

    save_cookies(session, COOKIES_OUT_FILE, original_cookie_data)
    print(f"💾 Куки обновлены и сохранены в: {COOKIES_OUT_FILE}")

    # Git commit и push
    print("🔄 Git-пуш изменений...")
    subprocess.run(["git", "add", "."], check=False)
    subprocess.run(["git", "commit", "-m", "Обновлены куки"], check=False)
    subprocess.run(["git", "push"], check=False)
    print("✅ Завершено.")

# Точка входа
if __name__ == "__main__":
    imitate_user_activity()
