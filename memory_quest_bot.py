#!/usr/bin/env python3
"""Memory Quest Telegram Bot — Railway-ready version."""

import html
import os
import threading
import time
from datetime import datetime
from io import BytesIO

import telebot
from telebot import types
from telebot.apihelper import ApiTelegramException
from PIL import Image, ImageDraw, ImageFont, ImageOps

BOT_TOKEN = os.environ.get("BOT_TOKEN", "").strip()
EVENT_DATE = os.environ.get("EVENT_DATE", "").strip() or datetime.now().strftime("%d.%m.%Y")
ALLOWED_USERS = []  # [] = усі; або [123456789, 987654321]

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set. Add BOT_TOKEN in Railway Variables.")

bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None, threaded=True)
state_lock = threading.RLock()

ROSE = "🌸"
GOLD = "✦"
MAP = "📍"
CAMERA = "📸"
VIDEO = "🎬"

# ── LOCATIONS DATA ─────────────────────────────────
LOCATIONS = [
    {
        "id": 0,
        "name": "Маріїнський парк",
        "theme": "Кохання",
        "riddle": (
            "🌳 Тут серед каштанів, де місто відкривається до Дніпра,\n"
            "є місце назване на честь імператриці.\n\n"
            "Закохані зупиняються тут щоб подивитися\n"
            "на місто з висоти правого берега."
        ),
        "answers": ["маріїнський парк", "маріїнський", "mariinsky"],
        "hints": [
            "Парк поруч з урядовим кварталом, на схилах правого берега Дніпра.",
            "Названий на честь дружини Олександра II. Тут є палац.",
            "Адреса: вул. Грушевського 5а — за Верховною Радою.",
        ],
        "wish": "«Кохання — це не тільки дивитися одне на одного,\nа ще дивитися разом в одному напрямку.»",
        "task": (
            "Подивіться одне одному в очі\n"
            "і не відводьте погляд протягом однієї хвилини.\n\n"
            "Без слів. 💕"
        ),
        "photo_prompt": "Зробіть спільне фото на оглядовому майданчику над Дніпром 📸",
        "reveal_word": "КОХАННЯ",
        "reveal_wish": "Кохання — це обирати одне одного знову і знову, кожного ранку.",
        "maps_url": "https://maps.google.com/?q=50.4411,30.5369",
    },
    {
        "id": 1,
        "name": "Пішохідний міст",
        "theme": "Довіра",
        "riddle": (
            "🌉 Він з'єднує береги без машин.\n"
            "Тут залишають замки з іменами.\n\n"
            "Звідси — найкращий вид на Дніпро і Труханів острів."
        ),
        "answers": ["пішохідний міст", "міст закоханих", "міст", "pedestrian bridge"],
        "hints": [
            "Цей міст ще називають Мостом закоханих.",
            "Веде на Труханів острів. Поруч — Наводницький парк.",
            "Поблизу Набережно-Хрещатицької вулиці.",
        ],
        "wish": "«Довіра будується роками,\nруйнується хвилинами, але варта в!»",
        "task": (
            "Станьте поруч у безпечному місці.\n"
            "Один заплющує очі на 30 секунд, а інший тримає за руку\n"
            "і описує, що бачить навколо. Потім поміняйтеся. 🤝"
        ),
        "photo_prompt": "Зробіть фото на фоні Дніпра 📸",
        "reveal_word": "ДОВІРА",
        "reveal_wish": "Довіра — це падати назад із заплющеними очима і знати, що тебе впіймають.",
        "maps_url": "https://maps.google.com/?q=50.4467,30.5432",
    },
    {
        "id": 2,
        "name": "Андріївський узвіз",
        "theme": "Повага",
        "riddle": (
            "🎨 Стара мощена вулиця з художниками та антикварями.\n"
            "Вона спускається від блакитної барокової церкви\n"
            "вниз до Подолу.\n\n"
            "Названа на честь апостола."
        ),
        "answers": ["андріївський узвіз", "андріївський", "andriyivsky"],
        "hints": [
            "З'єднує Верхнє місто з Подолом.",
            "Блакитна барокова церква — її символ.",
            "Між Михайлівською площею та Контрактовою.",
        ],
        "wish": "«Поважати одне одного —\nце бачити в партнері найкращу версію себе!»",
        "task": (
            "Кожен пише одну річ,\n"
            "яку хоче подарувати своїй родині за наступні 10 років.\n\n"
            "Обміняйтесь і прочитайте вголос. 📝"
        ),
        "photo_prompt": "Зробіть фото на фоні старого Києва 📸",
        "reveal_word": "ПОВАГА",
        "reveal_wish": "Повага — це бачити в партнері найкращу версію себе.",
        "maps_url": "https://maps.google.com/?q=50.4592,30.5157",
    },
    {
        "id": 3,
        "name": "Пейзажна алея",
        "theme": "Радість",
        "riddle": (
            "🌈 Тут живе мозаїчний кіт,\n"
            "якого всі хочуть сфотографувати.\n\n"
            "Арт-парк просто неба з яскравими скульптурами\n"
            "і видом на старий Київ."
        ),
        "answers": ["пейзажна алея", "пейзажна", "landscape alley"],
        "hints": [
            "Над Андріївським узвозом, на схилах Подолу.",
            "Є скульптура мозаїчного кота.",
            "Вул. Воздвиженська, поруч із Замковою горою.",
        ],
        "wish": "«Радість множиться, коли нею ділишся —\nа двоє сміються вдвічі голосніше.»",
        "task": (
            "Зробіть найвеселіше спільне фото дня.\n\n"
            "Жодних серйозних облич! 😄"
        ),
        "photo_prompt": "Найвеселіше фото дня — біля мозаїчного кота 📸",
        "reveal_word": "РАДІСТЬ",
        "reveal_wish": "Радість множиться, коли нею ділишся — а двоє сміються вдвічі голосніше.",
        "maps_url": "https://maps.google.com/?q=50.4604,30.5107",
    },
    {
        "id": 4,
        "name": "Поштова площа",
        "theme": "Вірність",
        "is_video": True,
        "riddle": (
            "📮 Звідси відпливали кораблі і приходили листи.\n"
            "Фунікулер піднімається від цієї площі до Михайлівської.\n\n"
            "Одна з найстаріших площ міста,\n"
            "де Поділ зустрічається з Дніпром."
        ),
        "answers": ["поштова площа", "поштова", "postal square"],
        "hints": [
            "Звідси курсує київський фунікулер.",
            "Поруч з Річковим вокзалом.",
            "Між Подолом і берегом Дніпра.",
        ],
        "wish": "«Вірність — це обирати одне одного\nзнову і знову, кожного ранку.»",
        "task": (
            "🎬 КАПСУЛА ЧАСУ\n\n"
            "Запишіть коротке відео — послання собі у 2046 рік.\n\n"
            "«Привіт, Аня та Нікіта через 20 років...\n"
            "це ваші перші дні як подружня пара.»\n\n"
            "Що ви хочете сказати собі у майбутньому?"
        ),
        "photo_prompt": "Надішліть відео-послання у майбутнє 🎬",
        "reveal_word": "ВІРНІСТЬ",
        "reveal_wish": "Вірність — це не відсутність спокус, а присутність вибору.",
        "maps_url": "https://maps.google.com/?q=50.4628,30.5226",
    },
    {
        "id": 5,
        "name": "Володимирська гірка",
        "theme": "Шлях",
        "riddle": (
            "⛪ Тут стоїть князь із хрестом,\n"
            "що освятив цю землю.\n\n"
            "Один із найвідоміших силуетів Києва —\n"
            "на схилі над Дніпром.\n\n"
            "Сюди приходять урочисто."
        ),
        "answers": ["володимирська гірка", "володимирська", "volodymyrska"],
        "hints": [
            "Пам'ятник святому Володимиру з хрестом у руці.",
            "Поруч парк Хрещатий яр.",
            "Вул. Грушевського 3 — навпроти Маріїнського парку.",
        ],
        "wish": "«Кожен спільний шлях складається з кроків\nяк ви робите разом —\nі цей погляд на Дніпро ви будете пам'ятати.»",
        "task": (
            "Знайдіть пам'ятник.\n"
            "Подивіться на Дніпро з висоти.\n\n"
            "Уявіть все що ви подолали разом —\n"
            "і все що ще попереду. 🌅"
        ),
        "photo_prompt": "Фото з видом на Дніпро з Володимирської гірки 📸",
        "reveal_word": "ШЛЯХ",
        "reveal_wish": "Кожен спільний шлях складається з кроків які ви робите разом.",
        "maps_url": "https://maps.google.com/?q=50.4519,30.5242",
    },
    
]

