#!/usr/bin/env python3
"""
Memory Quest Telegram Bot
Аня & Нікіта · {EVENT_DATE} · Київ

Встановлення:
  pip install pyTelegramBotAPI Pillow

Запуск:
  BOT_TOKEN=your_token python memory_quest_bot.py
"""

import os
import telebot
from telebot import types
import json
import time
from datetime import datetime
from io import BytesIO
from PIL import Image, ImageOps, ImageDraw, ImageFont

# ── CONFIG ─────────────────────────────────────────
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
EVENT_DATE = os.environ.get("EVENT_DATE") or datetime.now().strftime("%d.%m.%Y")
# Замінити на реальний Telegram ID Ані або Нікіти
ALLOWED_USERS = []  # [] = всі можуть, або [123456789, 987654321]

bot = telebot.TeleBot(BOT_TOKEN)

# ── EMOJIS & STYLE ─────────────────────────────────
ROSE   = "🌸"
GOLD   = "✦"
HEART  = "💍"
MAP    = "📍"
CAMERA = "📸"
KEY    = "🔑"
GIFT   = "🎁"
SPARK  = "✨"
VIDEO  = "🎬"

# ── LOCATIONS DATA ─────────────────────────────────
LOCATIONS = [
    {
        "id": 0,
        "name": "Маріїнський парк",
        "theme": "Кохання",
        "pin": 4,
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
        "pin": 2,
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
            "Пройдіть почерзі 20 кроків з закритими очима.\n\n"
            "Один веде — інший довіряє. 🤝"
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
        "pin": 6,
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
        "pin": 4,
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
        "pin": None,
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
            "дні ваш перший день як подружня пара.»\n\n"
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
        "pin": None,
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
    {
        "id": 6,
        "name": "Зоопарк 4 Сезони",
        "theme": "Початок",
        "pin": None,
        "is_final": True,
        "riddle": (
            "🦒 Ця пригода пройшла через кохання, довіру,\n"
            "повагу, радість, вірність і шлях.\n\n"
            "Тепер вона повертається туди звідки все починалось —\n"
            "щоб замкнути коло.\n\n"
            "Від початку до кінця.\n"
            "Від кінця до початку."
        ),
        "answers": ["зоопарк 4 сезони", "зоопарк", "4 сезони", "zoo"],
        "hints": [
            "Це місце де ви вперше зустрілись.",
            "Зоопарк у Києві — чотири пори року в назві.",
            "Зоопарк 4 Сезони, Київ.",
        ],
        "wish": "«Від початку до кінця.\nВід кінця — до нового початку.\nОсь що таке ваша історія.»",
        "task": (
            "Станьте там де у вас все починалось.\n"
            "Візьміться за руки.\n"
            "Подивіться одне одному в очі.\n\n"
            "І скажіть — кожен своє — одне речення.\n"
            "Те що йде від серця.\n\n"
            "Обіцянку що це ніколи не закінчиться. 💍"
        ),
        "photo_prompt": "Фото там де у вас все починалось 📸",
        "reveal_word": "ПОЧАТОК",
        "reveal_wish": "Від початку до кінця. Від кінця — до нового початку. Ось що таке ваша історія.",
        "maps_url": "https://maps.google.com/?q=50.4750,30.4489",
    },
]

CORRECT_PIN = [4, 2, 6, 4]

# ── STATE (in-memory) ──────────────────────────────
# Для production використовувати Redis або SQLite
sessions = {}

def get_state(user_id):
    if user_id not in sessions:
        sessions[user_id] = {
            "screen": "cover",
            "current_loc": 0,
            "completed": [],
            "pins": [],
            "hints_used": [0] * len(LOCATIONS),
            "photos": [],
            "started_at": time.time(),
        }
    return sessions[user_id]

def save_state(user_id, state):
    sessions[user_id] = state


def _font(size, bold=False):
    """Повертає шрифт з підтримкою кирилиці, якщо він є у контейнері."""
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


def _photo_items(state):
    """Витягує тільки фото. Відео та пропуски у колаж не потрапляють."""
    result = []
    for item in state.get("photos", []):
        if not item:
            continue
        # Новий формат
        if isinstance(item, dict):
            if item.get("type") == "photo" and item.get("file_id"):
                result.append(item)
        # Сумісність зі старими сесіями, де зберігався лише file_id
        elif isinstance(item, str):
            result.append({"type": "photo", "file_id": item, "location_name": ""})
    return result


def create_memory_collage(user_id):
    """
    Завантажує надіслані в квесті фото з Telegram і формує JPEG-колаж.
    Повертає BytesIO або None, якщо фото немає/колаж не вдалося створити.
    """
    state = get_state(user_id)
    items = _photo_items(state)
    if not items:
        return None

    images = []
    for item in items[:6]:  # у поточному маршруті максимум 6 фото-точок
        try:
            tg_file = bot.get_file(item["file_id"])
            raw = bot.download_file(tg_file.file_path)
            image = Image.open(BytesIO(raw)).convert("RGB")
            images.append((image, item.get("location_name", "")))
        except Exception as exc:
            print(f"Не вдалося завантажити фото для колажу: {exc}")

    if not images:
        return None

    # Вертикальний пам'ятний постер: 2 колонки × до 3 рядків.
    canvas_w = 1600
    margin = 70
    gap = 28
    header_h = 250
    footer_h = 150
    cell_w = (canvas_w - margin * 2 - gap) // 2
    cell_h = 620
    rows = (len(images) + 1) // 2
    canvas_h = header_h + rows * cell_h + max(0, rows - 1) * gap + footer_h + margin

    bg = (250, 246, 242)
    canvas = Image.new("RGB", (canvas_w, canvas_h), bg)
    draw = ImageDraw.Draw(canvas)

    title_font = _font(72, bold=True)
    subtitle_font = _font(34)
    label_font = _font(26, bold=True)
    footer_font = _font(30)

    # Заголовок
    title = "Аня & Нікіта"
    subtitle = f"Memory Quest · {EVENT_DATE} · Київ"
    title_box = draw.textbbox((0, 0), title, font=title_font)
    subtitle_box = draw.textbbox((0, 0), subtitle, font=subtitle_font)
    draw.text(((canvas_w - (title_box[2]-title_box[0]))/2, 55), title, fill=(91, 56, 62), font=title_font)
    draw.text(((canvas_w - (subtitle_box[2]-subtitle_box[0]))/2, 150), subtitle, fill=(126, 100, 103), font=subtitle_font)

    # Тонка декоративна лінія
    draw.line((margin, 220, canvas_w-margin, 220), fill=(210, 177, 174), width=3)

    for i, (image, location_name) in enumerate(images):
        row = i // 2
        col = i % 2
        x = margin + col * (cell_w + gap)
        y = header_h + row * (cell_h + gap)

        # Поле під підпис локації
        photo_h = cell_h - 62
        fitted = ImageOps.fit(image, (cell_w, photo_h), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))

        # Легка біла рамка
        framed = ImageOps.expand(fitted, border=8, fill="white")
        framed = framed.resize((cell_w, photo_h))
        canvas.paste(framed, (x, y))

        label = location_name or f"Спогад {i+1}"
        # Номер + підпис, щоб колаж читався як маршрут.
        label = f"{i+1}. {label}"
        bbox = draw.textbbox((0, 0), label, font=label_font)
        max_w = cell_w - 12
        if bbox[2] - bbox[0] > max_w:
            # Проста обрізка довгого підпису.
            while len(label) > 4 and draw.textbbox((0,0), label + "…", font=label_font)[2] > max_w:
                label = label[:-1]
            label += "…"
        draw.text((x + 6, y + photo_h + 16), label, fill=(86, 72, 73), font=label_font)

    footer_y = canvas_h - footer_h + 25
    footer = "Один день. Один маршрут. Спогад на все життя."
    fb = draw.textbbox((0,0), footer, font=footer_font)
    draw.text(((canvas_w-(fb[2]-fb[0]))/2, footer_y), footer, fill=(126, 100, 103), font=footer_font)

    output = BytesIO()
    output.name = "Anya_Nikita_Memory_Quest.jpg"
    canvas.save(output, format="JPEG", quality=90, optimize=True)
    output.seek(0)
    return output


