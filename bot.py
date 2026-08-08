import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3

# ========== КОНФИГ ==========
BOT_TOKEN = "8955397294:AAFJLJICXY2Lyzp2ROkmNY3lj5ugai2ILYc"
ADMIN_ID = 8614033857

# ========== ДАТАБАЗА ==========
conn = sqlite3.connect('users.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    full_name TEXT,
    phone TEXT,
    region TEXT,
    district TEXT,
    language TEXT,
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS promo_codes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    code TEXT,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')
conn.commit()

# ========== FSM STATE ==========
class RegistrationStates(StatesGroup):
    language = State()
    region = State()
    district = State()
    phone = State()
    promo_code = State()

# Admin reply holati
admin_reply_mode = {}

# ========== БОТНИ ИШГА ТУШИРИШ ==========
logging.basicConfig(level=logging.INFO)
storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())

# ========== ВИЛОЯТЛАР ВА ТУМАНЛАР ==========
REGIONS = {
    "uz": {
        "Toshkent": ["Yakkasaroy", "Chilonzor", "Mirzo Ulug'bek", "Olmazor", "Bektemir", "Yangihayot", "Mirobod", "Shayxontohur", "Uchtepa"],
        "Samarqand": ["Samarqand shahri", "Bulung'ur", "Jomboy", "Ishtixon", "Kattaqo'rg'on", "Narpay", "Oqdaryo", "Pastdarg'om", "Payariq", "Toyloq", "Urgut"],
        "Buxoro": ["Buxoro shahri", "Jondor", "Kogon", "Olot", "Peshku", "Romitan", "Shofirkon", "Vobkent", "G'ijduvon"],
        "Farg'ona": ["Farg'ona shahri", "Oltiariq", "Beshariq", "Bog'dod", "Dang'ara", "Farg'ona", "Furqat", "Qo'qon", "Quvasoy", "Rishton", "Sox", "Toshloq", "Uchko'prik", "O'zbekiston", "Yozyovon"],
        "Andijon": ["Andijon shahri", "Asaka", "Baliqchi", "Buloqboshi", "Izboskan", "Jalaquduq", "Marhamat", "Oltinko'l", "Paxtaobod", "Qo'rg'ontepa", "Shahrixon", "Ulug'nar", "Xo'jaobod"],
        "Namangan": ["Namangan shahri", "Chortoq", "Chust", "Kosonsoy", "Mingbuloq", "Norin", "Pop", "To'raqo'rg'on", "Uchqo'rg'on", "Yangiqo'rg'on"],
        "Qashqadaryo": ["Qarshi shahri", "Dehqonobod", "G'uzor", "Kasbi", "Kitob", "Koson", "Muborak", "Nishon", "Shahrisabz", "Yakkabog'", "Chiroqchi"],
        "Surxondaryo": ["Termiz shahri", "Angor", "Bandixon", "Boysun", "Denov", "Jarqo'rg'on", "Muzrabot", "Oltinsoy", "Qiziriq", "Qumqo'rg'on", "Sariosiyo", "Sherobod", "Shurchi", "Termiz tumani"],
        "Jizzax": ["Jizzax shahri", "Zomin", "Zafarobod", "Mirzacho'l", "G'allaorol", "Do'stlik", "Sharof Rashidov", "Baxmal", "Yangiyo'l"],
        "Sirdaryo": ["Guliston shahri", "Sayxunobod", "Sardoba", "Mirzaobod", "Boyovut", "Oqoltin"],
        "Navoiy": ["Navoiy shahri", "Karmana", "Konimex", "Nurota", "Qiziltepa", "Tomdi", "Uchquduq", "Xatirchi"],
        "Xorazm": ["Urganch shahri", "Xiva", "To'rtko'l", "Qo'shko'pir", "Hazorasp", "Yangibozor", "Shovot", "Xonqa"],
        "Qoraqalpog'iston": ["Nukus shahri", "Amudaryo", "Beruniy", "Chimboy", "Ellikqal'a", "Kegeyli", "Mo'ynoq", "Qanliko'l", "Qo'ng'irot", "Taxiatosh", "To'rtko'l", "Xo'jayli", "Bo'zatov", "Taxtako'pir", "Shumanay"],
    },
    "ru": {
        "Ташкент": ["Яккасарай", "Чиланзор", "Миробод", "Мирзо-Улугбек", "Сергели", "Олмазор", "Бектемир", "Учтепа", "Шайхонтохур", "Янгихаёт"],
        "Самарканд": ["Самарканд", "Булунгур", "Джомбой", "Иштыхан", "Каттакурган", "Нарпай", "Акдарья", "Пастдаргом", "Пайарык", "Тайлак", "Ургут"],
        "Бухара": ["Бухара", "Джандар", "Каган", "Алат", "Пешку", "Ромитан", "Шафиркан", "Вабкент", "Гиждуван"],
        "Фергана": ["Фергана", "Алтыарык", "Бешарык", "Богдад", "Дангара", "Канибадам", "Коканд", "Кува", "Риштан", "Сохиб", "Ташлак", "Учкуприк", "Язъяван", "Узбекистан"],
        "Андижан": ["Андижан", "Асака", "Балыкчи", "Булокбоши", "Избаскан", "Джалакудук", "Мархамат", "Алтынкуль", "Пахтаабад", "Кургантепа", "Шахрихан", "Улугнор", "Ходжаабад"],
        "Наманган": ["Наманган", "Чартак", "Чуст", "Касансай", "Мингбулак", "Нарын", "Пап", "Туракурган", "Учкурган", "Янгикурган"],
        "Кашкадарья": ["Карши", "Дехканабад", "Гузар", "Кассби", "Китаб", "Косон", "Мубарек", "Нишан", "Шахрисабз", "Яккабаг", "Чиракчи"],
        "Сурхандарья": ["Термез", "Ангор", "Бандихан", "Байсун", "Денау", "Джаркурган", "Музарабад", "Алтынсай", "Кизирик", "Кумкурган", "Сариосия", "Шерабад", "Шурчи", "Термез район"],
        "Джизак": ["Джизак", "Заамин", "Зафарабад", "Мирзачуль", "Галляарал", "Дустлик", "Шараф-Рашидов", "Бахмал", "Янгиёль"],
        "Сырдарья": ["Гулистан", "Сайхунабад", "Сардоба", "Мирзаабад", "Баяут", "Акалтын"],
        "Навои": ["Навои", "Кармана", "Конимех", "Нурата", "Кизилтепа", "Тамды", "Учкудук", "Хатирчи"],
        "Хорезм": ["Ургенч", "Хива", "Турткуль", "Кошкупир", "Хазарасп", "Янгибазар", "Шават", "Ханка"],
        "Каракалпакстан": ["Нукус", "Амударья", "Беруни", "Чимбай", "Элликкала", "Кегейли", "Муйнак", "Канлыкуль", "Кунград", "Тахиаташ", "Турткуль", "Ходжейли", "Бозатау", "Тахтакупир", "Шуманай"]
    }
}