# ── STATE ──────────────────────────────────────────
# Стан живе в пам'яті процесу. Не робіть redeploy під час проходження квесту.
sessions = {}


def new_state():
    return {
        "screen": "cover",
        "current_loc": 0,
        "completed": [],
        "hints_used": [0] * len(LOCATIONS),
        "photos": [],
        "started_at": time.time(),
        "signatures": [],
    }


def get_state(user_id):
    with state_lock:
        if user_id not in sessions:
            sessions[user_id] = new_state()
        return sessions[user_id]


def save_state(user_id, state):
    with state_lock:
        sessions[user_id] = state


def reset_state(user_id):
    with state_lock:
        sessions[user_id] = new_state()
        return sessions[user_id]


def user_allowed(user_id):
    return not ALLOWED_USERS or user_id in ALLOWED_USERS


def deny_if_needed(message):
    if user_allowed(message.from_user.id):
        return False
    bot.send_message(message.chat.id, "Цей квест доступний лише запрошеним учасникам 🌸")
    return True


# ── TELEGRAM HELPERS ───────────────────────────────
def esc(value):
    return html.escape(str(value), quote=False)


def send_html(chat_id, text, **kwargs):
    return bot.send_message(chat_id, text, parse_mode="HTML", **kwargs)


def kb(*buttons, row_width=1):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=row_width)
    for button in buttons:
        markup.add(types.KeyboardButton(button))
    return markup


