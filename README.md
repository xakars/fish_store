# fish_store

В проекте реализован рыбный магазин(MVP) в телеграмм боте. Управление продуктами происходит на стороне 
[elasticpath](https://www.elasticpath.com/)

Пример [демки](https://t.me/fish_store77_bot):


https://github.com/xakars/fish_store/assets/73193926/c3cb45fd-2cf8-451d-bb4d-8f78e242382f



### Как запустить

Для запуска сайта вам понадобится Python третьей версии.

Скачайте код с GitHub. Затем установите зависимости

```sh
pip install -r requirements.txt
```

Для развертывания проекта необходимо прописать переменные окружения в файле .env, такие как:
```
TELEGRAM_TOKEN={токен телеграм бота}
CLIENT_ID={client_id из elasticpath}
CLIENT_SECRET={client_secret из elasticpath}
PRICE_BOOK_ID={price_book из elasticpath}
```

После выполните следующию команду: 
```
python3 tg_bot.py
```
