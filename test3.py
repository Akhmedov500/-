import aiohttp
import asyncio
from datetime import date
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, InlineQueryHandler

TMDB_API_KEY = "5964ad98001f8a9d599fbd007eaea99b"
TELEGRAM_TOKEN = "8697060809:AAFXtcA2X13CHMbrqRqHHQtK6hqu1bZP-1E"

GENRES = {
    28: "Боевик", 12: "Приключения", 16: "Анимация", 35: "Комедия",
    80: "Криминал", 99: "Документальный", 18: "Драма", 10751: "Семейный",
    14: "Фэнтези", 36: "История", 27: "Ужасы", 10402: "Музыка",
    9648: "Детектив", 10749: "Мелодрама", 878: "Фантастика",
    10770: "ТВ фильм", 53: "Триллер", 10752: "Военный", 37: "Вестерн"
}

imdb_cache = {}


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.json()


async def get_movies_async(endpoint, pages=1):
    urls = [
        f"https://api.themoviedb.org/3/{endpoint}?api_key={TMDB_API_KEY}&language=ru-RU&page={page}"
        for page in range(1, pages + 1)
    ]
    async with aiohttp.ClientSession() as session:
        results = await asyncio.gather(*[fetch(session, url) for url in urls])
    movies = []
    for r in results:
        movies += r.get("results", [])
    return movies


async def get_soon_async(today, pages=3):
    urls = [
        f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&language=ru-RU&primary_release_date.gte={today}&sort_by=popularity.desc&page={page}"
        for page in range(1, pages + 1)
    ]
    async with aiohttp.ClientSession() as session:
        results = await asyncio.gather(*[fetch(session, url) for url in urls])
    movies = []
    for r in results:
        movies += r.get("results", [])
    return movies


async def get_imdb_ids_async(movie_ids):
    urls = {
        movie_id: f"https://api.themoviedb.org/3/movie/{movie_id}/external_ids?api_key={TMDB_API_KEY}"
        for movie_id in movie_ids
        if movie_id not in imdb_cache
    }
    if urls:
        async with aiohttp.ClientSession() as session:
            results = await asyncio.gather(*[fetch(session, url) for url in urls.values()])
        for movie_id, result in zip(urls.keys(), results):
            imdb_cache[movie_id] = result.get("imdb_id")


def format_movies(movies, start, end):
    text = ""
    for i, movie in enumerate(movies[start:end], start + 1):
        title = movie["title"]
        if len(title) > 16:
            title = title[:13] + "..."
        year = movie.get("release_date", "????")[:4]
        rating = round(movie.get("vote_average", 0), 1)
        text += f"{i}. [{title} ({year})](https://www.themoviedb.org/movie/{movie['id']}) ⭐ {rating}\n"
    return text


def nav_keyboard(current, total_pages, prefix):
    buttons = []
    if current > 0:
        buttons.append(InlineKeyboardButton("◀ Назад", callback_data=f"{prefix}_{current - 1}"))
    buttons.append(InlineKeyboardButton("Главная", callback_data="home"))
    if current < total_pages - 1:
        buttons.append(InlineKeyboardButton("Дальше ▶", callback_data=f"{prefix}_{current + 1}"))
    return InlineKeyboardMarkup([buttons])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "Привет! 🎬\n\n/popular — популярные фильмы недели\n/top — топ всех времён\n/soon — скоро в кино\n"
    await update.message.reply_text(text)


async def popular(update: Update, context: ContextTypes.DEFAULT_TYPE):
    loading = await update.message.reply_text("⏳ Загружаю...")
    movies = await get_movies_async("trending/movie/week", pages=3)
    context.user_data["popular"] = movies
    await loading.delete()
    text = "🎬 Популярное за неделю:\n\n" + format_movies(movies, 0, 10)
    await update.message.reply_text(text, parse_mode="Markdown",
                                    disable_web_page_preview=True,
                                    reply_markup=nav_keyboard(0, 5, "popular"))


async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    loading = await update.message.reply_text("⏳ Загружаю...")
    movies = await get_movies_async("movie/top_rated", pages=3)
    context.user_data["top"] = movies
    await loading.delete()
    text = "🏆 Топ фильмов всех времён:\n\n" + format_movies(movies, 0, 10)
    await update.message.reply_text(text, parse_mode="Markdown",
                                    disable_web_page_preview=True,
                                    reply_markup=nav_keyboard(0, 5, "top"))


