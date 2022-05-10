from rembg.bg import remove
from PIL import Image, ImageFile
from pathlib import Path
import data
import telebot
import locale
import os
import glob
import zipfile


ImageFile.LOAD_TRUNCATED_IMAGES = True
bot = telebot.TeleBot(data.Ttoken)
locale.setlocale(locale.LC_ALL, "")


@bot.message_handler(commands=['clear'])
def clearBackground(message):
    if not os.listdir(Path("download/" + str(message.chat.id) + "/input")):
        bot.reply_to(message, "Ви поки не надіслали жодних файлів для обробки!")
    else:
        try:
            count = 0
            folder = Path("download/" + str(message.chat.id) + "/input")
            count_files = len(list(folder.rglob("*")))

            messagetoedit = bot.send_message(message.from_user.id, "Обробка запущена! Готово [" + str(count) + "/" + str(count_files) + "]!")

            for name in glob.glob("download/" + str(message.chat.id) + "/input" + "/*"):
                input = Image.open(name)
                output = remove(input)
                output.save("download/" + str(message.chat.id) + "/output/" + str(count) + ".png")

                count = count + 1
                bot.edit_message_text(chat_id=message.chat.id, message_id=messagetoedit.message_id, text="Обробка запущена! Готово [" + str(count) + "/" + str(count_files) + "]!")

            bot.send_message(message.from_user.id, "Всі файли успішно оброблено!\n"
                                                   "Тепер можете завантажити їх архівом /getfile")
        except Exception as e:
            bot.reply_to(message, e)


@bot.message_handler(commands=['delinput'])
def deleteInputFile(message):
    try:
        for file in glob.glob("download/" + str(message.chat.id) + "/input/*"):
            os.remove(file)
        bot.send_message(message.from_user.id, "Всі надіслані файли успішно видалено!")
    except OSError as e:
        print(e)


@bot.message_handler(commands=['deloutput'])
def deleteOutputFile(message):
    try:
        for file in glob.glob("download/" + str(message.chat.id) + "/output/*"):
            os.remove(file)
        bot.send_message(message.from_user.id, "Всі оброблені файли успішно видалено!")
    except OSError as e:
        print(e)


@bot.message_handler(commands=['getfile'])
def sendUserFile(message):
    if not os.listdir(Path("download/" + str(message.chat.id) + "/output")):
        bot.reply_to(message, "Поки немає оброблених фото!")
    else:
        bot.send_message(message.from_user.id, "Запущена архівація файлів...")
        try:
            z = zipfile.ZipFile("readyPhoto.zip", 'w')  # Создание нового архива
            ready_folder = "download/" + str(message.chat.id) + "/output"
            for root, dirs, files in os.walk(ready_folder):  # Список всех файлов и папок в директории folder
                for file in files:
                    z.write(os.path.join(root, file))  # Создание относительных путей и запись файлов в архив

            z.close()

            bot.send_document(message.from_user.id, open("readyPhoto.zip", 'rb'))

        except Exception as e:
            bot.reply_to(message, e)


@bot.message_handler(content_types=['document'])
def getUserFile(message):
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        os.makedirs('download/{}'.format(str(message.chat.id)), exist_ok=True)
        os.makedirs('download/' + str(message.chat.id) + '/{}'.format("input"), exist_ok=True)
        os.makedirs('download/' + str(message.chat.id) + '/{}'.format("output"), exist_ok=True)

        src = 'download/' + str(message.chat.id) + "/input/" + message.document.file_name
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)

        bot.reply_to(message, "Фото успішно завантажене на диск!")

    except Exception as e:
        bot.reply_to(message, e)


if __name__ == '__main__':
        bot.infinity_polling()

