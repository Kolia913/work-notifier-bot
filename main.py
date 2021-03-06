import config
import logging
import asyncio
from datetime import datetime

from aiogram import Bot, Dispatcher, executor, types
from sqlighter import SQLighter

from kwork_parser import KworkParser

logging.basicConfig(level=logging.INFO)

loop = asyncio.get_event_loop()
bot = Bot(token=config.API_TOKEN)
dp = Dispatcher(bot, loop=loop)

db = SQLighter('db.db')

kw = KworkParser('lastkey.txt')


# Команда активации подписки
@dp.message_handler(commands=['subscribe'])
async def subscribe(message: types.Message):
    if not db.subscriber_exists(message.from_user.id):
        # если юзера нет в базе, добавляем его
        db.add_subscriber(message.from_user.id)
    else:
        # если он уже есть, то просто обновляем ему статус подписки
        db.update_subscription(message.from_user.id, True)

    await message.answer(
        "Вы успешно подписались на рассылку!\nЖдите, скоро выйдут новые обзоры и вы узнаете о них первыми =)")


# Команда отписки
@dp.message_handler(commands=['unsubscribe'])
async def unsubscribe(message: types.Message):
    if not db.subscriber_exists(message.from_user.id):
        # если юзера нет в базе, добавляем его с неактивной подпиской (запоминаем)
        db.add_subscriber(message.from_user.id, False)
        await message.answer("Вы итак не подписаны.")
    else:
        # если он уже есть, то просто обновляем ему статус подписки
        db.update_subscription(message.from_user.id, False)
        await message.answer("Вы успешно отписаны от рассылки.")


# проверяем наличие новых игр и делаем рассылки
async def scheduled(wait_for):
    while True:
        await asyncio.sleep(wait_for)

        # проверяем наличие новых игр
        new_kwork = kw.new_kworks()

        if new_kwork:
            # парсим инфу о новой игре
            nfo = kw.kwork_info(new_kwork)

            # получаем список подписчиков бота
            subscriptions = db.get_subscriptions()

            # отправляем всем новость
            for s in subscriptions:
                try:
                    await bot.send_message(s[1],
                                           text=f"Название: {nfo['title']}; \n Описание: {nfo['desc']}; \n "
                                                f"{nfo['green_payment']}; \n {nfo['gray_payment']}; \n Ссылка: "
                                                f"{nfo['link']}")
                except Exception as e:
                    print(e)

            # обновляем ключ
            kw.update_lastkey(str(nfo['link']))


if __name__ == '__main__':
    dp.loop.create_task(scheduled(10))  # пока что оставим 10 секунд (в качестве теста)
    executor.start_polling(dp, skip_updates=True)