def kb_remove():
    return types.ReplyKeyboardRemove()


def kb_url(text, url):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text, url=url))
    return markup


# ── COLLAGE ────────────────────────────────────────
def _font(size, bold=False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size=size)
            except OSError:
                pass
    return ImageFont.load_default()


def _photo_items(state):
    return [
        item for item in state.get("photos", [])
        if isinstance(item, dict) and item.get("type") == "photo" and item.get("file_id")
    ]


def create_memory_collage(user_id):
    state = get_state(user_id)
    items = _photo_items(state)
    if not items:
        return None

    images = []
    for item in items[:6]:
        try:
            tg_file = bot.get_file(item["file_id"])
            raw = bot.download_file(tg_file.file_path)
            with Image.open(BytesIO(raw)) as opened:
                image = opened.convert("RGB")
            images.append((image, item.get("location_name", "")))
        except Exception as exc:
            print(f"[COLLAGE] Не вдалося завантажити фото: {exc}")

    if not images:
        return None

    canvas_w = 1600
    margin = 70
    gap = 28
    header_h = 250
    footer_h = 150
    cell_w = (canvas_w - margin * 2 - gap) // 2
    cell_h = 620
    rows = (len(images) + 1) // 2
    canvas_h = header_h + rows * cell_h + max(0, rows - 1) * gap + footer_h + margin

    canvas = Image.new("RGB", (canvas_w, canvas_h), (250, 246, 242))
    draw = ImageDraw.Draw(canvas)
    title_font = _font(72, bold=True)
    subtitle_font = _font(34)
    label_font = _font(26, bold=True)
    footer_font = _font(30)

    def centered_text(text, y, font, fill):
        box = draw.textbbox((0, 0), text, font=font)
        width = box[2] - box[0]
        draw.text(((canvas_w - width) / 2, y), text, fill=fill, font=font)

    centered_text("Аня & Нікіта", 55, title_font, (91, 56, 62))
    centered_text(f"Memory Quest · {EVENT_DATE} · Київ", 150, subtitle_font, (126, 100, 103))
    draw.line((margin, 220, canvas_w - margin, 220), fill=(210, 177, 174), width=3)

    for i, (image, location_name) in enumerate(images):
        row, col = divmod(i, 2)
        x = margin + col * (cell_w + gap)
        y = header_h + row * (cell_h + gap)
        photo_h = cell_h - 62

        fitted = ImageOps.fit(
            image,
            (cell_w, photo_h),
            method=Image.Resampling.LANCZOS,
            centering=(0.5, 0.5),
        )
        canvas.paste(fitted, (x, y))
        draw.rectangle((x, y, x + cell_w - 1, y + photo_h - 1), outline=(255, 255, 255), width=8)

        label = f"{i + 1}. {location_name or f'Спогад {i + 1}'}"
        max_width = cell_w - 12
        while len(label) > 5 and draw.textbbox((0, 0), label + "…", font=label_font)[2] > max_width:
            label = label[:-1]
        draw.text((x + 6, y + photo_h + 16), label, fill=(86, 72, 73), font=label_font)

    centered_text(
        "Один день. Один маршрут. Спогад на все життя.",
        canvas_h - footer_h + 25,
        footer_font,
        (126, 100, 103),
    )

    output = BytesIO()
    output.name = "Anya_Nikita_Memory_Quest.jpg"
    canvas.save(output, format="JPEG", quality=90, optimize=True)
    output.seek(0)
    return output


