from datetime import datetime, timedelta
import pytz
from googleapiclient.errors import HttpError

# Глобальный кэш для результатов API
video_cache = {'timestamp': None, 'videos': None, 'shorts': None}
CHANNEL_ID = 'UCSYnLE11DE8q5Q9eqbG5eTw'  # Фиксированный channel_id

def load_last_content_id(user_id, content_type):
    try:
        collection = init_mongo()['youtube']
        entry = collection.find_one({'user_id': user_id, 'channel': 'loveanddeepspace', 'content_type': content_type})
        if entry and 'last_content_id' in entry:
            last_content_id = entry['last_content_id']
            last_published_at = entry.get('last_published_at')
            logger.debug(f"Загружен last_{content_type}_id '{last_content_id}', last_published_at={last_published_at} для user_id {user_id}")
            return last_content_id, last_published_at
        logger.warning(f"Запись для user_id {user_id}, content_type {content_type} не найдена или отсутствует last_content_id")
        return None, None
    except Exception as e:
        logger.error(f"Ошибка загрузки last_{content_type}_id для user_id {user_id}: {e}", exc_info=True)
        return None, None

def save_last_content_id(user_id, content_type, video_id, published_at):
    try:
        collection = init_mongo()['youtube']
        collection.update_one(
            {'user_id': user_id, 'channel': 'loveanddeepspace', 'content_type': content_type},
            {'$set': {'last_content_id': video_id, 'last_published_at': published_at}},
            upsert=True
        )
        logger.info(f"Сохранён last_{content_type}_id '{video_id}', last_published_at={published_at} для user_id {user_id}")
    except Exception as e:
        logger.error(f"Ошибка сохранения last_{content_type}_id для user_id {user_id}: {e}", exc_info=True)

