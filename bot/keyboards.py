from aiogram.types import WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder

from .i18n import LANGS

CASE_COMMON = "common"
CASE_RARE = "rare"
CASE_LEGEND = "legend"

CASES = {
    CASE_COMMON: {"icon": "📦", "min": 1, "max": 1, "weight": 70},
    CASE_RARE: {"icon": "🔷", "min": 1, "max": 2, "weight": 25},
    CASE_LEGEND: {"icon": "👑", "min": 2, "max": 3, "weight": 5},
}


def _label(lang: str, *, btn_cases="", btn_tasks="", btn_balance="", btn_lang="",
           case_common="", case_rare="", case_legend="", btn_back="", btn_i_subscribed="",
           btn_check="", btn_spin=""):
    from .i18n import _

    return {
        "cases": btn_cases or _(lang, "btn_cases"),
        "tasks": btn_tasks or _(lang, "btn_tasks"),
        "balance": btn_balance or _(lang, "btn_balance"),
        "lang": btn_lang or _(lang, "btn_lang"),
        "common": case_common or _(lang, "case_common"),
        "rare": case_rare or _(lang, "case_rare"),
        "legend": case_legend or _(lang, "case_legend"),
        "back": btn_back or _(lang, "btn_back"),
        "subscribed": btn_i_subscribed or _(lang, "btn_i_subscribed"),
        "check": btn_check or _(lang, "btn_check"),
        "spin": btn_spin or _(lang, "btn_spin"),
    }


def main_menu(lang: str, webapp_url: str = ""):
    kb = InlineKeyboardBuilder()
    l = _label(lang)
    kb.button(text=l["cases"], callback_data="menu:cases")
    kb.button(text=l["tasks"], callback_data="menu:tasks")
    kb.button(text=l["balance"], callback_data="menu:balance")
    kb.button(text=l["lang"], callback_data="menu:lang")
    kb.adjust(2)
    if webapp_url:
        kb.row()
        kb.button(text="🎰 Открыть в приложении", web_app=WebAppInfo(url=webapp_url))
    return kb.as_markup()


def cases_menu(lang: str):
    kb = InlineKeyboardBuilder()
    l = _label(lang)
    for key, case in CASES.items():
        kb.button(text=f"{case['icon']} {l[key]}", callback_data=f"case:{key}")
    kb.button(text=l["back"], callback_data="menu:main")
    kb.adjust(1)
    return kb.as_markup()


def task_menu(lang: str):
    kb = InlineKeyboardBuilder()
    l = _label(lang)
    kb.button(text=l["subscribed"], callback_data="task:check")
    kb.button(text=l["back"], callback_data="menu:cases")
    kb.adjust(1)
    return kb.as_markup()


def spin_menu(lang: str):
    kb = InlineKeyboardBuilder()
    l = _label(lang)
    kb.button(text=l["spin"], callback_data="case:spin")
    kb.button(text=l["back"], callback_data="menu:main")
    kb.adjust(1)
    return kb.as_markup()


def lang_menu():
    kb = InlineKeyboardBuilder()
    for code, label in LANGS.items():
        kb.button(text=label, callback_data=f"lang:{code}")
    kb.button(text="←", callback_data="menu:main")
    kb.adjust(1)
    return kb.as_markup()