def send_memory_collage(chat_id, user_id):
    try:
        collage = create_memory_collage(user_id)
        if collage is None:
            bot.send_message(chat_id, "📸 Для колажу поки немає фотографій.")
            return False
        bot.send_photo(
            chat_id,
            collage,
            caption=(
                "🌸 <b>Ваш Memory Quest — в одному кадрі</b>\n\n"
                "Збережіть цей колаж. Через роки він поверне вас у цей день ✨"
            ),
            parse_mode="HTML",
        )
        return True
    except Exception as exc:
        print(f"[COLLAGE] Помилка створення: {exc}")
        bot.send_message(chat_id, "📸 Фото збережені в чаті, але колаж зараз не вдалося зібрати.")
        return False


# ── SCREENS ────────────────────────────────────────
def send_cover(chat_id, user_id):
    state = get_state(user_id)
    state["screen"] = "cover"
    save_state(user_id, state)
    send_html(
        chat_id,
        f"{ROSE}{ROSE}{ROSE}\n\n"
        "<b>Аня &amp; Нікіта</b>\n"
        f"{esc(EVENT_DATE)} · Київ\n\n"
        "━━━━━━━━━━━━━━━\n\n"
        "Любі наші Аня та Нікіта!\n\n"
        "Сьогодні ми хочемо подарувати вам не річ і не конверт.\n\n"
        "Ми хочемо подарувати вам <b>пригоду.</b>\n\n"
        "Можливо, через роки ви забудете суму нашого подарунка.\n"
        "Але ми дуже хочемо, щоб ви пам'ятали цей день.\n\n"
        "━━━━━━━━━━━━━━━\n\n"
        f"<i>З любов'ю, Володя та Ірина</i> {GOLD}",
        reply_markup=kb(f"{ROSE} Почати пригоду"),
    )


def send_hub(chat_id, user_id):
    state = get_state(user_id)
    state["screen"] = "hub"
    save_state(user_id, state)

    done = len(state["completed"])
    total = len(LOCATIONS)
    progress = f"{'█' * done}{'░' * (total - done)} {done}/{total}"

    lines = []
    for i, loc in enumerate(LOCATIONS):
        if i in state["completed"]:
            lines.append(f"✅ {esc(loc['name'])}")
        elif i == state["current_loc"]:
            label = f"Завдання {i + 1}"
            lines.append(f"▶️ <b>{label}</b>")
        else:
            lines.append(f"🔒 Завдання {i + 1}")

    text = f"🗺 <b>Маршрут</b>\n<code>{esc(progress)}</code>\n\n" + "\n".join(lines)
    button = f"📍 Розпочати завдання {state['current_loc'] + 1}"
    send_html(chat_id, text, reply_markup=kb(button, f"{GOLD} Допомога"))