def send_memory_collage(chat_id, user_id):
    """Створює колаж і відправляє його у Telegram."""
    try:
        collage = create_memory_collage(user_id)
        if collage is None:
            bot.send_message(chat_id, "📸 Для колажу поки немає фотографій.")
            return False
        bot.send_photo(
            chat_id,
            collage,
            caption=(
                "🌸 *Ваш Memory Quest — в одному кадрі*\n\n"
                "Збережіть цей колаж. Через роки він поверне вас у цей день ✨"
            ),
            parse_mode="Markdown"
        )
        return True
    except Exception as exc:
        print(f"Помилка створення колажу: {exc}")
        bot.send_message(chat_id, "📸 Фото збережені, але колаж зараз не вдалося зібрати.")
        return False

# ── KEYBOARDS ──────────────────────────────────────
def kb(*buttons, row_width=1):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=row_width)
    for b in buttons:
        markup.add(types.KeyboardButton(b))
    return markup

def kb_inline(*pairs):
    """pairs = [(text, callback_data), ...]"""
    markup = types.InlineKeyboardMarkup()
    for text, data in pairs:
        markup.add(types.InlineKeyboardButton(text, callback_data=data))
    return markup

def kb_remove():
    return types.ReplyKeyboardRemove()

def kb_url(text, url, back_text=None, back_data=None):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text, url=url))
    if back_text and back_data:
        markup.add(types.InlineKeyboardButton(back_text, callback_data=back_data))
    return markup

