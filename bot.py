import logging
from aiogram import Bot, Dispatcher, executor, types
import re

TOKEN = "8955397294:AAEyrrWRR_BCv4_OYK3qcYU3OH1RAJcYJMo"
ADMIN_ID = 8614033857  # O'z ID raqamingiz

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

user_steps = {}
user_data = {}
all_users = set()

DISTRICTS = {
    "Toshkent sh.": [
        "Bektemir tumani", "Chilonzor tumani", "Mirobod tumani", "Mirzo Ulug'bek tumani",
        "Olmazor tumani", "Sergeli tumani", "Shayxontohur tumani", "Uchtepa tumani",
        "Yakkasaroy tumani", "Yashnobod tumani", "Yunusobod tumani", "Yangihayot tumani"
    ],
    "Toshkent v.": [
        "Angren sh.", "Bekobod sh.", "Chirchiq sh.", "Olmaliq sh.", "Nurafshon sh.", "Yangiyo'l sh.",
        "Oqqo'rg'on tumani", "Bo'ka tumani", "Chinoz tumani", "Qibray tumani", "Parkent tumani",
        "Piskent tumani", "Quyi Chirchiq tumani", "O'rta Chirchiq tumani", "Yangiyo'l tumani",
        "Yuqori Chirchiq tumani", "Zangiota tumani", "Bo'stonliq tumani", "Taqachi tumani"
    ],
    "Andijon": [
        "Andijon sh.", "Xonobod sh.", "Andijon tumani", "Asaka tumani", "Baliqchi tumani",
        "Buloqboshi tumani", "Bo'ston tumani", "Jalaquduq tumani", "Izboskan tumani",
        "Marhamat tumani", "Oltinko'l tumani", "Paxtaobod tumani",
        "Qo'rg'ontepa tumani", "Shahrixon tumani", "Ulug'nor tumani"
    ],
    "Buxoro": [
        "Buxoro sh.", "Kogon sh.", "Buxoro tumani", "G'ijduvon tumani", "Jondor tumani",
        "Kogon tumani", "Olot tumani", "Peshku tumani", "Romitan tumani", "Shofirkon tumani",
        "Vobkent tumani", "Qorovulbozor tumani"
    ],
    "Jizzax": [
        "Jizzax sh.", "Arnasoy tumani", "Baxmal tumani", "Do'stlik tumani", "Forish tumani",
        "G'allaorol tumani", "Sharof Rashidov tumani", "Mirzacho'l tumani", "Paxtakor tumani",
        "Yangiobod tumani", "Zafarobod tumani", "Zomin tumani"
    ],
    "Qashqadaryo": [
        "Qarshi sh.", "Shahrisabz sh.", "Chiroqchi tumani", "Dehqonobod tumani", "G'uzor tumani",
        "Kasbi tumani", "Kitob tumani", "Koson tumani", "Mirishkor tumani", "Muborak tumani",
        "Nishon tumani", "Qamashi tumani", "Qarshi tumani", "Shahrisabz tumani", "Yakkabog' tumani"
    ],
    "Navoiy": [
        "Navoiy sh.", "Zarafshon sh.", "Konimex tumani", "Karmana tumani", "Qiziltepa tumani",
        "Xatirchi tumani", "Navbahor tumani", "Nurota tumani", "Tomdi tumani", "Uchquduq tumani"
    ],
    "Namangan": [
        "Namangan sh.", "Chortoq tumani", "Chust tumani", "Kosonsoy tumani", "Mingbuloq tumani",
        "Namangan tumani", "Norin tumani", "Pop tumani", "To'raqo'rg'on tumani",
        "Uchqo'rg'on tumani", "Uychi tumani", "Yangiqo'rg'on tumani"
    ],
    "Samarqand": [
        "Samarqand sh.", "Kattaqo'rg'on sh.", "Oqdaryo tumani", "Bulung'ur tumani",
        "Jomboy tumani", "Kattaqo'rg'on tumani", "Qo'shrabot tumani", "Narpay tumani",
        "Nurobod tumani", "Paxtachi tumani", "Payariq tumani", "Samarqand tumani",
        "Toyloq tumani", "Urgut tumani"
    ],
    "Sirdaryo": [
        "Guliston sh.", "Shirin sh.", "Yangiyer sh.", "Boyovut tumani", "Guliston tumani",
        "Mirzaobod tumani", "Oqoltin tumani", "Sardoba tumani", "Sayxunobod tumani",
        "Sirdaryo tumani", "Xovos tumani"
    ],
    "Surxondaryo": [
        "Termiz sh.", "Angor tumani", "Boysun tumani", "Denov tumani", "Jarqo'rg'on tumani",
        "Muzrabot tumani", "Oltinsoy tumani", "Qiziriq tumani", "Qumqo'rg'on tumani",
        "Sariosiyo tumani", "Sherobod tumani", "Sho'rchi tumani", "Termiz tumani", "Uzun tumani"
    ],
    "Farg'ona": [
        "Farg'ona sh.", "Marg'ilon sh.", "Qo'qon sh.", "Quvasoy sh.", "Oltiariq tumani",
        "Bag'dod tumani", "Beshariq tumani", "Buvayda tumani", "Dang'ara tumani",
        "Farg'ona tumani", "Furqat tumani", "Qo'shtepa tumani", "Quva tumani",
        "Rishton tumani", "So'x tumani", "Toshloq tumani", "Uchko'prik tumani", "Yozyovon tumani"
    ],
    "Xorazm": [
        "Urganch sh.", "Xiva sh.", "Bog'ot tumani", "Gurlan tumani", "Xonqa tumani",
        "Hazorasp tumani", "Qo'shko'pir tumani", "Shovot tumani", "Urganch tumani",
        "Yangiariq tumani", "Yangibozor tumani"
    ]
}

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    all_users.add(user_id)
    user_steps[user_id] = "language"
    user_data[user_id] = {}
    
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    keyboard.add("Uzbek", "Russian")
    await message.answer("Assalomu alaykum! Xush kelibsiz. Tilni tanlang:", reply_markup=keyboard)