def send_riddle(chat_id, user_id):
    state = get_state(user_id)
    loc = LOCATIONS[state["current_loc"]]
    state["screen"] = "riddle"
    save_state(user_id, state)
    i = state["current_loc"]

    send_html(
        chat_id,
        f"{MAP} <b>Завдання {i + 1} з {len(LOCATIONS)}</b>\n"
        f"Тема: <i>{esc(loc['theme'])}</i>\n\n"
        "━━━━━━━━━━━━━━━\n\n"
        "🔍 <b>ЗАГАДКА</b>\n\n"
        f"{esc(loc['riddle'])}",
        reply_markup=kb("💡 Підказка", "← Карта квесту"),
    )
    bot.send_message(chat_id, "Напишіть назву місця 👇")


def send_hint(chat_id, user_id):
    state = get_state(user_id)
    loc = LOCATIONS[state["current_loc"]]
    i = state["current_loc"]
    used = state["hints_used"][i]

    if used >= len(loc["hints"]):
        bot.send_message(chat_id, "Всі підказки використано 🙈 Ви впораєтесь!")
        return

    hint_text = loc["hints"][used]
    state["hints_used"][i] += 1
    save_state(user_id, state)
    send_html(chat_id, f"💡 <b>Підказка {used + 1}:</b>\n\n<i>{esc(hint_text)}</i>")


def normalize_answer(text):
    return " ".join(text.strip().lower().replace("’", "'").split())


def check_answer(chat_id, user_id, text):
    state = get_state(user_id)
    loc = LOCATIONS[state["current_loc"]]
    answer = normalize_answer(text)
    accepted = {normalize_answer(a) for a in loc["answers"]}

    if answer in accepted:
        send_html(chat_id, f"✅ <b>Правильно!</b>\n\n<i>{esc(loc['name'])}</i>\n\nПрокладаємо маршрут…")
        bot.send_message(
            chat_id,
            "📍 Відкрийте Google Maps:",
            reply_markup=kb_url(f"📍 Маршрут до {loc['name']}", loc["maps_url"]),
        )
        state["screen"] = "navigate"
        save_state(user_id, state)
        bot.send_message(chat_id, "Коли будете на місці — натисніть кнопку 👇", reply_markup=kb("📍 Я на місці!"))
    else:
        bot.send_message(
            chat_id,
            "Спробуйте ще… 🤔 Підказка допоможе, якщо потрібно.",
            reply_markup=kb("💡 Підказка", "← Карта квесту"),
        )


def send_task(chat_id, user_id):
    state = get_state(user_id)
    loc = LOCATIONS[state["current_loc"]]
    state["screen"] = "task"
    save_state(user_id, state)

    send_html(
        chat_id,
        f"🌸 <b>{esc(loc['name'])}</b>\n"
        f"<i>{esc(loc['theme'])}</i>\n\n"
        "━━━━━━━━━━━━━━━\n\n"
        f"{esc(loc['wish'])}",
    )
    time.sleep(0.4)
    send_html(chat_id, f"🎯 <b>Ваше завдання:</b>\n\n{esc(loc['task'])}")
    time.sleep(0.4)

    if loc.get("is_video"):
        bot.send_message(chat_id, f"{VIDEO} {loc['photo_prompt']}\n\nНадішліть відео у цей чат 👇", reply_markup=kb("⏭ Пропустити відео"))
    else:
        bot.send_message(chat_id, f"{CAMERA} {loc['photo_prompt']}\n\nНадішліть фото у цей чат 👇", reply_markup=kb("⏭ Пропустити фото"))