# ── SCREENS ────────────────────────────────────────

def send_cover(chat_id, user_id):
    state = get_state(user_id)
    state["screen"] = "cover"
    save_state(user_id, state)

    bot.send_message(
        chat_id,
        (
            f"{ROSE}{ROSE}{ROSE}\n\n"
            f"*Аня & Нікіта*\n"
            f" {EVENT_DATE} · Київ\n\n"
            f"━━━━━━━━━━━━━━━\n\n"
            f"Любі наші Аня та Нікіта\\!\n\n"
            f"Сьогодні ми хочемо подарувати вам не річ і не конверт\\.\n\n"
            f"Ми хочемо подарувати вам *пригоду\\.*\n\n"
            f"Можливо, через роки ви забудете суму нашого подарунка\\.\n"
            f"Але ми дуже хочемо, щоб ви пам'ятали цей день\\.\n\n"
            f"━━━━━━━━━━━━━━━\n\n"
            f"_З любов'ю, Володя та Ірина_ {GOLD}"
        ),
        parse_mode="MarkdownV2",
        reply_markup=kb(f"{ROSE} Почати пригоду")
    )


def send_hub(chat_id, user_id):
    state = get_state(user_id)
    state["screen"] = "hub"
    save_state(user_id, state)

    done = len(state["completed"])
    total = len(LOCATIONS)

    # Progress bar
    filled = "█" * done
    empty  = "░" * (total - done)
    progress = f"{filled}{empty} {done}/{total}"

    # Location list
    loc_lines = []
    for i, loc in enumerate(LOCATIONS):
        if i in state["completed"]:
            icon = "✅"
            name = loc["name"]
        elif i == state["current_loc"]:
            icon = "▶️"
            name = f"*Завдання {i+1}*"
        else:
            icon = "🔒"
            name = f"Завдання {i+1}"
        loc_lines.append(f"{icon} {name}")

    # PIN collected
    pin_display = ""
    if state["pins"]:
        digits = " · ".join(str(p) for p in state["pins"])
        pin_display = f"\n\n🔑 PIN зібрано: *{digits}*"

    text = (
        f"🗺 *Маршрут*\n"
        f"`{progress}`\n\n"
        + "\n".join(loc_lines)
        + pin_display
    )

    current = LOCATIONS[state["current_loc"]]
    if current.get("is_final"):
        btn = f"{MAP} Перейти до фіналу"
    else:
        btn = f"{MAP} Розпочати завдання {state['current_loc']+1}"

    bot.send_message(
        chat_id, text,
        parse_mode="Markdown",
        reply_markup=kb(btn, f"{GOLD} Допомога")
    )


def send_riddle(chat_id, user_id):
    state = get_state(user_id)
    loc = LOCATIONS[state["current_loc"]]
    state["screen"] = "riddle"
    save_state(user_id, state)

    i = state["current_loc"]
    bot.send_message(
        chat_id,
        (
            f"{MAP} *Завдання {i+1} з {len(LOCATIONS)}*\n"
            f"Тема: _{loc['theme']}_\n\n"
            f"━━━━━━━━━━━━━━━\n\n"
            f"🔍 *ЗАГАДКА*\n\n"
            f"{loc['riddle']}"
        ),
        parse_mode="Markdown",
        reply_markup=kb(
            "💡 Підказка",
            "🗺 Відкрити карту",
            "← Карта квесту"
        )
    )
    bot.send_message(
        chat_id,
        "Напиши назву місця 👇",
        reply_markup=kb("💡 Підказка", "🗺 Відкрити карту", "← Карта квесту")
    )


