I18N = {
    "ru": {
        "welcome": (
            "🎰 Привет, {name}!\n\n"
            "Это крутилка подарков. Выполняй задания (подписки на каналы) — "
            "и крути кейсы с NFT и редкими подарками! Шанс редких — почти 0%, "
            "но звёзды из кейса падают всегда ⭐\n\n"
            "Баланс: {balance} ⭐"
        ),
        "menu": "Главное меню",
        "btn_cases": "🎁 Открыть кейс",
        "btn_balance": "💎 Мой баланс",
        "btn_tasks": "📋 Задания",
        "btn_lang": "🌐 Язык / Language",
        "choose_case": "🎰 Выбери кейс:",
        "case_common": "📦 Обычный кейс",
        "case_rare": "🔷 Редкий кейс",
        "case_legendary": "👑 Легендарный кейс",
        "case_desc": "{icon} {name}\nШанс редкого: почти 0%\nДроп: {min}-{max} ⭐",
        "no_tasks_balance": "Нет доступных заданий. Попробуй позже.",
        "task_start": (
            "📋 Чтобы открыть кейс — выполни 1 задание.\n\n"
            "1️⃣ Подпишись на канал ниже\n"
            "2️⃣ Вернись и нажми «Я подписался»"
        ),
        "btn_i_subscribed": "✅ Я подписался",
        "btn_back": "← Назад",
        "not_subscribed": (
            "❌ Подписка не подтверждена или ты уже был в этом канале ранее.\n"
            "Это бесполезно для рекламодателя, поэтому не засчитывается.\n\n"
            "Попробуй другой канал или нажми «Проверить» повторно."
        ),
        "btn_check": "🔄 Проверить снова",
        "subscribed_ok": (
            "✅ Задание выполнено! Кейс разблокирован.\n\n"
            "Жми «Крутить» и получай звёзды!"
        ),
        "btn_spin": "🎰 Крутить",
        "spinning": ["🎲 Крутим...", "🎡 Ещё крутим...", "🌀 Почти..."],
        "case_result": "🎁 Результат: +{stars} ⭐\n\nНовый баланс: {balance} ⭐\nОткрытий: {opened}",
        "cooldown_case": "⏳ Подожди {sec} сек перед следующим открытием.",
        "cooldown_task": "⏳ Подожди {sec} сек между заданиями.",
        "balance_msg": (
            "💎 Твой баланс: {balance} ⭐\n"
            "📦 Открыто кейсов: {opened}\n"
            "✅ Выполнено заданий: {tasks}"
        ),
        "lang_choose": "Выбери язык / Choose language:",
        "lang_changed": "Язык: {lang}",
        "unsub_soon": "🚨 Подписка пропала! Выполняй задания дальше.",
        "btn_refresh": "🔄 Проверить подписку",
        "unknown": "Не понял команду. Используй меню.",
    },
    "en": {
        "welcome": (
            "🎰 Hi, {name}!\n\n"
            "This is a gift spinner. Complete tasks (channel subscriptions) "
            "to spin cases with NFT and rare gifts! Rare chance ~0%, "
            "but stars always drop ⭐\n\n"
            "Balance: {balance} ⭐"
        ),
        "menu": "Main menu",
        "btn_cases": "🎁 Open case",
        "btn_balance": "💎 My balance",
        "btn_tasks": "📋 Tasks",
        "btn_lang": "🌐 Language",
        "choose_case": "🎰 Choose a case:",
        "case_common": "📦 Common case",
        "case_rare": "🔷 Rare case",
        "case_legendary": "👑 Legendary case",
        "case_desc": "{icon} {name}\nRare chance: ~0%\nDrop: {min}-{max} ⭐",
        "no_tasks_balance": "No tasks available. Try later.",
        "task_start": (
            "📋 To open a case — do 1 task.\n\n"
            "1️⃣ Subscribe to the channel below\n"
            "2️⃣ Come back and press 'I'm subscribed'"
        ),
        "btn_i_subscribed": "✅ I'm subscribed",
        "btn_back": "← Back",
        "not_subscribed": (
            "❌ Subscription not confirmed, or you were already in this channel.\n"
            "It gives nothing to the advertiser, so it doesn't count.\n\n"
            "Try another channel or press 'Check' again."
        ),
        "btn_check": "🔄 Check again",
        "subscribed_ok": (
            "✅ Task completed! Case unlocked.\n\n"
            "Press 'Spin' and get stars!"
        ),
        "btn_spin": "🎰 Spin",
        "spinning": ["🎲 Spinning...", "🎡 Still spinning...", "🌀 Almost..."],
        "case_result": "🎁 Result: +{stars} ⭐\n\nNew balance: {balance} ⭐\nOpens: {opened}",
        "cooldown_case": "⏳ Wait {sec} sec before the next open.",
        "cooldown_task": "⏳ Wait {sec} sec between tasks.",
        "balance_msg": (
            "💎 Your balance: {balance} ⭐\n"
            "📦 Cases opened: {opened}\n"
            "✅ Tasks done: {tasks}"
        ),
        "lang_choose": "Choose language / Выбери язык:",
        "lang_changed": "Language: {lang}",
        "unsub_soon": "🚨 Subscription lost! Keep doing tasks.",
        "btn_refresh": "🔄 Check subscription",
        "unknown": "Unknown command. Use the menu.",
    },
}


def _(lang: str, key: str, **kwargs):
    value = I18N.get(lang, I18N["ru"]).get(key, I18N["ru"].get(key, key))
    if isinstance(value, list):
        return value
    return value.format(**kwargs)


LANGS = {"ru": "🇷🇺 Русский", "en": "🇬🇧 English"}