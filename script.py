import os
import requests
import time
import json
import subprocess

# Пути к файлам куки
COOKIES_IN_FILE = "input_files/cookies.json"
COOKIES_OUT_FILE = "output_files/cookies_out.json"

# URL для обновления сессии
URL = "https://donschool115.eljur.ru/journal-app"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

# Интервал обновления куки (в секундах)
REQUEST_INTERVAL = 300  # 5 минут

# Функция для загрузки куки из файла
def load_cookies_from_json(filename):
    if not os.path.exists(filename):  # Проверяем, существует ли файл
        print(f"❌ Файл {filename} не найден!")
        return None, None  # Возвращаем None, если файл не найден

    # Открываем файл и загружаем данные
    with open(filename, encoding="utf-8") as f:
        cookies_data = json.load(f)

    jar = requests.cookies.RequestsCookieJar()  # Создаем контейнер для куки
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

# Функция для сохранения куки в файл
def save_cookies(session, path, original_cookies):
    original_map = {c["name"]: c for c in original_cookies}  # Сопоставляем куки с их исходными данными
    cookie_list = []  # Список для новых куки

    for c in session.cookies:  # Проходим по всем куки в сессии
        original = original_map.get(c.name, {})  # Ищем исходные данные куки
        domain = c.domain or original.get("domain", "")  # Получаем домен
        origin = f"https://{domain.lstrip('.')}" if domain else "https://"

        # Добавляем куки в список
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

    # Сохраняем куки в файл
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cookie_list, f, indent=2, ensure_ascii=False)

# Функция для обновления сессии
def refresh_session():
    print("🔄 Запуск обновления сессии...")
    session = requests.Session()  # Создаем новую сессию
    session.headers.update({"User-Agent": USER_AGENT})  # Обновляем заголовки сессии

    # Загружаем куки из файла
    cookies, original_cookie_data = load_cookies_from_json(COOKIES_IN_FILE)
    if cookies is None:  # Если куки не были загружены, выходим
        return

    session.cookies.update(cookies)  # Обновляем куки в сессии

    try:
        r = session.get(URL)  # Делаем запрос для обновления сессии
        if r.status_code == 200:
            print("✅ Успешный запрос, обновление куки...")
        else:
            print(f"⚠️ Ответ сервера: {r.status_code}")
    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")
        return

    # Сохраняем обновленные куки в файл
    save_cookies(session, COOKIES_OUT_FILE, original_cookie_data)
    print(f"💾 Куки сохранены в {COOKIES_OUT_FILE}")

    # Коммит изменений в репозиторий
    print("🔄 Выполнение коммита и пуша изменений в репозиторий...")
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", "Обновлены куки"])
    subprocess.run(["git", "push"])

# Основная программа
if __name__ == "__main__":
    refresh_session()  # Запускаем обновление сессии