# ========== ТУГМАЛАР ==========
def get_start_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="▶️ START")]],
        resize_keyboard=True
    )
    return keyboard

def get_language_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🇺🇿 O'zbek")],
            [KeyboardButton(text="🇷🇺 Русский")]
        ],
        resize_keyboard=True
    )
    return keyboard

def get_region_keyboard(lang):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=region)] for region in REGIONS[lang].keys()],
        resize_keyboard=True
    )
    return keyboard

def get_district_keyboard(lang, region):
    districts = REGIONS[lang].get(region, [])
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=district)] for district in districts],
        resize_keyboard=True
    )
    return keyboard

def get_phone_keyboard(lang):
    if lang == "uz":
        text = "📱 Telefon raqamni yuborish"
    else:
        text = "📱 Отправить номер телефона"
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=text, request_contact=True)]],
        resize_keyboard=True
    )
    return keyboard

# ===== FOYDALANUVCHI MENYUSI =====
def get_user_keyboard(lang):
    if lang == "uz":
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="🎁 Promokod yuborish")],
                [KeyboardButton(text="👤 Mening profilim")]
            ],
            resize_keyboard=True
        )
    else:
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="🎁 Отправить промокод")],
                [KeyboardButton(text="👤 Мой профиль")]
            ],
            resize_keyboard=True
        )
    return keyboard