async def soon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    loading = await update.message.reply_text("⏳ Загружаю...")
    today = date.today().isoformat()
    movies = await get_soon_async(today, pages=3)
    movies = [m for m in movies if m.get("release_date", "") > today and m.get("title") != m.get("original_title")]
    context.user_data["soon"] = movies
    await loading.delete()
    text = "🎟 Скоро в кино:\n\n" + format_movies(movies, 0, 10)
    await update.message.reply_text(text, parse_mode="Markdown",
                                    disable_web_page_preview=True,
                                    reply_markup=nav_keyboard(0, 3, "soon"))


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "home":
        text = "Привет! 🎬\n\n/popular — популярные фильмы недели\n/top — топ всех времён\n/soon — скоро в кино\n"
        await query.edit_message_text(text)
        return

    prefix, page = query.data.rsplit("_", 1)
    page = int(page)
    start = page * 10
    end = start + 10

    if prefix == "popular":
        movies = context.user_data.get("popular", await get_movies_async("trending/movie/week", pages=3))
        text = "🎬 Популярное за неделю:\n\n" + format_movies(movies, start, end)
        await query.edit_message_text(text, parse_mode="Markdown",
                                      disable_web_page_preview=True,
                                      reply_markup=nav_keyboard(page, 5, "popular"))

    elif prefix == "top":
        movies = context.user_data.get("top", await get_movies_async("movie/top_rated", pages=3))
        text = "🏆 Топ фильмов всех времён:\n\n" + format_movies(movies, start, end)
        await query.edit_message_text(text, parse_mode="Markdown",
                                      disable_web_page_preview=True,
                                      reply_markup=nav_keyboard(page, 5, "top"))

    elif prefix == "soon":
        movies = context.user_data.get("soon", [])
        text = "🎟 Скоро в кино:\n\n" + format_movies(movies, start, end)
        await query.edit_message_text(text, parse_mode="Markdown",
                                      disable_web_page_preview=True,
                                      reply_markup=nav_keyboard(page, 3, "soon"))


async def inline_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query
    if not query:
        return

    async with aiohttp.ClientSession() as session:
        url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&language=ru-RU&query={query}"
        data = await fetch(session, url)

    movies = data.get("results", [])[:6]
    movie_ids = [m.get("id") for m in movies]
    await get_imdb_ids_async(movie_ids)

    results = []
    for movie in movies:
        title = movie.get("title", "Без названия")
        year = movie.get("release_date", "????")[:4]
        rating = round(movie.get("vote_average", 0), 1)
        overview = movie.get("overview", "Описание отсутствует")[:200]
        movie_id = movie.get("id")
        poster = f"https://image.tmdb.org/t/p/w500{movie.get('poster_path')}" if movie.get("poster_path") else None
        imdb_id = imdb_cache.get(movie_id)

        genres = ", ".join([GENRES.get(g, "") for g in movie.get("genre_ids", [])[:1] if GENRES.get(g)])
        imdb_link = f"[IMDb](https://www.imdb.com/title/{imdb_id})" if imdb_id else f"[TMDB](https://www.themoviedb.org/movie/{movie_id})"

        text = (
            f"🎬 *{title}* ({year})\n"
            f"⭐ {rating} | 🎭 {genres}\n\n"
            f"{overview}...\n\n"
            f"🔗 {imdb_link}"
        )

        results.append(
            InlineQueryResultArticle(
                id=str(movie_id),
                title=f"{title} ({year})",
                description=f"⭐ {rating} | {overview[:60]}...",
                thumbnail_url=poster,
                input_message_content=InputTextMessageContent(
                    text, parse_mode="Markdown", disable_web_page_preview=True
                )
            )
        )
    await update.inline_query.answer(results, cache_time=30)


app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("popular", popular))
app.add_handler(CommandHandler("top", top))
app.add_handler(CommandHandler("soon", soon))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(InlineQueryHandler(inline_search))

print("Бот запущен...")
app.run_polling()