def check_new_videos(user_id, content_type):
    global video_cache
    youtube = init_youtube()
    if not youtube:
        logger.error(f"Ошибка инициализации YouTube API для user_id {user_id}")
        return {'error': "Не удалось открыть YouTube API. Проверьте YOUTUBE_API_KEY."}
    
    try:
        last_content_id, last_published_at = load_last_content_id(user_id, content_type)
        logger.debug(f"Проверка {content_type} для user_id {user_id}: last_content_id='{last_content_id}', last_published_at={last_published_at}")
        
        now = datetime.now(pytz.UTC)
        cache_valid = video_cache['timestamp'] and (now - video_cache['timestamp']).total_seconds() < 3600  # 60 минут
        if cache_valid and video_cache[content_type]:
            logger.debug(f"Используется кэшированный результат для {content_type}, user_id {user_id}")
            response = video_cache[content_type]
        else:
            search_query = {
                'part': 'snippet',
                'channelId': CHANNEL_ID,
                'maxResults': 2,
                'order': 'date',
                'type': 'video'
            }
            if content_type == 'shorts':
                search_query['videoDuration'] = 'short'
            try:
                request = youtube.search().list(**search_query)
                response = request.execute()
                logger.debug(f"Ответ YouTube API для {content_type}, user_id {user_id}: {response}")
                video_cache[content_type] = response
                video_cache['timestamp'] = now
            except HttpError as e:
                logger.error(f"Ошибка YouTube API для {content_type}, user_id {user_id}: {e}")
                return {'error': f"Не удалось проверить новые {content_type}: {str(e)}"}
        
        if not response.get('items'):
            logger.info(f"Нет новых {content_type} на канале @loveanddeepspace (ID: {CHANNEL_ID}) для user_id {user_id}")
            return {'error': f"Нет {content_type} на канале Love and Deepspace."}
        
        for video in response['items']:
            video_id = video['id']['videoId']
            published_at = video['snippet']['publishedAt']
            published_date = datetime.strptime(published_at, '%Y-%m-%dT%H:%M:%S%z')
            logger.debug(f"Анализ {content_type} с ID {video_id}, publishedAt={published_at} для user_id {user_id}")
            
            try:
                video_details = youtube.videos().list(
                    part='contentDetails,snippet',
                    id=video_id
                ).execute()
                if not video_details.get('items'):
                    logger.info(f"Не удалось получить детали для {content_type} {video_id} для user_id {user_id}")
                    continue
                
                content_details = video_details['items'][0]['contentDetails']
                duration = parse_iso_duration(content_details['duration'])
                if content_type == 'shorts' and duration > 60:
                    logger.info(f"Видео {video_id} не является шортсом (длительность: {duration} секунд) для user_id {user_id}")
                    continue
                elif content_type == 'video' and duration <= 60:
                    logger.info(f"Видео {video_id} не является видео (длительность: {duration} секунд) для user_id {user_id}")
                    continue
                
                other_content_type = 'shorts' if content_type == 'video' else 'video'
                last_other_content_id, _ = load_last_content_id(user_id, other_content_type)
                if video_id == last_other_content_id:
                    logger.info(f"{content_type.capitalize()} {video_id} пропущен для user_id {user_id}, так как совпадает с последним {other_content_type}")
                    continue
                
                if video_id == last_content_id:
                    logger.info(f"{content_type.capitalize()} {video_id} уже обработан для user_id {user_id} (publishedAt: {published_at})")
                    continue
                
                if last_published_at:
                    last_published_date = datetime.strptime(last_published_at, '%Y-%m-%dT%H:%M:%S%z')
                    if published_date <= last_published_date:
                        logger.info(f"{content_type.capitalize()} {video_id} пропущен для user_id {user_id}, так как не новее последнего обработанного (publishedAt: {published_at} <= {last_published_at})")
                        continue
                
                if (now - published_date).total_seconds() > 24 * 3600:
                    logger.info(f"{content_type.capitalize()} {video_id} пропущен для user_id {user_id}, так как слишком старое (publishedAt: {published_at})")
                    continue
                
                video_title = video['snippet']['title']
                video_url = f"https://www.youtube.com/watch?v={video_id}" if content_type == 'video' else f"https://www.youtube.com/shorts/{video_id}"
                logger.info(f"Найден новый {content_type}: {video_title} (ID: {video_id}, длительность: {duration} секунд, publishedAt: {published_at}) для user_id {user_id}")
                return {'title': video_title, 'url': video_url, 'video_id': video_id, 'published_at': published_at}
            
            except HttpError as e:
                logger.error(f"Ошибка получения деталей для {content_type} {video_id}, user_id {user_id}: {e}")
                continue
        
        logger.info(f"Не найдено новых {content_type} для user_id {user_id} после проверки всех видео")
        return {'error': f"Нет новых {content_type} для обработки."}
    
    except Exception as e:
        logger.error(f"Ошибка проверки новых {content_type} на YouTube для user_id {user_id}: {e}", exc_info=True)
        return {'error': f"Не удалось проверить новые {content_type}: {str(e)}"}