# ===== ADMIN MENYUSI =====
def get_admin_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📊 Statistika")],
            [KeyboardButton(text="📋 Promokodlar")],
            [KeyboardButton(text="📨 Xabar yuborish")]
        ],
        resize_keyboard=True
    )
    return keyboard

# ===== ADMIN REPLY KEYBOARD (9 TA BONUS TUGMALARI - TO'LIQ MATN) =====
def get_admin_reply_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎉Tabriklaymiz siz \"MUZLATGICH\" bonusiga ega bo'ldingiz🎉")],
            [KeyboardButton(text="🎉Tabriklaymiz siz \"AVTOMAT KIR YUVISH MASHINASI\" bonusiga ega bo'ldingiz🎉")],
            [KeyboardButton(text="🎉Tabriklaymiz siz \"KONDITSIONER\" bonusiga ega bo'ldingiz🎉")],
            [KeyboardButton(text="🎉Tabriklaymiz siz \"PRINTER\" bonusiga ega bo'ldingiz🎉")],
            [KeyboardButton(text="🎉Tabriklaymiz siz \"QOZONLAR TOPLAMI\" bonusiga ega bo'ldingiz🎉")],
            [KeyboardButton(text="🎉Tabriklaymiz siz \"BAGEMA TOPLAMI\" bonusiga ega bo'ldingiz🎉")],
            [KeyboardButton(text="🎉Tabriklaymiz siz \"CHANGYUTGICH\" bonusiga ega bo'ldingiz🎉")],
            [KeyboardButton(text="🎉Tabriklaymiz siz \"MINI KONDITSIONER\" bonusiga ega bo'ldingiz🎉")],
            [KeyboardButton(text="🎉Tabriklaymiz siz \"GAZ PLITA\" bonusiga ega bo'ldingiz🎉")]
        ],
        resize_keyboard=True
    )
    return keyboard

def get_back_keyboard(lang):
    if lang == "uz":
        keyboard = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="◀️ Orqaga")]],
            resize_keyboard=True
        )
    else:
        keyboard = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="◀️ Назад")]],
            resize_keyboard=True
        )
    return keyboard

def get_admin_reply_inline_keyboard(user_id):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✏️ Javob yozish", callback_data=f"reply_{user_id}")]
        ]
    )
    return keyboard

# ========== РАСМСИЗ МАТН ==========
async def send_welcome_without_image(message: types.Message, state: FSMContext):
    text = (
        "💰 *Mahsulot narxi: 7 500 000 so'm*\n\n"
        "🏆 *HALEY HY-3911 / HY-3916*\n"
        "✨ IDEAL GILAM YUVUVCHI\n\n"
        "🔥 TEZ QURITISH (Fast Drying)\n"
        "🎯 TURLI SIRTILAR UCHUN (All Surfaces)\n"
        "⚡ MAXIMUM POWER - 3600W\n"
        "🏠 SIZNING UYINGIZNI ISSIQROQ QILADI\n"
        "🧹 TO'LIQ AKSESSUARLAR TO'PLAMI\n\n"
        "🤖 Assalomu alaykum! HALEY yuvuvchi plisosini xarid qilganingiz uchun minnatdormiz.\n"
        "Botimiz orqali o'z bonusingizni aniqlang.\n"
        "Omad tilaymiz! 🍀\n\n"
        "👇 *Tilni tanlang / Выберите язык:*"
    )
    
    await message.answer(
        text=text,
        reply_markup=get_language_keyboard(),
        parse_mode="Markdown"
    )
    await state.set_state(RegistrationStates.language)

async def show_user_menu(message: types.Message, lang):
    if lang == "uz":
        await message.answer(
            "👋 Bosh menyu! Quyidagi tugmalardan birini tanlang:",
            reply_markup=get_user_keyboard(lang)
        )
    else:
        await message.answer(
            "👋 Главное меню! Выберите одну из кнопок:",
            reply_markup=get_user_keyboard(lang)
        )