def send_hint(chat_id, user_id):
    state = get_state(user_id)
    loc = LOCATIONS[state["current_loc"]]
    i = state["current_loc"]
    used = state["hints_used"][i]

    if used >= len(loc["hints"]):
        bot.send_message(chat_id, "Всі підказки використано 🙈\nТи впораєшся!")
        return

    hint_text = loc["hints"][used]
    state["hints_used"][i] += 1
    save_state(user_id, state)

    bot.send_message(
        chat_id,
        f"💡 *Підказка {used+1}:*\n\n_{hint_text}_",
        parse_mode="Markdown"
    )


def check_answer(chat_id, user_id, text):
    state = get_state(user_id)
    loc = LOCATIONS[state["current_loc"]]
    answer = text.strip().lower()

    if any(answer == a or (len(answer) > 3 and a.startswith(answer[:4]))
           for a in loc["answers"]):
        # Correct!
        bot.send_message(
            chat_id,
            f"✅ *Правильно\\!*\n\n_{loc['name']}_\n\nПрокладаємо маршрут\\.\\.\\.",
            parse_mode="MarkdownV2"
        )
        # Send maps link
        bot.send_message(
            chat_id,
            f"{MAP} Відкрий Google Maps:",
            reply_markup=kb_url(
                f"📍 Маршрут до {loc['name']}",
                loc["maps_url"],
            )
        )
        state["screen"] = "navigate"
        save_state(user_id, state)
        bot.send_message(
            chat_id,
            "Коли будете на місці — натисніть кнопку 👇",
            reply_markup=kb(f"📍 Я на місці!")
        )
    else:
        bot.send_message(
            chat_id,
            "Спробуйте ще… 🤔\nПідказка допоможе якщо потрібно.",
            reply_markup=kb("💡 Підказка", "🗺 Відкрити карту", "← Карта квесту")
        )


def send_task(chat_id, user_id):
    state = get_state(user_id)
    loc = LOCATIONS[state["current_loc"]]
    state["screen"] = "task"
    save_state(user_id, state)

    # Wish
    bot.send_message(
        chat_id,
        (
            f"🌸 *{loc['name']}*\n"
            f"_{loc['theme']}_\n\n"
            f"━━━━━━━━━━━━━━━\n\n"
            f"{loc['wish']}"
        ),
        parse_mode="Markdown"
    )

    time.sleep(1)

    # Task
    bot.send_message(
        chat_id,
        f"🎯 *Ваше завдання:*\n\n{loc['task']}",
        parse_mode="Markdown"
    )

    time.sleep(1)

    # Photo/video prompt
    is_video = loc.get("is_video", False)
    if is_video:
        bot.send_message(
            chat_id,
            f"{VIDEO} {loc['photo_prompt']}\n\nНадішліть відео у цей чат 👇",
            reply_markup=kb("⏭ Пропустити відео")
        )
    else:
        bot.send_message(
            chat_id,
            f"{CAMERA} {loc['photo_prompt']}\n\nНадішліть фото у цей чат 👇",
            reply_markup=kb("⏭ Пропустити фото")
        )


def send_reveal(chat_id, user_id):
    state = get_state(user_id)
    loc = LOCATIONS[state["current_loc"]]
    state["screen"] = "reveal"
    save_state(user_id, state)

    # Big word reveal
    word = loc["reveal_word"]
    bot.send_message(
        chat_id,
        (
            f"{'✦ ' * 3}\n\n"
            f"*{word}*\n\n"
            f"{'✦ ' * 3}"
        ),
        parse_mode="Markdown"
    )

    time.sleep(0.8)

    bot.send_message(
        chat_id,
        f"_{loc['reveal_wish']}_",
        parse_mode="Markdown"
    )

    time.sleep(0.8)

    # PIN reveal (if applicable)
    if loc["pin"] is not None:
        pin = loc["pin"]
        state["pins"].append(pin)
        save_state(user_id, state)

        bot.send_message(
            chat_id,
            (
                f"🔑 *PIN цієї локації:*\n\n"
                f"┌─────────┐\n"
                f"│    *{pin}*    │\n"
                f"└─────────┘\n\n"
                f"_Запам'ятайте цю цифру!_"
            ),
            parse_mode="Markdown"
        )
        time.sleep(0.5)

    # Next button
    next_idx = state["current_loc"] + 1
    if next_idx < len(LOCATIONS):
        next_loc = LOCATIONS[next_idx]
        bot.send_message(
            chat_id,
            f"Продовжуємо? 👇",
            reply_markup=kb(
                f"→ Наступне завдання: {next_idx+1}/{len(LOCATIONS)}",
                "← Карта квесту"
            )
        )
    else:
        bot.send_message(
            chat_id,
            "← Карта квесту",
            reply_markup=kb("← Карта квесту")
        )