def get_latest_content(update, context):
    user_id = str(update.effective_user.id)
    youtube = init_youtube()
    if not youtube:
        logger.error(f"Ошибка инициализации YouTube API для user_id {user_id}")
        update.message.reply_text("Не удалось открыть YouTube API.")
        return
    
    try:
        now = datetime.now(pytz.UTC)
        
        # Проверка видео
        cache_valid = video_cache['timestamp'] and (now - video_cache['timestamp']).total_seconds() < 3600
        if cache_valid and video_cache['videos']:
            logger.debug(f"Используется кэшированный результат для video, user_id {user_id}")
            response = video_cache['videos']
        else:
            search_query = {
                'part': 'snippet',
                'channelId': CHANNEL_ID,
                'maxResults': 2,
                'order': 'date',
                'type': 'video'
            }
            try:
                request = youtube.search().list(**search_query)
                response = request.execute()
                logger.debug(f"Ответ YouTube API для video, user_id {user_id}: {response}")
                video_cache['videos'] = response
                video_cache['timestamp'] = now
            except HttpError as e:
                logger.error(f"Ошибка YouTube API для video, user_id {user_id}: {e}")
                update.message.reply_text(f"Не удалось получить последнее видео: {str(e)}")
                return
        
        video_found = False
        if response.get('items'):
            for video in response['items']:
                video_id = video['id']['videoId']
                published_at = video['snippet']['publishedAt']
                logger.debug(f"Анализ video с ID {video_id}, publishedAt={published_at} для user_id {user_id}")
                
                try:
                    video_details = youtube.videos().list(
                        part='contentDetails,snippet',
                        id=video_id
                    ).execute()
                    if not video_details.get('items'):
                        logger.info(f"Не удалось получить детали для video {video_id} для user_id {user_id}")
                        continue
                    
                    content_details = video_details['items'][0]['contentDetails']
                    duration = parse_iso_duration(content_details['duration'])
                    if duration <= 60:
                        logger.info(f"Видео {video_id} не является видео (длительность: {duration} секунд) для user_id {user_id}")
                        continue
                    
                    video_title = video['snippet']['title']
                    video_url = f"https://www.youtube.com/watch?v={video_id}"
                    update.message.reply_text(f"Последнее видео на канале Love and Deepspace:\nНазвание: {video_title}\nСсылка: {video_url}")
                    logger.info(f"Отправлено последнее видео пользователю {user_id}: {video_id}")
                    video_found = True
                    break
                
                except HttpError as e:
                    logger.error(f"Ошибка получения деталей для video {video_id}, user_id {user_id}: {e}")
                    continue
        
        # Проверка шортсов
        if cache_valid and video_cache['shorts']:
            logger.debug(f"Используется кэшированный результат для shorts, user_id {user_id}")
            response = video_cache['shorts']
        else:
            search_query = {
                'part': 'snippet',
                'channelId': CHANNEL_ID,
                'maxResults': 2,
                'order': 'date',
                'type': 'video',
                'videoDuration': 'short'
            }
            try:
                request = youtube.search().list(**search_query)
                response = request.execute()
                logger.debug(f"Ответ YouTube API для shorts, user_id {user_id}: {response}")
                video_cache['shorts'] = response
                video_cache['timestamp'] = now
            except HttpError as e:
                logger.error(f"Ошибка YouTube API для shorts, user_id {user_id}: {e}")
                update.message.reply_text(f"Не удалось получить последний шортс: {str(e)}")
                return
        
        shorts_found = False
        if response.get('items'):
            for video in response['items']:
                video_id = video['id']['videoId']
                published_at = video['snippet']['publishedAt']
                logger.debug(f"Анализ shorts с ID {video_id}, publishedAt={published_at} для user_id {user_id}")
                
                try:
                    video_details = youtube.videos().list(
                        part='contentDetails,snippet',
                        id=video_id
                    ).execute()
                    if not video_details.get('items'):
                        logger.info(f"Не удалось получить детали для shorts {video_id} для user_id {user_id}")
                        continue
                    
                    content_details = video_details['items'][0]['contentDetails']
                    duration = parse_iso_duration(content_details['duration'])
                    if duration > 60:
                        logger.info(f"Видео {video_id} не является шортсом (длительность: {duration} секунд) для user_id {user_id}")
                        continue
                    
                    video_title = video['snippet']['title']
                    video_url = f"https://www.youtube.com/shorts/{video_id}"
                    update.message.reply_text(f"Последний шортс на канале Love and Deepspace:\nНазвание: {video_title}\nСсылка: {video_url}")
                    logger.info(f"Отправлено последний шортс пользователю {user_id}: {video_id}")
                    shorts_found = True
                    break
                
                except HttpError as e:
                    logger.error(f"Ошибка получения деталей для shorts {video_id}, user_id {user_id}: {e}")
                    continue
        
        if not video_found and not shorts_found:
            logger.info(f"Не найдено ни видео, ни шортсов для user_id {user_id}")
            update.message.reply_text("Не удалось найти ни видео, ни шортсов на канале Love and Deepspace.")
    
    except Exception as e:
        logger.error(f"Ошибка получения последнего контента для user_id {user_id}: {e}", exc_info=True)
        update.message.reply_text("Произошла ошибка при получении последнего контента.")