async def show_admin_menu(message: types.Message):
    await message.answer(
        "👨‍💼 *Admin paneli*\n\n"
        "Quyidagi tugmalardan birini tanlang:",
        reply_markup=get_admin_keyboard(),
        parse_mode="Markdown"
    )

# ========== START ==========
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    
    if user_id == ADMIN_ID:
        await show_admin_menu(message)
        return
    
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    
    if user:
        lang = user[6]
        await show_user_menu(message, lang)
    else:
        await send_welcome_without_image(message, state)

@dp.message_handler(lambda message: message.text == "▶️ START")
async def start_button(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    
    if user_id == ADMIN_ID:
        await show_admin_menu(message)
        return
    
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    
    if user:
        lang = user[6]
        await show_user_menu(message, lang)
    else:
        await send_welcome_without_image(message, state)

# ========== ТИЛ ТАНЛАШ ==========
@dp.message_handler(state=RegistrationStates.language)
async def select_language(message: types.Message, state: FSMContext):
    if message.text in ["🇺🇿 O'zbek", "🇷🇺 Русский"]:
        lang = "uz" if "O'zbek" in message.text else "ru"
        await state.update_data(language=lang)
        
        if lang == "uz":
            await message.answer(
                "🏙️ Iltimos, yashash viloyatingizni tanlang:",
                reply_markup=get_region_keyboard(lang)
            )
        else:
            await message.answer(
                "🏙️ Пожалуйста, выберите вашу область:",
                reply_markup=get_region_keyboard(lang)
            )
        await state.set_state(RegistrationStates.region)
    else:
        await message.answer("Iltimos, tugmalardan birini tanlang / Пожалуйста, выберите кнопку")

# ========== ВИЛОЯТ ТАНЛАШ ==========
@dp.message_handler(state=RegistrationStates.region)
async def select_region(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get('language', 'uz')
    
    if message.text in REGIONS[lang].keys():
        await state.update_data(region=message.text)
        
        if lang == "uz":
            await message.answer(
                f"📍 {message.text} viloyatida qaysi tumandasiz?",
                reply_markup=get_district_keyboard(lang, message.text)
            )
        else:
            await message.answer(
                f"📍 В каком районе области {message.text}?",
                reply_markup=get_district_keyboard(lang, message.text)
            )
        await state.set_state(RegistrationStates.district)
    else:
        await message.answer("Iltimos, viloyatni tugmalardan tanlang")

# ========== ТУМАН ТАНЛАШ ==========
@dp.message_handler(state=RegistrationStates.district)
async def select_district(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get('language', 'uz')
    region = data.get('region')
    
    if message.text in REGIONS[lang].get(region, []):
        await state.update_data(district=message.text)
        await message.answer(
            "📱 Iltimos, telefon raqamingizni yuboring:",
            reply_markup=get_phone_keyboard(lang)
        )
        await state.set_state(RegistrationStates.phone)
    else:
        await message.answer("Iltimos, tumanni tugmalardan tanlang")

# ========== ТЕЛЕФОН РАҚАМ ==========
@dp.message_handler(state=RegistrationStates.phone, content_types=types.ContentType.CONTACT)
async def handle_phone(message: types.Message, state: FSMContext):
    contact = message.contact
    user_id = message.from_user.id
    data = await state.get_data()
    lang = data.get('language', 'uz')
    
    cursor.execute('''
    INSERT OR REPLACE INTO users (user_id, username, full_name, phone, region, district, language)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, message.from_user.username, message.from_user.full_name, 
          contact.phone_number, data.get('region'), data.get('district'), lang))
    conn.commit()
    
    await state.finish()
    
    if lang == "uz":
        await message.answer(
            f"🎉 *Tabriklaymiz {message.from_user.full_name}!*\n"
            f"Siz muvaffaqiyatli ro'yxatdan o'tdingiz! ✅\n\n"
            f"Endi quyidagi tugmalardan birini tanlang:",
            reply_markup=get_user_keyboard(lang),
            parse_mode="Markdown"
        )
    else:
        await message.answer(
            f"🎉 *Поздравляем {message.from_user.full_name}!*\n"
            f"Вы успешно зарегистрированы! ✅\n\n"
            f"Теперь выберите одну из кнопок:",
            reply_markup=get_user_keyboard(lang),
            parse_mode="Markdown"
        )

@dp.message_handler(state=RegistrationStates.phone)
async def phone_error(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    data = await state.get_data()
    lang = data.get('language', 'uz') if data else 'uz'
    if lang == "uz":
        await message.answer("❗ Iltimos, pastdagi tugma orqali telefon raqamingizni yuboring")
    else:
        await message.answer("❗ Пожалуйста, отправьте номер телефона через кнопку ниже")

# ========== PROFIL ==========
@dp.message_handler(lambda message: message.text in ["👤 Mening profilim", "👤 Мой профиль"])
async def show_profile(message: types.Message):
    user_id = message.from_user.id
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    
    if user:
        lang = user[6]
        if lang == "uz":
            text = f"👤 *Profil ma'lumotlari*\n\n"
            text += f"📛 Ism: {user[2]}\n"
            text += f"📱 Telefon: {user[3]}\n"
            text += f"📍 Viloyat: {user[4]}\n"
            text += f"🏘️ Tuman: {user[5]}\n"
            text += f"🗣️ Til: O'zbek"
        else:
            text = f"👤 *Данные профиля*\n\n"
            text += f"📛 Имя: {user[2]}\n"
            text += f"📱 Телефон: {user[3]}\n"
            text += f"📍 Область: {user[4]}\n"
            text += f"🏘️ Район: {user[5]}\n"
            text += f"🗣️ Язык: Русский"
        await message.answer(text, parse_mode="Markdown")

# ========== PROMOKOD ==========
@dp.message_handler(lambda message: message.text in ["🎁 Promokod yuborish", "🎁 Отправить промокод"])
async def send_promo_code(message: types.Message, state: FSMContext):
    cursor.execute("SELECT language FROM users WHERE user_id = ?", (message.from_user.id,))
    user = cursor.fetchone()
    lang = user[0] if user else "uz"
    
    if lang == "uz":
        await message.answer(
            "🔑 Iltimos, 6 xonali promokodni yuboring:",
            reply_markup=get_back_keyboard(lang)
        )
    else:
        await message.answer(
            "🔑 Пожалуйста, отправьте 6-значный промокод:",
            reply_markup=get_back_keyboard(lang)
        )
    await state.set_state(RegistrationStates.promo_code)

@dp.message_handler(state=RegistrationStates.promo_code)
async def handle_promo_code(message: types.Message, state: FSMContext):
    cursor.execute("SELECT language FROM users WHERE user_id = ?", (message.from_user.id,))
    user = cursor.fetchone()
    lang = user[0] if user else "uz"
    
    if message.text in ["◀️ Orqaga", "◀️ Назад"]:
        await state.finish()
        await show_user_menu(message, lang)
        return
    
    code = message.text.strip()
    user_id = message.from_user.id
    
    if len(code) == 6:
        cursor.execute("INSERT INTO promo_codes (user_id, code) VALUES (?, ?)", (user_id, code))
        conn.commit()
        
        cursor.execute("SELECT username, full_name, phone FROM users WHERE user_id = ?", (user_id,))
        user_data = cursor.fetchone()
        
        username = user_data[0] if user_data[0] else "Yo'q"
        
        admin_text = "📨 *Yangi promokod kelib tushdi!*\n\n"
        admin_text += f"👤 Foydalanuvchi: {user_data[1]}\n"
        admin_text += f"🆔 Username: @{username}\n"
        admin_text += f"📱 Telefon: {user_data[2]}\n"
        admin_text += f"🔑 Promokod: `{code}`"
        
        await bot.send_message(
            ADMIN_ID, 
            admin_text, 
            parse_mode="Markdown",
            reply_markup=get_admin_reply_inline_keyboard(user_id)
        )
        
        if lang == "uz":
            await message.answer(
                f"🎉 *Tabriklaymiz {message.from_user.full_name}!*\n"
                f"Sizning promokodingiz qabul qilindi! ✅\n\n"
                f"Tez orada bonusingiz aniqlanadi.",
                reply_markup=get_user_keyboard(lang),
                parse_mode="Markdown"
            )
        else:
            await message.answer(
                f"🎉 *Поздравляем {message.from_user.full_name}!*\n"
                f"Ваш промокод принят! ✅\n\n"
                f"Скоро ваш бонус будет определен.",
                reply_markup=get_user_keyboard(lang),
                parse_mode="Markdown"
            )
        await state.finish()
    else:
        if lang == "uz":
            await message.answer("❌ Iltimos, 6 xonali promokod yuboring!")
        else:
            await message.answer("❌ Пожалуйста, отправьте 6-значный промокод!")

# ========== ADMIN REPLY ==========
@dp.callback_query_handler(lambda c: c.data and c.data.startswith('reply_'))
async def admin_reply_callback(callback_query: types.CallbackQuery):
    user_id = int(callback_query.data.split('_')[1])
    
    if callback_query.from_user.id != ADMIN_ID:
        await callback_query.answer("Siz admin emassiz!", show_alert=True)
        return
    
    admin_reply_mode[ADMIN_ID] = user_id
    
    await callback_query.message.answer(
        f"✏️ *Javob yozing:*\n\n"
        f"Quyidagi bonus tugmalaridan birini bosing yoki o'z matningizni yozing:",
        reply_markup=get_admin_reply_keyboard(),
        parse_mode="Markdown"
    )
    await callback_query.answer()

# ========== ADMIN 9 TA BONUS TUGMALARI (TO'LIQ MATN BILAN) ==========
@dp.message_handler(lambda message: message.from_user.id == ADMIN_ID and message.text in [
    "🎉Tabriklaymiz siz \"MUZLATGICH\" bonusiga ega bo'ldingiz🎉",
    "🎉Tabriklaymiz siz \"AVTOMAT KIR YUVISH MASHINASI\" bonusiga ega bo'ldingiz🎉",
    "🎉Tabriklaymiz siz \"KONDITSIONER\" bonusiga ega bo'ldingiz🎉",
    "🎉Tabriklaymiz siz \"PRINTER\" bonusiga ega bo'ldingiz🎉",
    "🎉Tabriklaymiz siz \"QOZONLAR TOPLAMI\" bonusiga ega bo'ldingiz🎉",
    "🎉Tabriklaymiz siz \"BAGEMA TOPLAMI\" bonusiga ega bo'ldingiz🎉",
    "🎉Tabriklaymiz siz \"CHANGYUTGICH\" bonusiga ega bo'ldingiz🎉",
    "🎉Tabriklaymiz siz \"MINI KONDITSIONER\" bonusiga ega bo'ldingiz🎉",
    "🎉Tabriklaymiz siz \"GAZ PLITA\" bonusiga ega bo'ldingiz🎉"
])
async def admin_bonus_reply(message: types.Message):
    if ADMIN_ID in admin_reply_mode:
        target_user_id = admin_reply_mode[ADMIN_ID]
        del admin_reply_mode[ADMIN_ID]
        
        # Tugma matnining o'zi to'liq javob matni
        reply_text = message.text
        
        try:
            await bot.send_message(
                target_user_id, 
                f"{reply_text}", 
                parse_mode="Markdown"
            )
            await message.answer(
                f"✅ Bonus foydalanuvchiga yuborildi!",
                reply_markup=get_admin_keyboard()
            )
        except Exception as e:
            await message.answer(f"❌ Xatolik: {e}")
        return
    
    await message.answer("❗ Avval 'Javob yozish' tugmasini bosing!", reply_markup=get_admin_keyboard())

# ========== ADMIN MATN QABUL QILISH ==========
@dp.message_handler(lambda message: message.from_user.id == ADMIN_ID)
async def admin_handle_message(message: types.Message):
    # Bekor qilish
    if message.text == "❌ Bekor qilish":
        if ADMIN_ID in admin_reply_mode:
            del admin_reply_mode[ADMIN_ID]
        await message.answer(
            "❌ Bekor qilindi!",
            reply_markup=get_admin_keyboard()
        )
        return
    
    # Agar admin reply holatida bo'lsa va bonus tugmasi bo'lmasa -> o'z matni
    if ADMIN_ID in admin_reply_mode:
        target_user_id = admin_reply_mode[ADMIN_ID]
        del admin_reply_mode[ADMIN_ID]
        
        try:
            await bot.send_message(
                target_user_id, 
                f"📩 *Admin javobi:*\n\n{message.text}", 
                parse_mode="Markdown"
            )
            await message.answer(
                f"✅ Xabar foydalanuvchiga yuborildi!",
                reply_markup=get_admin_keyboard()
            )
        except Exception as e:
            await message.answer(f"❌ Xatolik: {e}")
        return
    
    # Admin tugmalarini ishlash
    if message.text == "📊 Statistika":
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM promo_codes")
        promo_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT full_name, phone, registered_at FROM users ORDER BY registered_at DESC LIMIT 5")
        last_users = cursor.fetchall()
        
        text = "📊 *Statistika*\n\n"
        text += f"👤 Foydalanuvchilar: {user_count}\n"
        text += f"🔑 Promokodlar: {promo_count}\n\n"
        text += "📌 *Oxirgi 5 foydalanuvchi:*\n"
        for user in last_users:
            text += f"• {user[0]} - {user[1]} ({user[2][:16]})\n"
        
        await message.answer(text, parse_mode="Markdown", reply_markup=get_admin_keyboard())
        return
    
    if message.text == "📋 Promokodlar":
        cursor.execute("SELECT code, user_id, created_at FROM promo_codes ORDER BY created_at DESC LIMIT 20")
        promos = cursor.fetchall()
        
        if not promos:
            await message.answer("❌ Hali hech qanday promokod yuborilmagan!", reply_markup=get_admin_keyboard())
            return
        
        text = "📋 *Oxirgi 20 ta promokod:*\n\n"
        for promo in promos:
            cursor.execute("SELECT full_name, phone FROM users WHERE user_id = ?", (promo[1],))
            user = cursor.fetchone()
            if user:
                text += f"🔑 `{promo[0]}` - {user[0]} ({user[1]})\n"
            else:
                text += f"🔑 `{promo[0]}` - Noma'lum\n"
        
        await message.answer(text, parse_mode="Markdown", reply_markup=get_admin_keyboard())
        return
    
    if message.text == "📨 Xabar yuborish":
        await message.answer(
            "📨 *Xabar yuborish*\n\n"
            "Barcha foydalanuvchilarga xabar yuborish uchun matn yozing:",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="❌ Bekor qilish")]],
                resize_keyboard=True
            )
        )
        return
    
    # Broadcast - barcha foydalanuvchilarga
    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()
    
    if not users:
        await message.answer("❌ Hali hech qanday foydalanuvchi ro'yxatdan o'tmagan!", reply_markup=get_admin_keyboard())
        return
    
    sent_count = 0
    for user in users:
        try:
            await bot.send_message(user[0], f"📢 *Xabar:*\n\n{message.text}", parse_mode="Markdown")
            sent_count += 1
            await asyncio.sleep(0.05)
        except:
            pass
    
    await message.answer(
        f"✅ Xabar {sent_count} ta foydalanuvchiga yuborildi!",
        reply_markup=get_admin_keyboard()
    )

# ========== БАРЧА ХАБАРЛАР (ENG OXIRGI) ==========
@dp.message_handler()
async def handle_all_messages(message: types.Message):
    user_id = message.from_user.id
    
    # Admin bo'lsa, admin_handle_message da ishlov beriladi
    if user_id == ADMIN_ID:
        return
    
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    
    if user:
        lang = user[6]
        await show_user_menu(message, lang)
        return
    
    await message.answer(
        "👋 *Assalomu alaykum!*\n\n"
        "Botimizdan foydalanish uchun quyidagi START tugmasini bosing:\n\n"
        "👇 *Нажмите кнопку START, чтобы начать:*",
        reply_markup=get_start_keyboard(),
        parse_mode="Markdown"
    )

# ========== ИШГА ТУШИРИШ ==========
if __name__ == "__main__":
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)