def send_reveal(chat_id, user_id):
    state = get_state(user_id)
    loc = LOCATIONS[state["current_loc"]]
    state["screen"] = "reveal"
    save_state(user_id, state)

    send_html(chat_id, f"✦ ✦ ✦\n\n<b>{esc(loc['reveal_word'])}</b>\n\n✦ ✦ ✦")
    time.sleep(0.4)
    send_html(chat_id, f"<i>{esc(loc['reveal_wish'])}</i>")
    time.sleep(0.4)

    next_idx = state["current_loc"] + 1

    # Після 6-ї, останньої локації, одразу завершуємо квест.
    if next_idx >= len(LOCATIONS):
        complete_location(user_id)
        time.sleep(0.4)
        send_final(chat_id, user_id)
        return

    bot.send_message(
        chat_id,
        "Продовжуємо? 👇",
        reply_markup=kb(f"→ Наступне завдання: {next_idx + 1}/{len(LOCATIONS)}", "← Карта квесту"),
    )


def complete_location(user_id):
    state = get_state(user_id)
    i = state["current_loc"]
    if i not in state["completed"]:
        state["completed"].append(i)
    if i + 1 < len(LOCATIONS):
        state["current_loc"] = i + 1
    save_state(user_id, state)



def send_final(chat_id, user_id):
    state = get_state(user_id)
    state["screen"] = "final"
    save_state(user_id, state)

    elapsed = max(0, int((time.time() - state["started_at"]) / 60))
    photos = len(_photo_items(state))

    bot.send_message(chat_id, "🎊🌸🎊🌸🎊🌸🎊")
    time.sleep(0.4)
    send_html(
        chat_id,
        "💍 <b>Вітаємо, Аня &amp; Нікіта!</b>\n\n"
        "━━━━━━━━━━━━━━━\n\n"
        f"🗺 Локацій пройдено: <b>{len(state['completed'])}</b>\n"
        f"📸 Фото збережено: <b>{photos}</b>\n"
        f"⏱ Час пригоди: <b>{elapsed} хв</b>\n"
        "💍 Обітниці: ✓\n\n"
        "━━━━━━━━━━━━━━━",
    )
    time.sleep(0.5)
    
    send_html(
        chat_id,
        "✦ <b>Фінальний лист</b>\n\n"
        "Сьогодні ви шукали локації. Відгадували загадки. Трималися за руки. "
        "Давали обіцянки там, де все починалось.\n\n"
        "І створили те, що не можна купити — <b>спогад.</b>\n\n"
        "Нехай у вашій родині завжди будуть: Кохання. Довіра. Повага. Радість. Вірність. Початок.\n\n"
        "<i>З любов'ю, Володя та Ірина ✦</i>",
    )

    if photos > 0:
        time.sleep(0.7)
        bot.send_message(chat_id, "📸 А тепер — ваш день в одному кадрі…")
        time.sleep(0.4)
        send_memory_collage(chat_id, user_id)

    time.sleep(0.7)
    bot.send_message(chat_id, "🌟 Залишився один сюрприз…", reply_markup=kb("✨ Відкрити сюрприз"))


def send_proposal(chat_id, user_id):
    state = get_state(user_id)
    state["screen"] = "proposal"
    save_state(user_id, state)

    send_html(
        chat_id,
        "✦ <b>Другий сюрприз</b>\n\n"
        "━━━━━━━━━━━━━━━\n\n"
        "Ви щойно закінчили квест там, де у вас все починалось.\n\n"
        "Нехай пройдуть роки. Нехай буде багато інших місць і подорожей. ",
    )
    time.sleep(0.6)
    send_html(chat_id, "💡 <b>Поки ви проходили цей маршрут —</b>\nви тестували продукт, якого ще не існує у світі.")
    time.sleep(0.6)
    send_html(
        chat_id,
        "🤝 <b>Пропозиція</b>\n\n"
        "Поговорити про те, щоб створити Memory Quest разом.\n\n"
        "<b>Аня</b> — сильний Product Manager.\n"
        "<b>Нікіта</b> — сильний розробник.\n"
        "<b>Ми</b> — ідея і перший квест.\n\n"
        "<b>Просто — початок чогось спільного.</b>",
        reply_markup=kb("✦ Підписати меморандум", "💍 Завершити пригоду"),
    )


