import os
import telebot
from PIL import Image

# BotFather'dan olingan tokeningiz
TOKEN = "9197758020:AAEo4p1XD5v6JdNttltLYcgx42hGec7oFNg"
bot = telebot.TeleBot(TOKEN)

# Foydalanuvchilarning rasmlarini vaqtincha saqlash uchun lug'at
user_images = {}

@bot.message_handler(commands=['start'])
def send_welcome(bot_instance, message):
    user_id = message.from_user.id
    user_images[user_id] = []
    bot.reply_to(message, "Salom! Men rasm-to-PDF botiman 📄\nMenga 1 tadan 10 tagacha rasm yuboring. Hammasini yuborib bo'lgach, /pdf deb yozing, men ularni bitta PDF qilib beraman!")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_id = message.from_user.id
    if user_id not in user_images:
        user_images[user_id] = []
    
    # Agar rasmlar soni 10 tadan oshsa
    if len(user_images[user_id]) >= 10:
        bot.reply_to(message, "Maksimal 10 ta rasm yuborishingiz mumkin! Endi /pdf buyrug'ini bering.")
        return

    # Rasmni yuklab olish
    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    
    # Faylni saqlash
    file_name = f"{user_id}_{len(user_images[user_id])}.jpg"
    with open(file_name, 'wb') as new_file:
        new_file.write(downloaded_file)
    
    user_images[user_id].append(file_name)
    bot.reply_to(message, f"Rasm qabul qilindi ({len(user_images[user_id])}/10). Yana yuborishingiz yoki /pdf deb yozishingiz mumkin.")

@bot.message_handler(commands=['pdf'])
def create_pdf(message):
    user_id = message.from_user.id
    if user_id not in user_images or not user_images[user_id]:
        bot.reply_to(message, "Siz hali rasm yubormadingiz! Avval rasm yuboring.")
        return

    bot.reply_to(message, "PDF fayl tayyorlanmoqda, biroz kuting...")
    
    try:
        image_list = user_images[user_id]
        pdf_path = f"{user_id}_output.pdf"
        
        # Rasmlarni ochish va PDF ga o'girish
        pil_images = [Image.open(img).convert('RGB') for img in image_list]
        
        # Birinchi rasmni asos qilib olib, qolganlarini qo'shamiz
        pil_images[0].save(pdf_path, save_all=True, append_images=pil_images[1:])
        
        # PDF ni foydalanuvchiga yuborish
        with open(pdf_path, 'rb') as pdf_file:
            bot.send_document(message.chat.id, pdf_file, caption="Mana sizning tayyor PDF faylingiz! 🎉")
            
        # Tozalash
        for img in image_list:
            if os.path.exists(img):
                os.remove(img)
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
            
        user_images[user_id] = []
        
    except Exception as e:
        bot.reply_to(message, f"Xatolik yuz berdi: {e}")

# Botni ishga tushirish
bot.infinity_polling()