def last_video(update, context):
    try:
        get_latest_content(update, context)
    except Exception as e:
        logger.error(f"Ошибка в обработчике last_video для user_id {update.effective_user.id}: {e}", exc_info=True)
        update.message.reply_text("Произошла ошибка при получении последнего контента.")

def get_last_shorts(update, context):
    user_id = str(update.effective_user.id)
    result = check_new_videos(user_id, 'shorts')
    if result and 'error' not in result:
        message = f"Последний шортс на канале Love and Deepspace:\nНазвание: {result['title']}\nСсылка: {result['url']}"
        update.message.reply_text(message)
        logger.info(f"Отправлено последний шортс пользователю {user_id}: {result['video_id']}")
    else:
        update.message.reply_text(result.get('error', 'Не удалось получить последний шортс.'))
        logger.info(f"Не удалось отправить последний шортс пользователю {user_id}: {result.get('error', 'Неизвестная ошибка')}")

def send_new_videos(context):
    bot = context.bot
    try:
        collection = init_mongo()['youtube']
        users = collection.find().distinct('user_id')
        logger.info(f"Запуск send_new_videos для пользователей: {users}")
        for user_id in users:
            if not are_notifications_enabled(user_id):
                logger.info(f"Уведомления отключены для user_id {user_id}, пропускаем")
                continue
            new_video = check_new_videos(user_id, 'video')
            if new_video and 'error' not in new_video:
                message = f"Новое видео на канале Love and Deepspace:\nНазвание: {new_video['title']}\nСсылка: {new_video['url']}"
                if send_message_with_retry(bot, user_id, message):
                    save_last_content_id(user_id, 'video', new_video['video_id'], new_video['published_at'])
                    logger.info(f"Сохранён last_video_id '{new_video['video_id']}' после отправки для user_id {user_id}")
                else:
                    logger.error(f"Не удалось отправить сообщение о новом видео для user_id {user_id}, ID: {new_video['video_id']}")
            elif new_video and 'error' in new_video:
                logger.info(f"Ошибка для video user_id {user_id}: {new_video['error']}")
            new_shorts = check_new_videos(user_id, 'shorts')
            if new_shorts and 'error' not in new_shorts:
                last_video_id, _ = load_last_content_id(user_id, 'video')
                if new_shorts['video_id'] != last_video_id:
                    message = f"Новый шортс на канале Love and Deepspace:\nНазвание: {new_shorts['title']}\nСсылка: {new_shorts['url']}"
                    if send_message_with_retry(bot, user_id, message):
                        save_last_content_id(user_id, 'shorts', new_shorts['video_id'], new_shorts['published_at'])
                        logger.info(f"Сохранён last_shorts_id '{new_shorts['video_id']}' после отправки для user_id {user_id}")
                    else:
                        logger.error(f"Не удалось отправить сообщение о новом шортсе для user_id {user_id}, ID: {new_shorts['video_id']}")
                else:
                    logger.info(f"Шортс {new_shorts['video_id']} пропущен для user_id {user_id}, так как совпадает с последним видео")
            elif new_shorts and 'error' in new_shorts:
                logger.info(f"Ошибка для shorts user_id {user_id}: {new_shorts['error']}")
    except Exception as e:
        logger.error(f"Ошибка в send_new_videos: {e}", exc_info=True)

# Настройка apscheduler
from apscheduler.schedulers.background import BackgroundScheduler

def setup_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_new_videos, 'interval', minutes=60, args=[bot_context])  # 60 минут
    scheduler.add_job(send_daily_schedule, 'cron', hour=6, minute=30, args=[bot_context])  # 09:00 MSK (UTC 06:30)
    scheduler.start()