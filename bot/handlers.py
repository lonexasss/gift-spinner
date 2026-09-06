import asyncio
import json
import random
import time

from aiogram import Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message

from . import config, db, subgram
from .i18n import _
from .keyboards import CASES, CASE_COMMON, cases_menu, lang_menu, main_menu, spin_menu, task_menu


async def start_handler(message: Message):
    uid = message.from_user.id
    name = message.from_user.first_name or "player"
    username = message.from_user.username or ""
    user = db.ensure_user(uid, name, username)
    text = _(user["lang"], "welcome", name=name, balance=user["balance_stars"])
    await message.answer(text, reply_markup=main_menu(user["lang"], config.WEBAPP_URL))


async def safe_edit(cb: CallbackQuery, text: str, markup=None):
    try:
        await cb.message.edit_text(text, reply_markup=markup)
    except Exception:
        try:
            await cb.answer()
        except Exception:
            pass


async def menu_handler(cb: CallbackQuery):
    action = cb.data.split(":")[1]
    user = db.get_user(cb.from_user.id) or db.ensure_user(cb.from_user.id)
    lang = user["lang"]
    name = cb.from_user.first_name or "player"

    if action == "main":
        text = _(lang, "welcome", name=name, balance=user["balance_stars"])
        markup = main_menu(lang, config.WEBAPP_URL)
    elif action in ("cases", "tasks"):
        text = _(lang, "choose_case")
        markup = cases_menu(lang)
    elif action == "balance":
        text = _(lang, "balance_msg", balance=user["balance_stars"],
                 opened=user["cases_opened"], tasks=user["tasks_done"])
        markup = main_menu(lang, config.WEBAPP_URL)
    elif action == "lang":
        text = _(lang, "lang_choose")
        markup = lang_menu()
    else:
        text = _(lang, "unknown")
        markup = main_menu(lang, config.WEBAPP_URL)

    await safe_edit(cb, text, markup)


async def task_start_handler(cb: CallbackQuery):
    uid = cb.from_user.id
    user = db.get_user(uid) or db.ensure_user(uid)
    lang = user["lang"]

    now = int(time.time())
    left = config.TASK_COOLDOWN_SECONDS - (now - user.get("last_task_at", 0))
    if user.get("last_task_at") and left > 0:
        await cb.answer(_(lang, "cooldown_task", sec=left), show_alert=True)
        return

    sponsors = await subgram.get_sponsors(uid, cb.message.chat.id)
    if not sponsors:
        await cb.answer(_(lang, "no_tasks_balance"), show_alert=True)
        return

    sponsor = random.choice(sponsors)
    link = sponsor.get("link", "")
    title = sponsor.get("title", "")
    await safe_edit(cb, _(lang, "task_start"), task_menu(lang))
    if link:
        await cb.message.answer(f"🔗 {title}: {link}")


async def task_check_handler(cb: CallbackQuery):
    uid = cb.from_user.id
    user = db.get_user(uid) or db.ensure_user(uid)
    lang = user["lang"]

    now = int(time.time())
    left = config.TASK_COOLDOWN_SECONDS - (now - user.get("last_task_at", 0))
    if user.get("last_task_at") and left > 0:
        await cb.answer(_(lang, "cooldown_task", sec=left), show_alert=True)
        return

    sponsors = await subgram.get_sponsors(uid, cb.message.chat.id)
    if not sponsors:
        await cb.answer(_(lang, "no_tasks_balance"), show_alert=True)
        return
    sponsor_ids = [s.get("id") for s in sponsors if s.get("id")]

    ok = await subgram.user_subscribed(uid, sponsor_ids)
    if not ok:
        await safe_edit(cb, _(lang, "not_subscribed"), task_menu(lang))
        return

    db.touch_last_task(uid)
    db.touch_last_case(uid)
    db.log_task(uid, sponsor_ids[0] if sponsor_ids else "demo", sponsors[0].get("title", ""))
    await safe_edit(cb, _(lang, "subscribed_ok"), spin_menu(lang))


async def spin_handler(cb: CallbackQuery):
    uid = cb.from_user.id
    user = db.get_user(uid) or db.ensure_user(uid)
    lang = user["lang"]
    now = int(time.time())
    left = config.OPEN_CASE_COOLDOWN_SECONDS - (now - user.get("last_case_at", 0))
    if user.get("last_case_at") and left > 0:
        await cb.answer(_(lang, "cooldown_case", sec=left), show_alert=True)
        return

    await cb.answer()

    for phrase in _(lang, "spinning"):
        await asyncio.sleep(0.4)
        try:
            await cb.message.edit_text(phrase)
        except Exception:
            pass

    await do_spin(uid, lang, lambda text, reply_markup=None: safe_edit(cb, text, reply_markup))


async def lang_handler(cb: CallbackQuery):
    code = cb.data.split(":")[1]
    db.set_lang(cb.from_user.id, code)
    await safe_edit(cb, _(code, "lang_changed", lang=code), main_menu(code, config.WEBAPP_URL))


async def webapp_message_handler(message: Message):
    """Данные из Mini App (WebApp.sendData)."""
    uid = message.from_user.id
    user = db.get_user(uid) or db.ensure_user(uid, message.from_user.first_name or "", message.from_user.username or "")
    lang = user["lang"]

    raw = message.web_app_data.data if message.web_app_data else ""
    try:
        payload = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        payload = {}

    action = payload.get("action", "")

    if action != "spin":
        await message.answer(_(lang, "unknown"))
        return

    now = int(time.time())
    left = config.OPEN_CASE_COOLDOWN_SECONDS - (now - user.get("last_case_at", 0))
    if user.get("last_case_at") and left > 0:
        await message.answer(_(lang, "cooldown_case", sec=left))
        return

    if not user.get("last_task_at"):
        await message.answer(
            _(
                lang,
                "task_start",
            ) + "\n\n⚠️ " + _(
                lang,
                "not_subscribed",
            )
        )
        return

    await do_spin(uid, lang, message.answer)


async def do_spin(uid: int, lang: str, reply):
    db.touch_last_case(uid)
    user = db.get_user(uid) or db.ensure_user(uid)
    stars = random.randint(config.STAR_MIN, config.STAR_MAX)
    db.log_case(uid, "", stars)
    balance = db.add_stars(uid, stars)
    opened = user["cases_opened"] + 1
    text = _(lang, "case_result", stars=stars, balance=balance, opened=opened)
    await reply(text, reply_markup=main_menu(lang, config.WEBAPP_URL))


def register(dp: Dispatcher):
    dp.message.register(start_handler, CommandStart())
    dp.message.register(webapp_message_handler, F.web_app_data)
    dp.callback_query.register(menu_handler, F.data.startswith("menu:"))
    dp.callback_query.register(spin_handler, F.data == "case:spin")
    dp.callback_query.register(task_start_handler, F.data.startswith("case:"))
    dp.callback_query.register(task_check_handler, F.data == "task:check")
    dp.callback_query.register(lang_handler, F.data.startswith("lang:"))