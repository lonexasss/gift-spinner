# 🎰 Gift Case — Telegram Mini App + Bot

Telegram Mini App `Gift Case`: игрок выполняет задание (подписка на канал рекламодателя) → открывает кейс в **Mini App** (анимация, витрина с подарками) → награда на баланс.

**Заработок:** рекламодатель платит SubGram за уникальных подписчиков → платформа платит тебе → ты отдаёшь часть юзерам в виде звёзд. Твой доход = наценка.

## Архитектура

```
┌────────────────────────────────┐
│ Mini App (фронтенд)            │  /docs — HTML/CSS/JS, GitHub Pages (бесплатно)
│ кейсы, анимация, инвентарь     │  HTTPS от GitHub, аккаунт по email
└──────────┬─────────────────────┘
           │ WebApp.sendData → бот отвечает в чате
┌──────────▼─────────────────────┐
│ Бот-бэкенд (у тебя на ПК)      │  Python aiogram, SQLite
│ баланс, SubGram, анти-фарм     │  polling — публичный сервер не нужен
└────────────────────────────────┘
```

## Часть 1. Фронтенд Mini App → GitHub Pages (10 мин)

1. Заведи аккаунт на [GitHub](https://github.com) (email, документы не нужны).
2. Создай новый **public** репозиторий: `+ New repository` → имя например `gift-spinner` → Public → Create.
3. Залей файлы папки `docs/` (`index.html`, `style.css`, `app.js`): `Add file → Upload files`.
4. `Settings → Pages → Build and deployment → Source: Deploy from a branch` → Branch `main`, path `/docs` → Save.
5. Через ~1 мин сайт живёт: `https://<твой_юзер>.github.io/<repo>/` — это URL Mini App.
6. Проверь в браузере: должна открыться страница кейсов (можно играть без Telegram).

> Важно: в корне репозитория должен лежать пустой файл `.nojekyll` (иначе GitHub соберёт страницу из README через Jekyll).

## Часть 2. Бот-бэкенд (локально)

Требуется Python 3.10+.

```bash
cd gift-spinner-bot
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

В `.env` впиши:
- `BOT_TOKEN` — от **@BotFather** (`/newbot`)
- `WEBAPP_URL=https://<твой_юзер>.github.io/<repo>/` — из Части 1

Запуск:
```bash
python -m bot
```

В BotFather команда `/setdomain` → выбери бота → вставь тот же URL Mini App.

## Как играет игрок

1. `/start` → меню → «🎰 Открыть в приложении» → открывается Mini App.
2. В Mini App: выбирает кейс → «Открыть» → анимация → дроп звёзд (клиентский показ).
3. Через `WebApp.sendData` бот получает факт открытия → проверяет (выполнено ли задание, кулдаун) → зачисляет честные звёзды в БД → отвечает в чат «Результат: +N ⭐. Баланс M ⭐».
4. Задание (подписка на рекламодателя) выдаёт бот в чате: кнопка «🎁 Открыть кейс» в меню бота.

## Подключение реальных рекламодателей (SubGram)

1. Регистрация на [SubGram](https://subgram.org) (бесплатно), добавить бота → получить **Bot API Key**.
2. `.env`: `SUBGRAM_BOT_API_KEY=<ключ>`, `DEMO_MODE=0`.

Платят только за **уникальных** новых подписчиков по инвайт-ссылке.

## Конфиг (`.env`)

| Параметр | Назначение |
|---|---|
| `BOT_TOKEN` | Токен от BotFather |
| `WEBAPP_URL` | HTTPS-адрес Mini App |
| `DEMO_MODE` | `1` — демо, `0` — реальный SubGram |
| `SUBGRAM_BOT_API_KEY` | Ключ бота из SubGram |
| `ADMIN_IDS` | ID админов через запятую |
| `STAR_MIN`, `STAR_MAX` | Диапазон дропа |
| `TASK_COOLDOWN_SECONDS` | Пауза между заданиями |
| `OPEN_CASE_COOLDOWN_SECONDS` | Пауза между открытиями |

## Структура

```
docs/            # Mini App (хостится на GitHub Pages)
  index.html     # витрина кейсов, инвентарь
  style.css      # тёмная тема
  app.js         # Telegram.WebApp, анимация открытия, sendData
bot/
  __main__.py    # точка входа
  config.py      # конфиг из .env
  db.py          # SQLite (балансы, статистика, анти-фарм)
  subgram.py     # адаптер SubGram API + демо
  handlers.py    # логика бота + приём web_app_data
  keyboards.py   # кнопки (вкл. кнопку Mini App)
  i18n.py        # RU/EN
test_flow.py     # автотесты флоу (python test_flow.py)
```

## Тесты

```bash
python test_flow.py      # бот-флоу
python test_flow.py alt  # флоу Mini App (web_app_data)
```

## Честные ограничения

- **Вывод звёзд юзерам** — MVP на внутреннем балансе в БД. Реальный вывод Telegram Stars игрокам и синхронизация баланса внутри Mini App в реальном времени — второй этап (потребуется HTTP-API для Mini App).
- **ToS**: не продавай открытие кейсов за деньги/звёзды юзерам (станет гэмблом → бан). Открытие — только за выполненную подписку.
- **Продвижение** — главная задача после запуска: каналы «заработок», «раздачи», взаимопиар.