def send_mou(chat_id, user_id):
    state = get_state(user_id)
    state["screen"] = "mou"
    save_state(user_id, state)
    send_html(
        chat_id,
        "📜 <b>Меморандум про наміри</b>\n\n"
        "Цей документ не створює зобов'язань. Він лише підтверджує бажання створити щось красиве разом.\n\n"
        "━━━━━━━━━━━━━━━\n\n"
        "✦ Володя\n✦ Ірина\n✦ Аня ← ваш підпис\n✦ Нікіта ← ваш підпис\n\n"
        "━━━━━━━━━━━━━━━\n\n"
        "<i>Натисніть, щоб підписати</i>",
        reply_markup=kb("✦ Аня підписує", "✦ Нікіта підписує", "💍 Завершити пригоду"),
    )


def sign_mou(chat_id, user_id, name):
    state = get_state(user_id)
    if name not in state["signatures"]:
        state["signatures"].append(name)
        save_state(user_id, state)
        send_html(chat_id, f"✦ <b>{esc(name)}: підпис додано</b> ✓\n\n<i>Підпис збережено в цій сесії.</i>")
    else:
        bot.send_message(chat_id, f"✦ Підпис {name} вже додано ✓")


def send_end(chat_id, user_id):
    state = get_state(user_id)
    state["screen"] = "end"
    save_state(user_id, state)
    send_html(
        chat_id,
        "🌸✦🌸✦🌸\n\n"
        "<b>Memory Quest завершено.</b>\n\n"
        f"<i>Аня &amp; Нікіта · {esc(EVENT_DATE)}</i>\n\n"
        "Дякуємо, що довіряєте нам найважливіший день.\n\n"
        "До зустрічі ✦\n\n"
        "🌸✦🌸✦🌸",
        reply_markup=kb_remove(),
    )


# ── HANDLERS ───────────────────────────────────────
@bot.message_handler(commands=["start"])
def handle_start(message):
    if deny_if_needed(message):
        return
    uid = message.from_user.id
    reset_state(uid)
    send_cover(message.chat.id, uid)


@bot.message_handler(commands=["map"])
def handle_map(message):
    if deny_if_needed(message):
        return
    send_hub(message.chat.id, message.from_user.id)


@bot.message_handler(content_types=["photo"])
def handle_photo(message):
    if deny_if_needed(message):
        return
    uid = message.from_user.id
    cid = message.chat.id
    state = get_state(uid)

    if state["screen"] != "task":
        bot.send_message(cid, "Фото отримано 📸 Під час завдання я автоматично додам його до колажу.")
        return

    loc = LOCATIONS[state["current_loc"]]
    if loc.get("is_video"):
        bot.send_message(cid, "На цій локації потрібне саме відео 🎬")
        return

    state["photos"].append({
        "type": "photo",
        "file_id": message.photo[-1].file_id,
        "location_id": loc["id"],
        "location_name": loc["name"],
    })
    save_state(uid, state)
    bot.send_message(cid, f"{CAMERA} Фото збережено в книзі спогадів ✓")
    time.sleep(0.3)
    send_reveal(cid, uid)


@bot.message_handler(content_types=["video"])
def handle_video(message):
    if deny_if_needed(message):
        return
    uid = message.from_user.id
    cid = message.chat.id
    state = get_state(uid)

    if state["screen"] != "task":
        bot.send_message(cid, "Відео отримано 🎬")
        return

    loc = LOCATIONS[state["current_loc"]]
    if not loc.get("is_video"):
        bot.send_message(cid, "На цій локації потрібне фото 📸")
        return

    state["photos"].append({
        "type": "video",
        "file_id": message.video.file_id,
        "location_id": loc["id"],
        "location_name": loc["name"],
    })
    save_state(uid, state)
    bot.send_message(cid, f"{VIDEO} Відео-капсула збережена в цьому чаті ✓")
    time.sleep(0.3)
    send_reveal(cid, uid)


