import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.session.base import BaseSession
from aiogram.types import Chat, Message, Update, User

from bot import handlers

CALLS = []


class MockSession(BaseSession):
    async def close(self):
        pass

    async def make_request(self, bot, method, timeout=None):
        CALLS.append(("api", method, () , {}))
        return {"ok": True, "result": {}}

    async def stream_content(self, url, timeout=None, chunk_size=65536):
        raise NotImplementedError


class FakeBot(Bot):
    def __init__(self):
        super().__init__(token="123:TEST", session=MockSession())

    async def answer_callback_query(self, *args, **kwargs):
        CALLS.append(("answer", args, kwargs))


def _msg(chat_id=1, msg_id=10):
    chat = Chat(id=chat_id, type="private")
    return Message(message_id=msg_id, date=0, chat=chat, from_user=_user())


def _user(uid=42):
    return User(id=uid, is_bot=False, first_name="Tester")


def _update_cb(data: str, uid: int = 42, msg_id=10):
    cb = aiogram_cb(data, uid, msg_id)
    return Update(update_id=1, callback_query=cb)


def aiogram_cb(data, uid, msg_id):
    from aiogram.types import CallbackQuery

    return CallbackQuery(
        id=f"cb{msg_id}",
        from_user=_user(uid),
        chat_instance="ci",
        data=data,
        message=_msg(1, msg_id),
    )


def _update_msg(text: str):
    return Update(
        update_id=1,
        message=Message(
            message_id=1,
            date=0,
            chat=Chat(id=1, type="private"),
            from_user=_user(),
            text=text,
        ),
    )


def api_names() -> list[str]:
    return [type(m).__name__ for t, m, _, _ in CALLS]


def find_edit_with(sub: str) -> bool:
    for t, m, _, _ in CALLS:
        if t == "api" and type(m).__name__ == "EditMessageText" and sub in str(m):
            return True
    return False


async def main():
    import bot.config as config
    import bot.db as db

    config.TASK_COOLDOWN_SECONDS = 0
    config.OPEN_CASE_COOLDOWN_SECONDS = 0
    db.init_db()

    dp = Dispatcher()
    handlers.register(dp)
    bot = FakeBot()

    await dp.feed_update(bot, _update_msg("/start"))
    print("C0 /start:", api_names())
    assert "SendMessage" in api_names()

    CALLS.clear()
    await dp.feed_update(bot, _update_cb("menu:cases"))
    print("C1 cases:", api_names())
    assert find_edit_with("Choose a case") or find_edit_with("Выбери кейс")

    CALLS.clear()
    await dp.feed_update(bot, _update_cb("case:common"))
    print("C2 task start:", api_names())
    assert find_edit_with("Subscribe to the channel") or find_edit_with("Подпишись на канал")

    CALLS.clear()
    await dp.feed_update(bot, _update_cb("task:check"))
    print("C3 check:", api_names())
    assert find_edit_with("Task completed") or find_edit_with("Задание выполнено")

    CALLS.clear()
    await dp.feed_update(bot, _update_cb("case:spin"))
    print("C4 spin:", api_names())
    assert find_edit_with("Result") or find_edit_with("Результат")

    print("FLOW OK")


if __name__ == "__main__":
    asyncio.run(main())

async def main_alt():
    import bot.config as config
    import bot.db as db

    config.TASK_COOLDOWN_SECONDS = 0
    config.OPEN_CASE_COOLDOWN_SECONDS = 0
    db.init_db()

    dp = Dispatcher()
    handlers.register(dp)
    bot = FakeBot()

    # имитация webapp_msg: webapp_data со spin
    def _webapp_msg(payload: str):
        from aiogram.types import WebAppData
        wad = WebAppData(data=payload, button_text="test")
        return Update(
            update_id=5,
            message=Message(
                message_id=2, date=0, chat=Chat(id=1, type="private"),
                from_user=_user(), web_app_data=wad,
            ),
        )

    # Без задания спин запрещён
    await dp.feed_update(bot, _webapp_msg('{"action":"spin","init":"x"}'))
    texts = [str(m) for t, m, _, _ in CALLS if t == "api"]
    print("W1 without task:", "cooldown" in " ".join(texts) or "Задание" in " ".join(texts) or "Task" in " ".join(texts))

    # принудительно отмечаем задание выполненным
    with db.get_conn() as conn:
        conn.execute("UPDATE users SET last_task_at=? WHERE user_id=42", (int(__import__("time").time()),))

    CALLS.clear()
    await dp.feed_update(bot, _webapp_msg('{"action":"spin","init":"x"}'))
    texts = [str(m) for t, m, _, _ in CALLS if t == "api"]
    ok = any("Result" in s or "Результат" in s for s in texts)
    print("W2 spin:", ok)
    assert ok
    print("WEBAPP FLOW OK")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "alt":
        asyncio.run(main_alt())
    else:
        asyncio.run(main())
