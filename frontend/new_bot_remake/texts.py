# texts.py
# Файл со всеми текстами бота для поддержки мультиязычности (RU/EN)

TEXTS = {
    'ru': {
        # ===== СТАРТОВЫЙ ТЕКСТ (/start) =====
        'welcome': """Добро пожаловать в ChatGPT от LudiceTeam!

Наш бот помогает быстро и удобно получать ответы на любые вопросы. Вы можете задавать текстовые запросы — и бот предоставит понятные и точные ответы.

Но что ещё удобнее — не обязательно вручную вводить текст! Просто отправьте картинку с нужным текстом или задачей, а наш бот самостоятельно её «прочитает», распознает и решит за вас.

Используйте нашего бота для учебы, работы и повседневных задач — он сэкономит ваше время и сделает процесс проще!""",
        
        'welcome_referral': "🎉 Вы зашли по ссылке друга!",
        
        # ===== ПРОФИЛЬ (/profile) =====
        'profile_sub_expired': """📅 Ваша подписка закончилась.

🔓 Чтобы продолжить пользоваться платным функционалом, вам нужно оформить её снова.

🆓 Вы можете пользоваться ботом в пределах бесплатного тарифа.

Благодарим за поддержку!""",
        
        'profile_ref_bonus': """✅ Basic подписка получена!
✅ Награда за 5 приглашённых друзей
✅ Активна 30 дней""",
        
        'profile_template': """
Профиль @{username}:
        
Запросов осталось: {requests_left}

Запросы к Nano Banana: {nano_requests}

Статус подписки: {subscription_status}

Срок истечения подписки: {subscription_end}
""",
        
        # ===== СТАТУСЫ ПОДПИСКИ =====
        'subscription_premium': "Premium (Безлимитная)",
        'subscription_basic': "Basic (25 запросов в день)",
        'subscription_none': "Не активирована",
        
        # ===== ТЕКСТЫ ДЛЯ ЗАПРОСОВ =====
        'requests_unlimited': "∞ (безлимит)",
        'requests_basic': "/25",
        'requests_free': "/20",
        
        # ===== NANO BANANA ЗАПРОСЫ =====
        'nano_premium': "/15",
        'nano_basic': "/10",
        'nano_free': "/5",
        
        # ===== РЕФЕРАЛЬНАЯ ПРОГРАММА (/referal) =====
        'referral_program': """📢 **РЕФЕРАЛЬНАЯ ПРОГРАММА**

🎁 Приглашайте друзей и получайте бонусы!

🔗 **Ваша реферальная ссылка:**
https://t.me/character_ai_ludice_team_bot?start={user_id}

👥 **Приглашено друзей:** {count}

🏆 **Ваши бонусы за приглашения:**

✅ **За каждого друга:** +5 запросов к нейросети
✅ **Первые 5 друзей:** Подписка Basic на 1 месяц!

💡 **Как это работает:**
1. Отправьте другу вашу реферальную ссылку
2. Друг переходит и начинает пользоваться ботом
3. Вы автоматически получаете бонусы!

🚀 **Начните приглашать прямо сейчас!**""",
        
        # ===== ПОДПИСКИ (/pay) =====
        'subscription_info': """Возможности подписок: 

Basic:
Gemini 3 Flash, 
Gemini 2.5 Flash, 
Deepseek, 
Mistral Large, 
Claude Opus 4.6, 
Claude Sonnet 4.6, 
GPT-4, 
GPT-4 Turbo - 25 запросов/день

Nano Banana - 5 запросов/день

Premium: безлимитный доступ к любой нейросети, кроме Nano Banana (15 запросов/день)""",
        
        # ===== ПОКУПКА ПОДПИСКИ =====
        'buy_premium': "1) Стоимость: 499 звезд / 30 дней. \n\n Бонус: любая следующая покупка в боте будет со скидкой 10%",
        'buy_premium_with_sale': "1) Стоимость: 449 звезд / 30 дней. \n\n Бонус: любая следующая покупка в боте будет со скидкой 10%",
        'buy_basic': "1) Стоимость: 199 звезд / 30 дней",
        'buy_requests_info': "Данная покупка предоставляет только фиксированное количество запросов без каких-либо дополнительных привилегий, гарантий приоритета или влияния на обработку запросов.",
        
        # ===== УСПЕШНЫЕ ПОКУПКИ =====
        'purchase_premium_success': "✅ Вы успешно подписались на Premium подписку. Спасибо за покупку. Приятного пользования.",
        'purchase_basic_success': "✅ Вы успешно подписались на Basic. Спасибо за покупку. Приятного пользования.",
        'purchase_requests_success': "✅ Вы купили запросов. Спасибо за покупку. Приятного пользования.",
        'purchase_error': "Что то пошло не так. Попробуйте снова.",
        
        # ===== HELP (/help) =====
        'help': """🎯Основные разделы (главное меню):

Чат — начать общение со мной. Здесь я помогаю с текстами презентаций, переводом, разбором параграфов и любыми вашими вопросами.

Профиль — информация о вашем аккаунте. Здесь можно посмотреть оставшееся количество запросов на день.

Сбросить контекст — очистить историю нашего диалога.

Помощь — это сообщение с описанием возможностей бота (данное сообщение).

Поддержка — связь с разработчиком, если что-то работает не так.

👤Профиль:
В этом разделе вы можете контролировать свою активность:

Узнать свой статус.

Проверить лимит доступных запросов.

💡Советы:

Старайтесь формулировать запрос четко и как можно подробнее — так результат будет точнее.""",
        
        # ===== SUPPORT (/support) =====
        'support': "Отправьте ваш вопрос вот этому пользователю : @kksndid_support",
        
        # ===== RESET (/reset) =====
        'reset_success': "✅ История отчищена.",
        
        # ===== ВЫБОР МОДЕЛИ (/ai_mode) =====
        'ai_mode': """🤖 **Выберите AI модель**

**Google: Gemini 3 Flash**
⚡ Быстрая модель от Google

**Google: Gemini 2.5 Flash**
⚡ Сбалансированная модель от Google

**OpenAI: GPT-4**
🤖 Мощная модель от OpenAI

**OpenAI: GPT-4 Turbo**
🤖 Ускоренная версия GPT-4

**Anthropic: Claude Opus 4.6**
👑 Флагманская модель Claude

**Anthropic: Claude Sonnet 4.6**
📝 Стандартная модель Claude

**Mistral: Mistral Large**
🌀 Европейская языковая модель

**DeepSeek: DeepSeek Chat**
🧠 Китайская языковая модель

**Nano Banana: Banana Gen**
🍌 Генерация реалистичных изображений""",
        
        # ===== ОТВЕТЫ НА СООБЩЕНИЯ =====
        'thinking': "Думаю...",
        'no_requests_nano': "У вас не осталось запросов к Nano Banana.",
        'no_requests_basic': "У вас на сегодня закончились запросы. Попробуйте завтра",
        'no_requests_free': "У вас не осталось бесплатных запросов. Купить подписку вы можете по команде /pay",
        'nano_wrong_model': "Ваш запрос не подходит для данной модели. Измените запрос или выберите другую модель.",
        'empty_photo_text': "Текст с фотографии не извлечен",
        
        # ===== АДМИН-КОМАНДЫ =====
        'admin_gsp_usage': "Укажите ID! Пример: /gsp 12345",
        'admin_gsp_success': "✅ Подписка выдана",
        'admin_gsp_user_not_found': "Пользователь не найден",
        
        'admin_rms_usage': "Укажите ID! Пример: /rms 12345",
        'admin_rms_success': "✅ Подписка отобрана",
        
        # ===== РАБОТА С ФАЙЛАМИ =====
        'file_too_big': """❌ Файл слишком большой!
📁 Размер: 20MB
⚠️ Максимум: 20MB
💡 Попробуй сжать файл или отправь часть""",
        
        'file_format_unsupported': "Формат файла не поддерживается",
        'file_text_not_extracted': "Текст с файла не был извлечен",
        
        # ===== ОЧЕРЕДЬ =====
        'queue_overflow': "🔄 Очередь переполнена",
        'queue_timeout': "⏱️ Превышено время ожидания",
        
        # ===== ОТВЕТ GEMINI =====
        'gemini_empty': "🤔 Gemini вернул пустой ответ.",
        'gemini_no_image': "🤔 Нет изображения в ответе.",
        'gemini_error': "❌ Ошибка",
        
    
        
        # ===== НАЗВАНИЯ МОДЕЛЕЙ ДЛЯ КНОПОК =====
        'model_gemini_3_flash': "Gemini 3 Flash",
        'model_gemini_25_flash': "Gemini 2.5 Flash",
        'model_gpt4': "GPT-4",
        'model_gpt4_turbo': "GPT-4 Turbo",
        'model_claude_opus': "Claude Opus",
        'model_claude_sonnet': "Claude Sonnet",
        'model_mistral': "Mistral Large",
        'model_deepseek': "DeepSeek Chat",
        'model_nano_banana': "Nano Banana",
        'model_selected': "✅ ",
    },
    
    'en': {
        # ===== START TEXT (/start) =====
        'welcome': """Welcome to ChatGPT from LudiceTeam!

Our bot helps you quickly and conveniently get answers to any questions. You can ask text queries — and the bot will provide clear and accurate answers.

But what's even more convenient — you don't have to type manually! Just send a picture with the desired text or task, and our bot will independently "read" it, recognize it, and solve it for you.

Use our bot for studying, work, and everyday tasks — it will save your time and make the process easier!""",
        
        'welcome_referral': "🎉 You came through a friend's link!",
        
        # ===== PROFILE (/profile) =====
        'profile_sub_expired': """📅 Your subscription has expired.

🔓 To continue using paid features, you need to renew it.

🆓 You can use the bot within the free plan.

Thank you for your support!""",
        
        'profile_ref_bonus': """✅ Basic subscription received!
✅ Reward for 5 invited friends
✅ Active for 30 days""",
        
        'profile_template': """
Profile @{username}:
        
Requests left: {requests_left}

Nano Banana requests: {nano_requests}

Subscription status: {subscription_status}

Subscription expires: {subscription_end}
""",
        
        # ===== SUBSCRIPTION STATUSES =====
        'subscription_premium': "Premium (Unlimited)",
        'subscription_basic': "Basic (25 requests/day)",
        'subscription_none': "Not activated",
        
        # ===== REQUEST TEXTS =====
        'requests_unlimited': "∞ (unlimited)",
        'requests_basic': "/25",
        'requests_free': "/20",
        
        # ===== NANO BANANA REQUESTS =====
        'nano_premium': "/15",
        'nano_basic': "/10",
        'nano_free': "/5",
        
        # ===== REFERRAL PROGRAM (/referal) =====
        'referral_program': """📢 **REFERRAL PROGRAM**

🎁 Invite friends and get bonuses!

🔗 **Your referral link:**
https://t.me/character_ai_ludice_team_bot?start={user_id}

👥 **Friends invited:** {count}

🏆 **Your bonuses for invites:**

✅ **For each friend:** +5 requests to the neural network
✅ **First 5 friends:** Basic subscription for 1 month!

💡 **How it works:**
1. Send your referral link to a friend
2. Friend clicks and starts using the bot
3. You automatically receive bonuses!

🚀 **Start inviting right now!**""",
        
        # ===== SUBSCRIPTIONS (/pay) =====
        'subscription_info': """Subscription features: 

Basic:
Gemini 3 Flash, 
Gemini 2.5 Flash, 
Deepseek, 
Mistral Large, 
Claude Opus 4.6, 
Claude Sonnet 4.6, 
GPT-4, 
GPT-4 Turbo - 25 requests/day

Nano Banana - 5 requests/day

Premium: unlimited access to any neural network, except Nano Banana (15 requests/day)""",
        
        # ===== BUY SUBSCRIPTION =====
        'buy_premium': "1) Price: 499 stars / 30 days. \n\n Bonus: any next purchase in the bot will have a 10% discount",
        'buy_premium_with_sale': "1) Price: 449 stars / 30 days. \n\n Bonus: any next purchase in the bot will have a 10% discount",
        'buy_basic': "1) Price: 199 stars / 30 days",
        'buy_requests_info': "This purchase only provides a fixed number of requests without any additional privileges, priority guarantees, or impact on request processing.",
        
        # ===== SUCCESSFUL PURCHASES =====
        'purchase_premium_success': "✅ You have successfully subscribed to Premium. Thank you for your purchase. Enjoy!",
        'purchase_basic_success': "✅ You have successfully subscribed to Basic. Thank you for your purchase. Enjoy!",
        'purchase_requests_success': "✅ You bought requests. Thank you for your purchase. Enjoy!",
        'purchase_error': "Something went wrong. Please try again.",
        
        # ===== HELP (/help) =====
        'help': """🎯Main sections (main menu):

Chat — start communicating with me. Here I help with presentation texts, translation, paragraph analysis, and any of your questions.

Profile — information about your account. Here you can see the remaining number of requests for the day.

Reset context — clear our conversation history.

Help — this message with a description of the bot's features (this message).

Support — contact the developer if something isn't working.

👤Profile:
In this section you can control your activity:

Check your status.

Check your available request limit.

💡Tips:

Try to formulate your query clearly and in as much detail as possible — the result will be more accurate.""",
        
        # ===== SUPPORT (/support) =====
        'support': "Send your question to this user: @kksndid_support",
        
        # ===== RESET (/reset) =====
        'reset_success': "✅ History cleared.",
        
        # ===== MODEL SELECTION (/ai_mode) =====
        'ai_mode': """🤖 **Choose AI Model**

**Google: Gemini 3 Flash**
⚡ Fast model from Google

**Google: Gemini 2.5 Flash**
⚡ Balanced model from Google

**OpenAI: GPT-4**
🤖 Powerful model from OpenAI

**OpenAI: GPT-4 Turbo**
🤖 Accelerated version of GPT-4

**Anthropic: Claude Opus 4.6**
👑 Claude's flagship model

**Anthropic: Claude Sonnet 4.6**
📝 Claude's standard model

**Mistral: Mistral Large**
🌀 European language model

**DeepSeek: DeepSeek Chat**
🧠 Chinese language model

**Nano Banana: Banana Gen**
🍌 Realistic image generation""",
        
        # ===== RESPONSES TO MESSAGES =====
        'thinking': "Thinking...",
        'no_requests_nano': "You have no requests left for Nano Banana.",
        'no_requests_basic': "You've run out of requests for today. Try tomorrow",
        'no_requests_free': "You have no free requests left. You can buy a subscription with the /pay command",
        'nano_wrong_model': "Your request is not suitable for this model. Change your request or choose another model.",
        'empty_photo_text': "Text not extracted from photo",
        
        # ===== ADMIN COMMANDS =====
        'admin_gsp_usage': "Specify ID! Example: /gsp 12345",
        'admin_gsp_success': "✅ Subscription granted",
        'admin_gsp_user_not_found': "User not found",
        
        'admin_rms_usage': "Specify ID! Example: /rms 12345",
        'admin_rms_success': "✅ Subscription removed",
        
        # ===== FILE HANDLING =====
        'file_too_big': """❌ File too big!
📁 Size: 20MB
⚠️ Maximum: 20MB
💡 Try compressing the file or send part of it""",
        
        'file_format_unsupported': "File format not supported",
        'file_text_not_extracted': "Text could not be extracted from file",
        
        # ===== QUEUE =====
        'queue_overflow': "🔄 Queue is full",
        'queue_timeout': "⏱️ Timeout exceeded",
        
        # ===== GEMINI RESPONSE =====
        'gemini_empty': "🤔 Gemini returned an empty response.",
        'gemini_no_image': "🤔 No image in response.",
        'gemini_error': "❌ Error",
        
        
        # ===== MODEL NAMES FOR BUTTONS =====
        'model_gemini_3_flash': "Gemini 3 Flash",
        'model_gemini_25_flash': "Gemini 2.5 Flash",
        'model_gpt4': "GPT-4",
        'model_gpt4_turbo': "GPT-4 Turbo",
        'model_claude_opus': "Claude Opus",
        'model_claude_sonnet': "Claude Sonnet",
        'model_mistral': "Mistral Large",
        'model_deepseek': "DeepSeek Chat",
        'model_nano_banana': "Nano Banana",
        'model_selected': "✅ ",
    }
}