def complete_location(chat_id, user_id):
    state = get_state(user_id)
    i = state["current_loc"]

    if i not in state["completed"]:
        state["completed"].append(i)

    # Move to next
    if i + 1 < len(LOCATIONS):
        state["current_loc"] = i + 1

    save_state(user_id, state)


def send_pin_screen(chat_id, user_id):
    state = get_state(user_id)
    state["screen"] = "pin"
    save_state(user_id, state)

    pins_str = " · ".join(str(p) for p in state["pins"]) if state["pins"] else "—"

    bot.send_message(
        chat_id,
        (
            f"🏆 *Введіть PIN-код*\n\n"
            f"Ви зібрали цифри з кожної локації.\n\n"
            f"🔑 Ваші цифри: `{pins_str}`\n\n"
            f"Введіть 4-значний PIN-код 👇\n"
            f"_(наприклад: 1234)_"
        ),
        parse_mode="Markdown",
        reply_markup=kb("← Карта квесту")
    )


def check_pin(chat_id, user_id, text):
    state = get_state(user_id)
    digits = [int(c) for c in text.strip() if c.isdigit()]

    if digits == CORRECT_PIN:
        send_final(chat_id, user_id)
    else:
        bot.send_message(
            chat_id,
            "❌ Невірний код.\nПеревірте цифри з локацій і спробуйте ще.",
            reply_markup=kb("← Карта квесту")
        )


def send_final(chat_id, user_id):
    state = get_state(user_id)
    state["screen"] = "final"
    save_state(user_id, state)

    elapsed = int((time.time() - state["started_at"]) / 60)
    photos = len(_photo_items(state))

    # Celebration
    bot.send_message(chat_id, "🎊🌸🎊🌸🎊🌸🎊")

    time.sleep(0.5)

    bot.send_message(
        chat_id,
        (
            f"💍 *Вітаємо, Аня & Нікіта\\!*\n\n"
            f"━━━━━━━━━━━━━━━\n\n"
            f"🗺 Локацій пройдено: *{len(state['completed'])}*\n"
            f"📸 Фото збережено: *{photos}*\n"
            f"⏱ Час пригоди: *{elapsed} хв*\n"
            f"🔑 PIN\\-код: *4 · 2 · 6 · 4*\n"
            f"💍 Обітниці: ✓\n\n"
            f"━━━━━━━━━━━━━━━"
        ),
        parse_mode="MarkdownV2"
    )

    time.sleep(1)

    # Gift
    bot.send_message(
        chat_id,
        (
            f"🎁 *Ваш подарунок*\n\n"
            f"Банківська картка з грошовим подарунком\n"
            f"чекає на вас у Володі та Ірини\\.\n\n"
            f"Це — символ початку вашого спільного дому\n"
            f"і всього, що ви збудуєте разом\\."
        ),
        parse_mode="MarkdownV2"
    )

    time.sleep(1)

    # Final letter
    bot.send_message(
        chat_id,
        (
            f"✦ *Фінальний лист*\n\n"
            f"Сьогодні ви шукали локації\\.\n"
            f"Відгадували загадки\\.\n"
            f"Трималися за руки\\.\n"
            f"Давали обіцянки там де все починалось\\.\n\n"
            f"І створили те, що не можна купити —\n"
            f"*спогад\\.*\n\n"
            f"Нехай у вашій родині завжди будуть:\n"
            f"Кохання\\. Довіра\\. Повага\\.\n"
            f"Радість\\. Вірність\\. Початок\\.\n\n"
            f"_З любов'ю, Володя та Ірина ✦_"
        ),
        parse_mode="MarkdownV2"
    )

    time.sleep(1.5)

    # Memory collage
    if photos > 0:
        bot.send_message(chat_id, "📸 А тепер — ваш день в одному кадрі…")
        time.sleep(0.8)
        send_memory_collage(chat_id, user_id)
        time.sleep(1.2)

    # Surprise
    bot.send_message(
        chat_id,
        f"🌟 Залишився один сюрприз...",
        reply_markup=kb("✨ Відкрити сюрприз")
    )