@bot.message_handler(content_types=["text"])
def handle_text(message):
    if deny_if_needed(message):
        return

    uid = message.from_user.id
    cid = message.chat.id
    text = (message.text or "").strip()
    state = get_state(uid)
    screen = state["screen"]
    loc = LOCATIONS[state["current_loc"]]

    if ROSE in text and "Почати" in text:
        send_hub(cid, uid)
        return

    if "Карта квесту" in text or text == "← Карта":
        send_hub(cid, uid)
        return

    if "Допомога" in text:
        send_html(
            cid,
            "ℹ️ <b>Допомога</b>\n\n"
            "• Натисніть «Розпочати завдання»\n"
            "• Відгадайте загадку та напишіть відповідь\n"
            "• Підказки доступні кнопкою 💡\n"
            "• На місці натисніть «Я на місці»\n"
            "• Надішліть фото або відео, коли бот попросить\n"

            "/start — почати спочатку\n/map — карта квесту",
        )
        return

    if "Розпочати завдання" in text:
        send_riddle(cid, uid)
        return

    if screen == "riddle":
        if "Підказка" in text:
            send_hint(cid, uid)
            return
        check_answer(cid, uid, text)
        return

    if screen == "navigate":
        if "на місці" in text.lower():
            send_html(cid, f"✓ Прибуття підтверджено! Вітаємо на <b>{esc(loc['name'])}</b>!")
            time.sleep(0.3)
            send_task(cid, uid)
        else:
            bot.send_message(cid, "Коли прибудете — натисніть «📍 Я на місці!»")
        return

    if screen == "task":
        if "Пропустити" in text:
            state["photos"].append({
                "type": "skip",
                "file_id": None,
                "location_id": loc["id"],
                "location_name": loc["name"],
            })
            save_state(uid, state)
            send_reveal(cid, uid)
        else:
            expected = "відео" if loc.get("is_video") else "фото"
            bot.send_message(cid, f"Надішліть {expected} або натисніть кнопку «Пропустити».")
        return

    if screen == "reveal":
        if "Наступне завдання" in text:
            complete_location(uid)
            send_riddle(cid, uid)
            return

    if screen == "final" and "Відкрити сюрприз" in text:
        send_proposal(cid, uid)
        return

    if screen in ("proposal", "mou"):
        if "Підписати меморандум" in text:
            send_mou(cid, uid)
            return
        if "Аня підписує" in text:
            sign_mou(cid, uid, "Аня")
            return
        if "Нікіта підписує" in text:
            sign_mou(cid, uid, "Нікіта")
            return
        if "Завершити" in text:
            send_end(cid, uid)
            return

    if screen == "end":
        bot.send_message(cid, "Memory Quest уже завершено 🌸 Щоб почати спочатку: /start")
        return

    bot.send_message(cid, "Не зовсім зрозумів команду. Натисніть кнопку на екрані або /map.")


# ── RUN ────────────────────────────────────────────
def run_bot():
    print("Memory Quest Bot запускається 🌸")
    print(f"Дата квесту: {EVENT_DATE}")

    try:
        bot.remove_webhook()
    except Exception as exc:
        print(f"[STARTUP] Не вдалося видалити webhook: {exc}")

    while True:
        try:
            print("Memory Quest Bot online ✓")
            bot.infinity_polling(
                skip_pending=True,
                timeout=30,
                long_polling_timeout=30,
                allowed_updates=["message"],
            )
        except ApiTelegramException as exc:
            print(f"[TELEGRAM] {exc}")
            if getattr(exc, "error_code", None) == 409:
                print("[TELEGRAM] 409 conflict: запущено інший процес із цим Bot Token. Залиште лише один Railway instance.")
            time.sleep(5)
        except KeyboardInterrupt:
            print("Bot stopped")
            break
        except Exception as exc:
            print(f"[FATAL LOOP] {type(exc).__name__}: {exc}")
            time.sleep(5)


if __name__ == "__main__":
    run_bot()
