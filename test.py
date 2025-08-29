def check_today_anime(user_id=None):
    encourage_message = random.choice(ENCOURAGE_MESSAGES)
    url = "https://www.livechart.me/schedule/tv"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0'}
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=2, status_forcelist=[429, 500, 502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))
    try:
        response = session.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        today_anime = []
        anime_list = load_anime_list()
        user_anime = {a['name'].lower(): a for a in anime_list.get(user_id, [])} if user_id else {}
        top_anime = {a['name'].lower() for a in anime_list.get(user_id, []) if a.get('is_top', False)} if user_id else set()
        if not user_anime:
            logger.info(f"Список аниме для user_id {user_id} пуст")
            return "У вас нет отслеживаемых аниме. Добавьте с помощью /add."
        today_container = soup.find('div', class_='lc-timetable-day lc-today')
        if not today_container:
            logger.info("Контейнер lc-timetable-day lc-today не найден")
            return "Нет аниме в расписании на сегодня."
        schedule = today_container.find_all('div', class_='lc-timetable-anime-block')
        for entry in schedule:
            if 'data-schedule-anime-title' not in entry.attrs or not entry['data-schedule-anime-title'].strip():
                logger.debug(f"Пропущена карточка без атрибута data-schedule-anime-title")
                continue
            title = entry['data-schedule-anime-title'].strip().lower()
            matched_anime = None
            matched_anime_entry = None
            for anime_name, anime in user_anime.items():
                if anime_name in title or (anime.get('alt_name') and anime['alt_name'].lower() in title):
                    matched_anime = anime_name
                    matched_anime_entry = anime
                    break
            if not matched_anime:
                logger.debug(f"Аниме '{title}' не в списке пользователя, пропускаем")
                continue
            episode_number = None
            release_label = entry.find('a', class_='lc-tt-release-label')
            if release_label:
                episode_text = release_label.text.strip()
                episode_match = re.search(r'(?:EP|Episode|Epi.?)?(\d+)', episode_text, re.IGNORECASE)
                if episode_match:
                    episode_number = episode_match.group(1)
                    logger.debug(f"Найден номер эпизода в lc-tt-release-label: {episode_number} для '{title}'")
                else:
                    logger.debug(f"Номер эпизода не найден в lc-tt-release-label: {episode_text} для '{title}'")
            else:
                logger.debug(f"Элемент lc-tt-release-label не найден для '{title}'")
            alt_name = None
            if matched_anime_entry and matched_anime_entry.get('alt_name'):
                alt_name = matched_anime_entry['alt_name']
                logger.debug(f"Использовано сохранённое второе название для '{title}': {alt_name}")
            else:
                anime_link_elem = entry.find('a', href=lambda x: x and '/anime/' in x)
                if anime_link_elem:
                    href = anime_link_elem['href'].strip(':').rstrip('/')
                    anime_url = 'https://www.livechart.me' + href
                    logger.debug(f"Извлечён URL аниме: {anime_url} для '{title}'")
                    for attempt in range(3):
                        try:
                            anime_response = session.get(anime_url, headers=headers, timeout=15)
                            anime_response.raise_for_status()
                            anime_soup = BeautifulSoup(anime_response.text, 'html.parser')
                            main_div = anime_soup.find('div', class_='hidden md:block text-base-content/50')
                            if main_div:
                                inner_divs = main_div.find_all('div', recursive=False)
                                logger.debug(f"Найдено {len(inner_divs)} внутренних div в первом 'hidden md:block text-base-content/50' для '{title}'")
                                if len(inner_divs) >= 2:
                                    alt_name = inner_divs[1].text.strip()
                                    if alt_name:
                                        logger.info(f"Найдено второе название (новая логика) для '{title}': {alt_name}")
                                    else:
                                        logger.debug(f"Второе название пустое (новая логика) для '{title}' по URL {anime_url}")
                            if not alt_name:
                                alt_name_divs = anime_soup.find_all('div', class_='hidden md:block text-base-content/50')
                                logger.debug(f"Проверяем старую логику: найдено {len(alt_name_divs)} div с классом 'hidden md:block text-base-content/50' для '{title}'")
                                if len(alt_name_divs) >= 2:
                                    alt_name = alt_name_divs[1].text.strip()
                                    if alt_name:
                                        logger.info(f"Найдено второе название (старая логика) для '{title}': {alt_name}")
                                    else:
                                        logger.debug(f"Второе название пустое (старая логика) для '{title}' по URL {anime_url}")
                                else:
                                    logger.debug(f"Второе название не найдено (старая логика) для '{title}' по URL {anime_url}, найдено {len(alt_name_divs)} элементов")
                            break
                        except requests.exceptions.RequestException as e:
                            if isinstance(e, requests.exceptions.HTTPError) and e.response.status_code == 429:
                                delay = 2 ** attempt + 1
                                logger.warning(f"Ошибка 429 для '{title}' по URL {anime_url}, попытка {attempt + 1}/3, ждём {delay} сек")
                                sleep(delay)
                            else:
                                logger.warning(f"Ошибка получения второго названия для '{title}' по URL {anime_url}: {e}")
                                break
                    else:
                        logger.error(f"Не удалось получить второе название для '{title}' по URL {anime_url} после 3 попыток")
                else:
                    logger.debug(f"Ссылка на страницу аниме не найдена для '{title}'")
                sleep(2)
            if matched_anime_entry and matched_anime_entry.get('alt_name') != alt_name:
                save_anime(
                    user_id, matched_anime_entry['name'], matched_anime_entry.get('last_torrent_id'),
                    matched_anime_entry.get('is_top', False), matched_anime_entry.get('filters', []),
                    matched_anime_entry.get('last_episode_number'), alt_name, 
                    matched_anime_entry.get('last_gdrive_link')
                )
            entry_text = f"{matched_anime_entry['name']}"
            if episode_number:
                entry_text += f" (EP{episode_number})"
            if matched_anime in top_anime:
                entry_text += " — ЗАПИСАТЬ СЕГОДНЯ!"
            today_anime.append(entry_text)
            logger.info(f"Добавлено аниме в список: {matched_anime_entry['name']} (соответствует {matched_anime}, эпизод: {episode_number if episode_number else 'не указан'}, alt_name: {alt_name})")
        if not today_anime:
            return f"{encourage_message} \n\nДорогая, сегодня у тебя нет новых серий аниме. Отдыхай, котенок!"
        return "Дорогая, сегодня у тебя работа:\n" + "\n".join(sorted(today_anime)) + f"\n {encourage_message}"
    except Exception as e:
        logger.error(f"Ошибка при проверке LiveChart.me: {e}", exc_info=True)
        return "Не удалось загрузить расписание с LiveChart.me."