def send_proposal(chat_id, user_id):
    state = get_state(user_id)
    state["screen"] = "proposal"
    save_state(user_id, state)

    bot.send_message(
        chat_id,
        (
            f"✦ *Другий сюрприз*\n\n"
            f"━━━━━━━━━━━━━━━\n\n"
            f"Ви щойно закінчили квест там,\n"
            f"де у вас все починалось.\n\n"
            f"Нехай пройдуть роки.\n"
            f"Нехай буде багато інших місць і подорожей.\n"
            f"Але Зоопарк 4 Сезони завжди буде\n"
            f"у вашій пам'яті —\n"
            f"як місце де все починалось."
        ),
        parse_mode="Markdown"
    )

    time.sleep(1.5)

    bot.send_message(
        chat_id,
        (
            f"💡 *Поки ви проходили цей маршрут —*\n"
            f"ви тестували продукт, якого ще не існує у світі.\n\n"
           
        ),
        parse_mode="Markdown"
    )

    time.sleep(1.5)

    bot.send_message(
        chat_id,
        (
            f"🤝 *Пропозиція*\n\n"
            f"Поговорити про те, щоб створити\n"
            f"Memory Quest разом.\n\n"
            f"*Аня* — сильний Product Manager.\n"
            f"*Нікіта* — сильний розробник.\n"
            f"*Ми* — ідея і перший квест."
            f"*Просто — початок чогось спільного.*"
        ),
        parse_mode="Markdown",
        reply_markup=kb(
            "✦ Підписати меморандум",
            "💍 Завершити пригоду"
        )
    )


def send_mou(chat_id, user_id):
    bot.send_message(
        chat_id,
        (
            f"📜 *Меморандум про наміри*\n\n"
            f"Цей документ не створює зобов'язань.\n"
            f"Він лише підтверджує бажання\n"
            f"створити щось красиве разом.\n\n"
            f"━━━━━━━━━━━━━━━\n\n"
            f"✦ Володя\n"
            f"✦ Ірина\n"
            f"✦ Аня ← ваш підпис\n"
            f"✦ Нікіта ← ваш підпис\n\n"
            f"━━━━━━━━━━━━━━━\n\n"
            f"_Натисніть щоб підписати_"
        ),
        parse_mode="Markdown",
        reply_markup=kb(
            "✦ Аня підписує",
            "✦ Нікіта підписує",
            "💍 Завершити пригоду"
        )
    )


def send_end(chat_id, user_id):
    bot.send_message(
        chat_id,
        (
            f"🌸✦🌸✦🌸\n\n"
            f"*Memory Quest завершено.*\n\n"
            f"_Аня & Нікіта _\n\n"
            f"Дякуємо що довіряєте нам\n"
            f"найважливіший день.\n\n"
            f"До зустрічі після весілля ✦\n\n"
            f"🌸✦🌸✦🌸"
        ),
        parse_mode="Markdown",
        reply_markup=kb_remove()
    )


# ── MESSAGE HANDLER ────────────────────────────────

@bot.message_handler(commands=["start"])
def handle_start(message):
    uid = message.from_user.id
    cid = message.chat.id
    sessions.pop(uid, None)  # reset
    send_cover(cid, uid)


@bot.message_handler(commands=["map", "карта"])
def handle_map(message):
    uid = message.from_user.id
    send_hub(message.chat.id, uid)


@bot.message_handler(content_types=["photo"])
def handle_photo(message):
    uid = message.from_user.id
    cid = message.chat.id
    state = get_state(uid)

    if state["screen"] == "task":
        loc = LOCATIONS[state["current_loc"]]
        state["photos"].append({
            "type": "photo",
            "file_id": message.photo[-1].file_id,
            "location_id": loc["id"],
            "location_name": loc["name"],
        })
        save_state(uid, state)
        bot.send_message(cid, f"{CAMERA} Фото збережено в книзі спогадів ✓")
        time.sleep(0.5)
        send_reveal(cid, uid)


