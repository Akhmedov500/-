import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, InlineQueryHandler

TMDB_API_KEY = "5964ad98001f8a9d599fbd007eaea99b"
TELEGRAM_TOKEN = "8785802756:AAG1OXthghXaRkqLrkNqhDcVt8Q62oTbn_I"

#
def get_movies(endpoint, pages=1):
    movies = []
    for page in range(1, pages + 1):
        url = f"https://api.themoviedb.org/3/{endpoint}?api_key={TMDB_API_KEY}&language=ru-RU&page={page}"
        response = requests.get(url)
        movies += response.json()["results"]
    return movies


def format_movies(movies, start, end):
    text = ""
    for i, movie in enumerate(movies[start:end], start + 1):
        title = movie["title"]
        if len(title) > 16:
            title = title[:13] + "..."
        year = movie["release_date"][:4]
        rating = round(movie["vote_average"], 1)
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
    text = "Привет! 🎬\n\n/popular — популярные фильмы недели\n/top — топ всех времён\n"
    await update.message.reply_text(text)


async def popular(update: Update, context: ContextTypes.DEFAULT_TYPE):
    movies = get_movies("trending/movie/week", pages=3)
    context.user_data["popular"] = movies
    text = "🎬 Популярное за неделю:\n\n" + format_movies(movies, 0, 10)
    await update.message.reply_text(text, parse_mode="Markdown",
                                    disable_web_page_preview=True,
                                    reply_markup=nav_keyboard(0, 5, "popular"))


async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    movies = get_movies("movie/top_rated", pages=3)
    context.user_data["top"] = movies
    text = "🏆 Топ фильмов всех времён:\n\n" + format_movies(movies, 0, 10)
    await update.message.reply_text(text, parse_mode="Markdown",
                                    disable_web_page_preview=True,
                                    reply_markup=nav_keyboard(0, 5, "top"))


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "home":
        text = "Привет! 🎬\n\n/popular — популярные фильмы недели\n/top — топ всех времён\n"
        await query.edit_message_text(text)
        return

    prefix, page = query.data.rsplit("_", 1)
    page = int(page)
    start = page * 10
    end = start + 10

    if prefix == "popular":
        movies = context.user_data.get("popular", get_movies("trending/movie/week", pages=3))
        text = "🎬 Популярное за неделю:\n\n" + format_movies(movies, start, end)
        await query.edit_message_text(text, parse_mode="Markdown",
                                      disable_web_page_preview=True,
                                      reply_markup=nav_keyboard(page, 5, "popular"))

    elif prefix == "top":
        movies = context.user_data.get("top", get_movies("movie/top_rated", pages=3))
        text = "🏆 Топ фильмов всех времён:\n\n" + format_movies(movies, start, end)
        await query.edit_message_text(text, parse_mode="Markdown",
                                      disable_web_page_preview=True,
                                      reply_markup=nav_keyboard(page, 5, "top"))

async def inline_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query
    if not query:
        return

    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&language=ru-RU&query={query}"
    response = requests.get(url)
    movies = response.json().get("results", [])[:8]

    results = []
    for movie in movies:
        title = movie.get("title", "Без названия")
        year = movie.get("release_date", "????")[:4]
        rating = round(movie.get("vote_average", 0), 1)
        overview = movie.get("overview", "Описание отсутствует")[:200]
        movie_id = movie.get("id")
        poster = f"https://image.tmdb.org/t/p/w500{movie.get('poster_path')}" if movie.get("poster_path") else None

        text = (
            f"🎬 *{title}* ({year})\n"
            f"⭐ {rating}\n\n"
            f"📝 {overview}...\n\n"
            f"🔗 [TMDB](https://www.themoviedb.org/movie/{movie_id})"
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
app.add_handler(CallbackQueryHandler(button))
app.add_handler(InlineQueryHandler(inline_search))

from telegram import InlineQueryResultArticle, InputTextMessageContent

print("Бот запущен...")
app.run_polling()