@dp.message_handler(content_types=types.ContentTypes.CONTACT)
async def process_contact(message: types.Message):
    user_id = message.from_user.id
    all_users.add(user_id)
    if user_steps.get(user_id) == "phone":
        user_data[user_id]["phone"] = message.contact.phone_number
        user_steps[user_id] = "region"
        
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        for reg in DISTRICTS.keys():
            keyboard.add(reg)
            
        await message.answer("Telefon raqamingiz qabul qilindi! Iltimos, viloyatingizni tanlang:", reply_markup=keyboard)

@dp.message_handler()
async def process_messages(message: types.Message):
    user_id = message.from_user.id
    text = message.text
    step = user_steps.get(user_id)
    all_users.add(user_id)

    # 1. AGAR ADMIN XABAR Yozsa
    if user_id == ADMIN_ID:
        # A) Agar promokod xabariga REPLY (Javob berish) qilingan bo'lsa -> Faqat o'sha mijozga "Sizning bonusingiz:" deb boradi
        if message.reply_to_message:
            reply_text = message.reply_to_message.text
            id_match = re.search(r"ID:\s*`?(\d+)`?", reply_text)
            if id_match:
                client_id = int(id_match.group(1))
                try:
                    await bot.send_message(client_id, f"Sizning bonusingiz:\n\n{text}")
                    await message.answer("✅ Bonus mijozga yuborildi!")
                except Exception as e:
                    await message.answer(f"❌ Xatolik: {e}")
                return

        # B) Agar REPLY qilinmasdan shunchaki yozilsa -> Barcha foydalanuvchilarga oddiy SMS bo'lib boradi
        success_count = 0
        for uid in all_users:
            if uid == ADMIN_ID:
                continue
            try:
                await bot.send_message(uid, text)
                success_count += 1
            except Exception as e:
                print(f"Yuborib bo'lmadi {uid}: {e}")
        await message.answer(f"✅ Xabar {success_count} ta foydalanuvchiga oddiy SMS sifatida tarqatildi!")
        return

    # 2. Ro'yxatdan o'tish bosqichlari
    if step == "language":
        if text in ["Uzbek", "Russian"]:
            user_data[user_id]["language"] = text
            user_steps[user_id] = "phone"
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
            keyboard.add(types.KeyboardButton("Telefon raqamni yuborish", request_contact=True))
            await message.answer("Iltimos, telefon raqamingizni yuboring:", reply_markup=keyboard)
        else:
            await message.answer("Iltimos, tugmalardan birini bosing!")

    elif step == "region":
        if text in DISTRICTS:
            user_data[user_id]["region"] = text
            user_steps[user_id] = "district"
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            for dist in DISTRICTS[text]:
                keyboard.add(dist)
            await message.answer(f"\"{text}\" tanlandi. Endi tumaningizni tanlang:", reply_markup=keyboard)
        else:
            await message.answer("Iltimos, tugmalardagi viloyatlardan birini tanlang!")

    elif step == "district":
        user_data[user_id]["district"] = text
        user_steps[user_id] = "menu"
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        keyboard.add("Promokod yuborish", "Profil")
        await message.answer("Tumaningiz qabul qilindi!", reply_markup=keyboard)

    elif step == "promocode":
        phone = user_data[user_id].get("phone", "Ko'rsatilmadi")
        region = user_data[user_id].get("region", "Ko'rsatilmadi")
        district = user_data[user_id].get("district", "Ko'rsatilmadi")
        user = message.from_user
        
        await message.answer(f"Hurmatli {user.full_name}, Siz yuborgan promokod qabul qilindi va tekshiruvga yuborildi.")
        
        admin_text = (
            f"📩 **Yangi promokod keldi!**\n\n"
            f"👤 Ismi: {user.full_name}\n"
            f"🆔 ID: `{user.id}`\n"
            f"📞 Telefon: {phone}\n"
            f"📍 Viloyat: {region}\n"
            f"🏙 Tuman: {district}\n"
            f"🔑 Promokod: **{text}**"
        )
        
        try:
            await bot.send_message(ADMIN_ID, admin_text, parse_mode="Markdown")
        except Exception as e:
            print(f"Xatolik: {e}")
            
        user_steps[user_id] = "menu"

    else:
        if text == "Promokod yuborish":
            user_steps[user_id] = "promocode"
            await message.answer("Iltimos, 6 xonali promokodingizni yozib yuboring:")
        elif text == "Profil":
            phone = user_data[user_id].get("phone", "Kiritilmagan")
            region = user_data[user_id].get("region", "Kiritilmagan")
            district = user_data[user_id].get("district", "Kiritilmagan")
            
            profile_text = (
                f"👤 **Sizning profilingiz:**\n\n"
                f"Ism: {message.from_user.full_name}\n"
                f"Telefon: {phone}\n"
                f"Viloyat: {region}\n"
                f"Tuman: {district}"
            )
            await message.answer(profile_text, parse_mode="Markdown")
        else:
            await message.answer("Iltimos, pastdagi tugmalardan birini bosing.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, skip_updates=True)