@bot.message_handler(content_types=["video"])
def handle_video(message):
    uid = message.from_user.id
    cid = message.chat.id
    state = get_state(uid)

    if state["screen"] == "task":
        loc = LOCATIONS[state["current_loc"]]
        state["photos"].append({
            "type": "video",
            "file_id": message.video.file_id,
            "location_id": loc["id"],
            "location_name": loc["name"],
        })
        save_state(uid, state)
        bot.send_message(cid, f"{VIDEO} Відео-капсула збережена на 20 років ✓")
        time.sleep(0.5)
        send_reveal(cid, uid)


@bot.message_handler(content_types=["text"])
def handle_text(message):
    uid = message.from_user.id
    cid = message.chat.id
    text = message.text.strip()
    state = get_state(uid)
    screen = state["screen"]
    loc = LOCATIONS[state["current_loc"]]

    # ── COVER ──
    if ROSE in text and "Почати" in text:
        send_hub(cid, uid)
        return

    # ── HUB ──
    if "Карта квесту" in text or "← Карта" in text:
        send_hub(cid, uid)
        return

    if "Розпочати завдання" in text or "Перейти до фіналу" in text:
        if loc.get("is_final"):
            send_pin_screen(cid, uid)
        else:
            send_riddle(cid, uid)
        return

    if "Допомога" in text:
        bot.send_message(
            cid,
            (
                "ℹ️ *Допомога*\n\n"
                "• Натисни *Розпочати завдання* щоб почати\n"
                "• Відгадай загадку і напиши відповідь\n"
                "• Натисни *💡 Підказка* якщо потрібно\n"
                "• Коли на місці — надішли фото\n"
                "• PIN збирається автоматично\n\n"
                "/start — почати спочатку\n"
                "/map — карта квесту"
            ),
            parse_mode="Markdown"
        )
        return

    # ── RIDDLE ──
    if screen == "riddle":
        # Перехоплюємо всі кнопки ДО check_answer
        if "Підказка" in text:
            send_hint(cid, uid)
            return
        if ("карту" in text.lower() or "Карту" in text
                or "Відкрити" in text or "🗺" in text):
            bot.send_message(
                cid,
                "Відкрий Google Maps:",
                reply_markup=kb_url(
                    f"📍 Маршрут до {loc['name']}",
                    loc["maps_url"]
                )
            )
            return
        if "Карта квесту" in text or "← Карта" in text:
            send_hub(cid, uid)
            return
        # Тільки якщо це реальна текстова відповідь
        check_answer(cid, uid, text)
        return

    # ── NAVIGATE — on site ──
    if screen == "navigate" and "на місці" in text.lower():
        bot.send_message(cid, f"✓ Прибуття підтверджено! Вітаємо на *{loc['name']}*!", parse_mode="Markdown")
        time.sleep(0.5)
        send_task(cid, uid)
        return

    # ── TASK ──
    if screen == "task":
        if "Пропустити" in text:
            state["photos"].append(None)
            save_state(uid, state)
            send_reveal(cid, uid)
            return

    # ── REVEAL ──
    if screen == "reveal":
        if "Наступне завдання" in text:
            complete_location(cid, uid)
            new_loc = LOCATIONS[state["current_loc"]]
            if new_loc.get("is_final"):
                send_hub(cid, uid)
            else:
                send_riddle(cid, uid)
            return

    # ── PIN ENTRY ──
    if screen == "pin":
        digits = "".join(c for c in text if c.isdigit())
        if len(digits) == 4:
            check_pin(cid, uid, digits)
            return

    # ── FINAL ──
    if screen == "final" and "Відкрити сюрприз" in text:
        send_proposal(cid, uid)
        return

    # ── PROPOSAL ──
    if screen == "proposal":
        if "меморандум" in text.lower() or "Підписати" in text:
            send_mou(cid, uid)
            return
        if "Завершити" in text:
            send_end(cid, uid)
            return

    # ── MOU signing ──
    if "Аня підписує" in text:
        bot.send_message(cid, "✦ *Аня підписала меморандум* ✓\n\n_Ваш підпис збережено._", parse_mode="Markdown")
        return

    if "Нікіта підписує" in text:
        bot.send_message(cid, "✦ *Нікіта підписав меморандум* ✓\n\n_Ваш підпис збережено._", parse_mode="Markdown")
        return

    if "Завершити пригоду" in text:
        send_end(cid, uid)
        return


# ── RUN ────────────────────────────────────────────
if __name__ == "__main__":
    print("Memory Quest Bot запущено 🌸")
    print("Натисніть Ctrl+C щоб зупинити")
    bot.infinity_polling()
