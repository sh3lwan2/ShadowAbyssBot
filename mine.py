import logging
import telebot
import json
import os
import time
import random
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# إعداد التسجيل
logging.basicConfig(filename="log.txt", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
error_handler = logging.FileHandler("errors.txt")
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logging.getLogger().addHandler(error_handler)

# جلب التوكن
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    print("❌ خطأ: لم يتم العثور على التوكن!")
    exit()

# إنشاء البوت
bot = telebot.TeleBot(TOKEN)
logging.info("⚫ هاوية الظلال تُشعل… مرحبًا بالكيان الأسمى!")

# تحديد الـ Admin ID وقناة التيليجرام
ADMIN_ID = "7920989999"  # غيريه لـ ID بتاعك
CHANNEL_USERNAME = "@UNKNOWN_404X"

# ملف JSON لحفظ البيانات
BOT_FILE = "bots.json"
if not os.path.exists(BOT_FILE):
    initial_data = {
        "users": {},
        "verified": [],
        "stats": {},
        "invites": {},
        "last_message": {},
        "total_users": 0,
        "user_list": [],
        "language": {},
        "banned_users": [],
        "tasks": [],
        "shop": [],
        "ranks": {
            "رماد الظلال": [0, 50],
            "حارس الهاوية": [51, 100],
            "سيف الظلام": [101, 200],
            "شبح الليل": [201, 350],
            "سيد الظلال": [351, 500],
            "ملك الهاوية": [501, 750],
            "إمبراطور الظلام": [751, 1000],
            "أسطورة الظلال": [1001, float("inf")]
        },
        "complaints": [],
        "allow_duplicates": False
    }
    with open(BOT_FILE, "w") as f:
        json.dump(initial_data, f)

# التحقق من الاشتراك
def check_channel_membership(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        logging.error(f"خطأ في فحص الاشتراك: {e}")
        return False

# حذف الرسالة السابقة
def delete_previous_message(chat_id, user_id):
    try:
        with open(BOT_FILE, "r") as f:
            data = json.load(f)
        last_msg = data["last_message"].get(str(user_id))
        if last_msg:
            bot.delete_message(chat_id, last_msg)
    except Exception as e:
        logging.warning(f"فشل حذف الرسالة القديمة: {e}")

# إشعارات عشوائية
random_notifications = [
    "⚫ اختيارك أيقظ الظلال!",
    "🌑 الهاوية تراقب خطواتك.",
    "⚔️ سلاحك جاهز للمعركة!",
    "💨 الظلام يتبعك الآن.",
    "🔳 نقطة جديدة في الهاوية!",
    "🌙 ليلك أصبح أقوى!",
    "⬛ الظلال تنتظر أمرك.",
    "✨ خطوة نحو الأسطورة!",
    "⚫ الهاوية تحتضنك!",
    "🔳 قوتك تزداد!"
]

# النصوص بلغتين
messages = {
    "welcome": {"ar": "⚫ مرحبًا بك في هاوية الظلال! اختر أداتك!", "en": "⚫ Welcome to the Abyss of Shadows! Choose your tool!"},
    "subscribe": {"ar": f"⚫ اشترك في {CHANNEL_USERNAME} أولاً!", "en": f"⚫ Subscribe to {CHANNEL_USERNAME} first!"},
    "my_stats": {"ar": "⚫ نقاطك: {points}\n🌑 رتبتك: {rank}", "en": "⚫ Your Points: {points}\n🌑 Rank: {rank}"},
    "my_profile": {"ar": "⚫ ملفك:\n🔻 @{username}\n🌑 رتبتك: {rank}\n⚫ نقاطك: {points}\n💨 إحالاتك: {invites}", "en": "⚫ Profile:\n🔻 @{username}\n🌑 Rank: {rank}\n⚫ Points: {points}\n💨 Referrals: {invites}"},
    "add_bot_prompt": {"ar": "⚫ أضف بوت:\nأرسل اللينك + الوصف (مثال: t.me/bot - بوت سحب)", "en": "⚫ Add Bot:\nSend link + description (e.g., t.me/bot - Withdrawal bot)"},
    "add_bot_success": {"ar": "⚫ تمت الإضافة… في انتظار المراجعة!", "en": "⚫ Added… awaiting review!"},
    "add_bot_error": {"ar": "⚫ خطأ في الصيغة!", "en": "⚫ Format error!"},
    "my_bots": {"ar": "⚫ بوتاتك:", "en": "⚫ Your Bots:"},
    "my_bots_empty": {"ar": "🌑 مكتبتك خاوية!", "en": "🌑 Your library is empty!"},
    "edit_bot_prompt": {"ar": "⚫ تعديل بوت:\nأرسل الرقم + التعديل (مثال: 1 - t.me/newbot - جديد)", "en": "⚫ Edit Bot:\nSend number + edit (e.g., 1 - t.me/newbot - New)"},
    "edit_bot_success": {"ar": "⚔️ تم التعديل!", "en": "⚔️ Edited!"},
    "edit_bot_error": {"ar": "⚫ خطأ في الرقم أو الصيغة!", "en": "⚫ Number or format error!"},
    "delete_bot_prompt": {"ar": "⚫ حذف بوت:\nأرسل الرقم (مثال: 1)", "en": "⚫ Delete Bot:\nSend number (e.g., 1)"},
    "delete_bot_success": {"ar": "💨 تم الحذف!", "en": "💨 Deleted!"},
    "delete_bot_error": {"ar": "⚫ خطأ في الرقم!", "en": "⚫ Number error!"},
    "verified_bots": {"ar": "⚫ البوتات المعتمدة:", "en": "⚫ Verified Bots:"},
    "verified_bots_empty": {"ar": "🌑 لا بوتات معتمدة!", "en": "🌑 No verified bots!"},
    "invite_friends": {"ar": "⚫ انشر الظلال:\nرابطك: {invite_link}\n💨 1 نقطة لكل إحالة!", "en": "⚫ Spread the Shadows:\nYour link: {invite_link}\n💨 1 point per referral!"},
    "tasks": {"ar": "⚫ المهام:\n{tasks_list}", "en": "⚫ Tasks:\n{tasks_list}"},
    "tasks_empty": {"ar": "🌑 لا مهام حاليًا!", "en": "🌑 No tasks currently!"},
    "shop": {"ar": "⚫ المتجر:\n{shop_list}", "en": "⚫ Shop:\n{shop_list}"},
    "shop_empty": {"ar": "🌑 المتجر خالٍ!", "en": "🌑 Shop is empty!"},
    "shop_purchase": {"ar": "⚫ تم الشراء: {item}!", "en": "⚫ Purchased: {item}!"},
    "shop_insufficient": {"ar": "⚫ نقاطك غير كافية!", "en": "⚫ Insufficient points!"},
    "stats": {"ar": "⚫ إحصائيات:\n🔻 العدد الكلي: {total_users}\n⚫ سيوف الظلال:\n{top_12}\n🌑 الرتب الأدنى:\n{next_8}", "en": "⚫ Stats:\n🔻 Total Users: {total_users}\n⚫ Swords of Shadows:\n{top_12}\n🌑 Lower Ranks:\n{next_8}"},
    "stats_empty": {"ar": "🌑 لا مستخدمين بعد!", "en": "🌑 No users yet!"},
    "referral_self": {"ar": "⚫ لا يمكنك خداع الظلال!", "en": "⚫ You can’t trick the shadows!"},
    "referral_notification": {"ar": "💨 تابع جديد تحت ظلالك… +1 نقطة!", "en": "💨 New follower under your shadows… +1 point!"},
    "admin_panel": {"ar": "⚫ لوحة التحكم:", "en": "⚫ Admin Panel:"},
    "bot_not_trusted": {"ar": "⚫ بوتك مش موثوق، ننصحك تحذفه!", "en": "⚫ Your bot isn’t trusted, we suggest deleting it!"},
    "bot_approved": {"ar": "⚫ تم اعتماد بوتك في المكتبة العامة! +5 نقاط", "en": "⚫ Your bot was approved in the public library! +5 points"},
    "complaint_received": {"ar": "⚫ تم تسجيل شكواك!", "en": "⚫ Your complaint has been recorded!"}
}

# القايمة الرئيسية
def main_menu(chat_id, user_id):
    delete_previous_message(chat_id, user_id)
    with open(BOT_FILE, "r") as f:
        data = json.load(f)
    lang = data["language"].get(str(user_id), "ar")
    text = messages["welcome"][lang]
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("⚫ ملفك" if lang == "ar" else "⚫ Profile", callback_data="my_profile"),
               InlineKeyboardButton("⚫ نقاطك" if lang == "ar" else "⚫ Points", callback_data="my_stats"))
    markup.add(InlineKeyboardButton("⚫ المكتبة" if lang == "ar" else "⚫ Library", callback_data="library"),
               InlineKeyboardButton("⚫ المهام" if lang == "ar" else "⚫ Tasks", callback_data="tasks"))
    markup.add(InlineKeyboardButton("⚫ المتجر" if lang == "ar" else "⚫ Shop", callback_data="shop"),
               InlineKeyboardButton("⚫ الإحصائيات" if lang == "ar" else "⚫ Stats", callback_data="stats"))
    markup.add(InlineKeyboardButton("🌑 تعريف" if lang == "ar" else "🌑 About", callback_data="about"),
               InlineKeyboardButton("💨 شكوى" if lang == "ar" else "💨 Complaint", callback_data="complaint"))
    if str(user_id) == ADMIN_ID:
        markup.add(InlineKeyboardButton("⚔️ لوحة التحكم" if lang == "ar" else "⚔️ Admin Panel", callback_data="admin_panel"))
    msg = bot.send_message(chat_id, text, reply_markup=markup)
    data["last_message"][str(user_id)] = msg.message_id
    with open(BOT_FILE, "w") as f:
        json.dump(data, f)

# أمر /start
@bot.message_handler(commands=['start'])
def command_start(message):
    user_id = str(message.from_user.id)
    chat_id = message.chat.id
    delete_previous_message(chat_id, user_id)

    with open(BOT_FILE, "r") as f:
        data = json.load(f)
    lang = data["language"].get(user_id, "ar")

    if user_id in data["banned_users"]:
        bot.send_message(chat_id, "⚫ أنت محظور من استخدام الهاوية!")
        return

    if not check_channel_membership(user_id):
        text = messages["subscribe"][lang]
        msg = bot.send_message(chat_id, text)
        data["last_message"][user_id] = msg.message_id
        with open(BOT_FILE, "w") as f:
            json.dump(data, f)
        return

    user_exists = any(user["id"] == user_id for user in data["user_list"])
    if not user_exists:
        if not data["allow_duplicates"]:
            for user in data["user_list"]:
                if user["id"] == user_id:
                    bot.send_message(chat_id, "⚫ لا يمكنك التكرار!")
                    return
        data["total_users"] += 1
        data["user_list"].append({
            "id": user_id,
            "username": message.from_user.username or "مجهول" if lang == "ar" else "Unknown",
            "first_name": message.from_user.first_name or "بدون اسم" if lang == "ar" else "No Name",
            "join_time": time.ctime()
        })
        data["stats"][user_id] = {"points": 0}
        bot.send_message(ADMIN_ID, f"⚫ مستخدم جديد:\n🔻 @{message.from_user.username or 'مجهول'}\nID: {user_id}\nالعدد: {data['total_users']}")
        with open(BOT_FILE, "w") as f:
            json.dump(data, f)
    main_menu(chat_id, user_id)

# التعامل مع الأزرار
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = str(call.from_user.id)
    chat_id = call.message.chat.id
    delete_previous_message(chat_id, user_id)

    with open(BOT_FILE, "r") as f:
        data = json.load(f)
    lang = data["language"].get(user_id, "ar")

    if user_id in data["banned_users"]:
        bot.send_message(chat_id, "⚫ أنت محظور!")
        return

    if not check_channel_membership(user_id):
        text = messages["subscribe"][lang]
        msg = bot.send_message(chat_id, text)
        data["last_message"][user_id] = msg.message_id
        with open(BOT_FILE, "w") as f:
            json.dump(data, f)
        return

    if call.data == "main_menu":
        main_menu(chat_id, user_id)
        return
    elif call.data == "my_stats":
        points = "⚫♾️" if user_id == ADMIN_ID else data["stats"].get(user_id, {}).get("points", 0)
        rank = "أسطورة الظلال" if user_id == ADMIN_ID else get_rank(points, data["ranks"])
        text = messages["my_stats"][lang].format(points=points, rank=rank)
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔳 رجوع" if lang == "ar" else "🔳 Back", callback_data="main_menu"))
    elif call.data == "my_profile":
        points = "⚫♾️" if user_id == ADMIN_ID else data["stats"].get(user_id, {}).get("points", 0)
        rank = "أسطورة الظلال" if user_id == ADMIN_ID else get_rank(points, data["ranks"])
        invites = len(data["invites"].get(user_id, []))
        username = call.from_user.username or "مجهول" if lang == "ar" else "Unknown"
        text = messages["my_profile"][lang].format(username=username, rank=rank, points=points, invites=invites)
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔳 رجوع" if lang == "ar" else "🔳 Back", callback_data="main_menu"))
    elif call.data == "library":
        text = "⚫ المكتبة:"
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("⚫ إضافة بوت" if lang == "ar" else "⚫ Add Bot", callback_data="add_bot"),
                   InlineKeyboardButton("🌑 بوتاتك" if lang == "ar" else "🌑 Your Bots", callback_data="my_bots"))
        markup.add(InlineKeyboardButton("⚫ البوتات المعتمدة" if lang == "ar" else "⚫ Verified Bots", callback_data="verified_bots"))
        markup.add(InlineKeyboardButton("🔳 رجوع" if lang == "ar" else "🔳 Back", callback_data="main_menu"))
    elif call.data == "add_bot":
        text = messages["add_bot_prompt"][lang]
        msg = bot.send_message(chat_id, text)
        bot.register_next_step_handler(msg, save_bot, chat_id, user_id)
        return
    elif call.data == "my_bots":
        if user_id in data["users"] and data["users"][user_id]:
            text = messages["my_bots"][lang]
            markup = InlineKeyboardMarkup()
            for i, item in enumerate(data["users"][user_id]):
                markup.add(InlineKeyboardButton(f"⚫ بوت {i+1}" if lang == "ar" else f"⚫ Bot {i+1}", callback_data=f"show_bot_{i}"))
            markup.add(InlineKeyboardButton("🔳 رجوع" if lang == "ar" else "🔳 Back", callback_data="library"))
        else:
            text = messages["my_bots_empty"][lang]
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("🔳 رجوع" if lang == "ar" else "🔳 Back", callback_data="main_menu"))
    elif call.data.startswith("show_bot_"):
        bot_index = int(call.data.split("_")[2])
        if user_id in data["users"] and 0 <= bot_index < len(data["users"][user_id]):
            bot_info = data["users"][user_id][bot_index]
            text = f"⚫ {bot_info['bot']}\n🌑 {bot_info['desc']}"
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("⚔️ تعديل" if lang == "ar" else "⚔️ Edit", callback_data=f"edit_bot_{bot_index}"),
                       InlineKeyboardButton("💨 حذف" if lang == "ar" else "💨 Delete", callback_data=f"delete_bot_{bot_index}"))
            markup.add(InlineKeyboardButton("🔳 رجوع" if lang == "ar" else "🔳 Back", callback_data="my_bots"))
        else:
            text = messages["my_bots_empty"][lang]
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("🔳 رجوع" if lang == "ar" else "🔳 Back", callback_data="main_menu"))
    elif call.data.startswith("edit_bot_"):
        bot_index = int(call.data.split("_")[2])
        if user_id in data["users"] and 0 <= bot_index < len(data["users"][user_id]):
            text = messages["edit_bot_prompt"][lang]
            msg = bot.send_message(chat_id, text)
            bot.register_next_step_handler(msg, edit_bot_save, chat_id, user_id, bot_index)
            return
    elif call.data.startswith("delete_bot_"):
        bot_index = int(call.data.split("_")[2])
        if user_id in data["users"] and 0 <= bot_index < len(data["users"][user_id]):
            text = messages["delete_bot_prompt"][lang]
            msg = bot.send_message(chat_id, text)
            bot.register_next_step_handler(msg, delete_bot_save, chat_id, user_id, bot_index)
            return
    elif call.data == "verified_bots":
        if data["verified"]:
            text = messages["verified_bots"][lang]
            markup = InlineKeyboardMarkup()
            for i, item in enumerate(data["verified"]):
                markup.add(InlineKeyboardButton(f"⚫ بوت {i+1}" if lang == "ar" else "⚫ Bot {i+1}", callback_data=f"show_verified_{i}"))
            markup.add(InlineKeyboardButton("🔳 رجوع" if lang == "ar" else "🔳 Back", callback_data="library"))
        else:
            text = messages["verified_bots_empty"][lang]
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("🔳 رجوع" if lang == "ar" else "🔳 Back", callback_data="main_menu"))
    elif call.data.startswith("show_verified_"):
        bot_index = int(call.data.split("_")[2])
        if 0 <= bot_index < len(data["verified"]):
            bot_info = data["verified"][bot_index]
            text = f"⚫ {bot_info['bot']}\n🌑 {bot_info['desc']}"
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("🔳 رجوع" if lang == "ar" else "🔳 Back", callback_data="verified_bots"))
    elif call.data == "tasks":
        if data["tasks"]:
            tasks_list = "\n".join([f"⚫ {task['desc']} - {task['points']} نقطة" for task in data["tasks"]])
            text = messages["tasks"][lang].format(tasks_list=tasks_list)
        else:
            text = messages["tasks_empty"][lang]
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔳 رجوع" if lang == "ar" else "🔳 Back", callback_data="main_menu"))
    elif call.data == "shop":
        if data["shop"]:
            shop_list = "\n".join([f"⚫ {item['name']} - {item['price']} نقطة\n🌑 {item['desc']}" for item in data["shop"]])
            text = messages["shop"][lang].format(shop_list=shop_list)
            markup = InlineKeyboardMarkup()
            for i, item in enumerate(data["shop"]):
                markup.add(InlineKeyboardButton(f"⚫ شراء: {item['name']}", callback_data=f"buy_item_{i}"))
            markup.add(InlineKeyboardButton("🔳 رجوع" if lang == "ar" else "🔳 Back", callback_data="main_menu"))
        else:
            text = messages["shop_empty"][lang]
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("🔳 رجوع" if lang == "ar" else "🔳 Back", callback_data="main_menu"))
    elif call.data.startswith("buy_item_"):
        item_index = int(call.data.split("_")[2])
        if 0 <= item_index < len(data["shop"]):
            item = data["shop"][item_index]
            points = data["stats"].get(user_id, {}).get("points", 0)
            if points >= item["price"]:
                data["stats"][user_id]["points"] -= item["price"]
                text = messages["shop_purchase"][lang].format(item=item["name"])
                bot.send_message(ADMIN_ID, f"⚫ @{call.from_user.username or 'مجهول'} اشترى: {item['name']}")
                with open(BOT_FILE, "w") as f:
                    json.dump(data, f)
            else:
                text = messages["shop_insufficient"][lang]
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("🔳 رجوع" if lang == "ar" else "🔳 Back", callback_data="shop"))
    elif call.data == "stats":
        if data["user_list"]:
            sorted_users = sorted(data["stats"].items(), key=lambda x: x[1]["points"], reverse=True)
            top_12 = "\n".join([f"⚫ @{data['user_list'][i]['username']} - {points['points']} نقطة" for i, (uid, points) in enumerate(sorted_users[:12]) if uid != ADMIN_ID])
            next_8 = "\n".join([f"🌑 @{data['user_list'][i]['username']} - {points['points']} نقطة" for i, (uid, points) in enumerate(sorted_users[12:20]) if uid != ADMIN_ID])
            text = messages["stats"][lang].format(total_users=data["total_users"], top_12=top_12 or "⚫ لا أحد", next_8=next_8 or "🌑 لا أحد")
        else:
            text = messages["stats_empty"][lang]
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔳 رجوع" if lang == "ar" else "🔳 Back", callback_data="main_menu"))
    elif call.data == "about":
        text = "⚫ هاوية الظلال: مكتبة بوتات موثوقة ونقاط مجانية!\n🌑 انضم للظلام!"
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔳 رجوع" if lang == "ar" else "🔳 Back", callback_data="main_menu"))
    elif call.data == "complaint":
        text = "⚫ اكتب شكواك:"
        msg = bot.send_message(chat_id, text)
        bot.register_next_step_handler(msg, save_complaint, chat_id, user_id)
        return
    elif call.data == "admin_panel" and user_id == ADMIN_ID:
        text = messages["admin_panel"][lang]
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("⚫ إدارة المستخدمين", callback_data="manage_users"),
                   InlineKeyboardButton("🌑 إدارة المكتبة", callback_data="manage_library"))
        markup.add(InlineKeyboardButton("⚔️ إدارة المهام", callback_data="manage_tasks"),
                   InlineKeyboardButton("💨 إدارة النقاط", callback_data="manage_points"))
        markup.add(InlineKeyboardButton("⬛ إرسال رسالة", callback_data="send_message"),
                   InlineKeyboardButton("⚫ إدارة المتجر", callback_data="manage_shop"))
        markup.add(InlineKeyboardButton("🌙 إدارة المسابقات", callback_data="manage_contests"),
                   InlineKeyboardButton("🔳 إحصائيات الأدمن", callback_data="admin_stats"))
        markup.add(InlineKeyboardButton("⚫ الشكاوى", callback_data="view_complaints"),
                   InlineKeyboardButton("🌑 تعديل التعريف", callback_data="edit_about"))
        markup.add(InlineKeyboardButton("🔳 رجوع", callback_data="main_menu"))
    elif call.data == "manage_users" and user_id == ADMIN_ID:
        text = "⚫ إدارة المستخدمين:"
        markup = InlineKeyboardMarkup()
        for user in data["user_list"]:
            markup.add(InlineKeyboardButton(f"⚫ @{user['username']} - ID: {user['id']}", callback_data=f"manage_user_{user['id']}"))
        markup.add(InlineKeyboardButton("🔳 رجوع", callback_data="admin_panel"))
    elif call.data.startswith("manage_user_") and user_id == ADMIN_ID:
        target_id = call.data.split("_")[2]
        user_data = next((u for u in data["user_list"] if u["id"] == target_id), None)
        if user_data:
            text = f"⚫ @{user_data['username']} - ID: {target_id}\n🌑 البوتات: {len(data['users'].get(target_id, []))}"
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("⚫ عرض المكتبة", callback_data=f"view_user_bots_{target_id}"),
                       InlineKeyboardButton("💨 حظر", callback_data=f"ban_user_{target_id}"))
            markup.add(InlineKeyboardButton("⚔️ إضافة نقاط", callback_data=f"add_points_{target_id}"),
                       InlineKeyboardButton("🌑 خصم نقاط", callback_data=f"remove_points_{target_id}"))
            markup.add(InlineKeyboardButton("⬛ السماح بالتعدد", callback_data="toggle_duplicates"))
            markup.add(InlineKeyboardButton("🔳 رجوع", callback_data="manage_users"))
    elif call.data.startswith("view_user_bots_") and user_id == ADMIN_ID:
        target_id = call.data.split("_")[3]
        if target_id in data["users"] and data["users"][target_id]:
            text = f"⚫ بوتات @{next(u['username'] for u in data['user_list'] if u['id'] == target_id)}:"
            markup = InlineKeyboardMarkup()
            for i, item in enumerate(data["users"][target_id]):
                markup.add(InlineKeyboardButton(f"⚫ بوت {i+1}", callback_data=f"admin_show_bot_{target_id}_{i}"))
            markup.add(InlineKeyboardButton("🔳 رجوع", callback_data=f"manage_user_{target_id}"))
        else:
            text = "🌑 لا بوتات!"
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("🔳 رجوع", callback_data=f"manage_user_{target_id}"))
    elif call.data.startswith("admin_show_bot_") and user_id == ADMIN_ID:
        target_id, bot_index = call.data.split("_")[3], int(call.data.split("_")[4])
        if target_id in data["users"] and 0 <= bot_index < len(data["users"][target_id]):
            bot_info = data["users"][target_id][bot_index]
            text = f"⚫ {bot_info['bot']}\n🌑 {bot_info['desc']}"
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("⚫ اعتماد", callback_data=f"approve_bot_{target_id}_{bot_index}"),
                       InlineKeyboardButton("🌑 رفض", callback_data=f"reject_bot_{target_id}_{bot_index}"))
            markup.add(InlineKeyboardButton("💨 حذف", callback_data=f"delete_user_bot_{target_id}_{bot_index}"),
                       InlineKeyboardButton("⬛ تحذير", callback_data=f"warn_user_{target_id}_{bot_index}"))
            markup.add(InlineKeyboardButton("🔳 رجوع", callback_data=f"view_user_bots_{target_id}"))
    elif call.data.startswith("approve_bot_") and user_id == ADMIN_ID:
        target_id, bot_index = call.data.split("_")[2], int(call.data.split("_")[3])
        bot_info = data["users"][target_id][bot_index]
        data["verified"].append(bot_info)
        data["stats"][target_id]["points"] += 5
        bot.send_message(target_id, messages["bot_approved"][lang])
        text = "⚫ تم الاعتماد!"
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔳 رجوع", callback_data=f"view_user_bots_{target_id}"))
        with open(BOT_FILE, "w") as f:
            json.dump(data, f)
    elif call.data.startswith("reject_bot_") and user_id == ADMIN_ID:
        target_id = call.data.split("_")[2]
        bot.send_message(target_id, messages["bot_not_trusted"][lang])
        text = "⚫ تم الرفض!"
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔳 رجوع", callback_data=f"view_user_bots_{target_id}"))
    elif call.data.startswith("delete_user_bot_") and user_id == ADMIN_ID:
        target_id, bot_index = call.data.split("_")[3], int(call.data.split("_")[4])
        del data["users"][target_id][bot_index]
        text = "💨 تم الحذف!"
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔳 رجوع", callback_data=f"view_user_bots_{target_id}"))
        with open(BOT_FILE, "w") as f:
            json.dump(data, f)
    elif call.data.startswith("warn_user_") and user_id == ADMIN_ID:
        target_id = call.data.split("_")[2]
        bot.send_message(target_id, "⚫ تحذير: بوتك غير موثوق، ننصحك بحذفه!")
        text = "⬛ تم التحذير!"
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔳 رجوع", callback_data=f"view_user_bots_{target_id}"))
    elif call.data.startswith("ban_user_") and user_id == ADMIN_ID:
        target_id = call.data.split("_")[2]
        if target_id not in data["banned_users"]:
            data["banned_users"].append(target_id)
            text = "💨 تم الحظر!"
            with open(BOT_FILE, "w") as f:
                json.dump(data, f)
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔳 رجوع", callback_data=f"manage_user_{target_id}"))
    elif call.data.startswith("add_points_") and user_id == ADMIN_ID:
        target_id = call.data.split("_")[2]
        text = "⚫ أدخل عدد النقاط:"
        msg = bot.send_message(chat_id, text)
        bot.register_next_step_handler(msg, add_points, chat_id, target_id)
        return
    elif call.data.startswith("remove_points_") and user_id == ADMIN_ID:
        target_id = call.data.split("_")[2]
        text = "⚫ أدخل عدد النقاط:"
        msg = bot.send_message(chat_id, text)
        bot.register_next_step_handler(msg, remove_points, chat_id, target_id)
        return
    elif call.data == "toggle_duplicates" and user_id == ADMIN_ID:
        data["allow_duplicates"] = not data["allow_duplicates"]
        text = f"⚫ التعدد: {'مسموح' if data['allow_duplicates'] else 'ممنوع'}"
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔳 رجوع", callback_data="manage_users"))
        with open(BOT_FILE, "w") as f:
            json.dump(data, f)
    elif call.data == "manage_library" and user_id == ADMIN_ID:
        text = "🌑 إدارة المكتبة:"
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("⚫ إضافة بوت", callback_data="admin_add_bot"),
                   InlineKeyboardButton("🌑 عرض المعتمدة", callback_data="admin_view_verified"))
        markup.add(InlineKeyboardButton("🔳 رجوع", callback_data="admin_panel"))
    elif call.data == "admin_add_bot" and user_id == ADMIN_ID:
        text = "⚫ أدخل اللينك + الوصف:"
        msg = bot.send_message(chat_id, text)
        bot.register_next_step_handler(msg, admin_save_bot, chat_id)
        return
    elif call.data == "admin_view_verified" and user_id == ADMIN_ID:
        if data["verified"]:
            text = "⚫ البوتات المعتمدة:"
            markup = InlineKeyboardMarkup()
            for i, item in enumerate(data["verified"]):
                markup.add(InlineKeyboardButton(f"⚫ بوت {i+1}", callback_data=f"admin_show_verified_{i}"))
            markup.add(InlineKeyboardButton("🔳 رجوع", callback_data="manage_library"))
        else:
            text = "🌑 لا بوتات معتمدة!"
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("🔳 رجوع", callback_data="manage_library"))
    elif call.data.startswith("admin_show_verified_") and user_id == ADMIN_ID:
        bot_index = int(call.data.split("_")[3])
        if 0 <= bot_index < len(data["verified"]):
            bot_info = data["verified"][bot_index]
            text = f"⚫ {bot_info['bot']}\n🌑 {bot_info['desc']}"
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("💨 حذف", callback_data=f"admin_delete_verified_{bot_index}"))
            markup.add(InlineKeyboardButton("🔳 رجوع", callback_data="admin_view_verified"))
    elif call.data.startswith("admin_delete_verified_") and user_id == ADMIN_ID:
        bot_index = int(call.data.split("_")[3])
        del data["verified"][bot_index]
        text = "💨 تم الحذف!"
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔳 رجوع", callback_data="admin_view_verified"))
        with open(BOT_FILE, "w") as f:
            json.dump(data, f)
    elif call.data == "manage_tasks" and user_id == ADMIN_ID:
        text = "⚔️ إدارة المهام:"
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("⚫ إضافة مهمة", callback_data="add_task"),
                   InlineKeyboardButton("🌑 عرض المهام", callback_data="view_tasks"))
        markup.add(InlineKeyboardButton("🔳 رجوع", callback_data="admin_panel"))
    elif call.data == "add_task" and user_id == ADMIN_ID:
        text = "⚫ أدخل المهمة + النقاط (مثال: أضف بوت - 10):"
        msg = bot.send_message(chat_id, text)
        bot.register_next_step_handler(msg, save_task, chat_id)
        return
    elif call.data == "view_tasks" and user_id == ADMIN_ID:
        if data["tasks"]:
            text = "⚫ المهام:"
            markup = InlineKeyboardMarkup()
            for i, task in enumerate(data["tasks"]):
                markup.add(InlineKeyboardButton(f"⚫ {task['desc']} - {task['points']}", callback_data=f"delete_task_{i}"))
            markup.add(InlineKeyboardButton("🔳 رجوع", callback_data="manage_tasks"))
        else:
            text = "🌑 لا مهام!"
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("🔳 رجوع", callback_data="manage_tasks"))
    elif call.data.startswith("delete_task_") and user_id == ADMIN_ID:
        task_index = int(call.data.split("_")[2])
        del data["tasks"][task_index]
        text = "💨 تم الحذف!"
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔳 رجوع", callback_data="view_tasks"))
        with open(BOT_FILE, "w") as f:
            json.dump(data, f)
    elif call.data == "manage_points" and user_id == ADMIN_ID:
        text = "💨 إدارة النقاط:"
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("⚫ إنشاء لينك نقاط", callback_data="create_points_link"))
        markup.add(InlineKeyboardButton("🔳 رجوع", callback_data="admin_panel"))
    elif call.data == "create_points_link" and user_id == ADMIN_ID:
        text = "⚫ أدخل عدد النقاط:"
        msg = bot.send_message(chat_id, text)
        bot.register_next_step_handler(msg, create_points_link, chat_id)
        return
    elif call.data == "send_message" and user_id == ADMIN_ID:
        text = "⬛ أدخل الرسالة + ID (اختياري، اتركه فارغًا للكل):"
        msg = bot.send_message(chat_id, text)
        bot.register_next_step_handler(msg, send_admin_message, chat_id)
        return
    elif call.data == "manage_shop" and user_id == ADMIN_ID:
        text = "⚫ إدارة المتجر:"
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("⚫ إضافة منتج", callback_data="add_shop_item"),
                   InlineKeyboardButton("🌑 عرض المتجر", callback_data="view_shop_items"))
        markup.add(InlineKeyboardButton("🔳 رجوع", callback_data="admin_panel"))
    elif call.data == "add_shop_item" and user_id == ADMIN_ID:
        text = "⚫ أدخل الاسم + السعر + الوصف (مثال: بوت مميز - 50 - بوت قوي):"
        msg = bot.send_message(chat_id, text)
        bot.register_next_step_handler(msg, save_shop_item, chat_id)
        return
    elif call.data == "view_shop_items" and user_id == ADMIN_ID:
        if data["shop"]:
            text = "⚫ المتجر:"
            markup = InlineKeyboardMarkup()
            for i, item in enumerate(data["shop"]):
                markup.add(InlineKeyboardButton(f"⚫ {item['name']} - {item['price']}", callback_data=f"delete_shop_item_{i}"))
            markup.add(InlineKeyboardButton("🔳 رجوع", callback_data="manage_shop"))
        else:
            text = "🌑 المتجر خالٍ!"
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("🔳 رجوع", callback_data="manage_shop"))
    elif call.data.startswith("delete_shop_item_") and user_id == ADMIN_ID:
        item_index = int(call.data.split("_")[3])
        del data["shop"][item_index]
        text = "💨 تم الحذف!"
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔳 رجوع", callback_data="view_shop_items"))
        with open(BOT_FILE, "w") as f:
            json.dump(data, f)
    elif call.data == "manage_contests" and user_id == ADMIN_ID:
        text = "🌙 إدارة المسابقات: (سيتم تفعيلها لاحقًا)"
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔳 رجوع", callback_data="admin_panel"))
    elif call.data == "admin_stats" and user_id == ADMIN_ID:
        text = f"⚫ إحصائيات الأدمن:\n🔻 العدد الكلي: {data['total_users']}\n"
        sorted_users = sorted(data["stats"].items(), key=lambda x: x[1]["points"], reverse=True)
        text += "⚫ أعلى المستخدمين:\n" + "\n".join([f"🔳 @{data['user_list'][i]['username']} - ID: {uid} - {points['points']}" for i, (uid, points) in enumerate(sorted_users[:10])])
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("⚫ تعديل العدد الكلي", callback_data="edit_total_users"))
        markup.add(InlineKeyboardButton("🔳 رجوع", callback_data="admin_panel"))
    elif call.data == "edit_total_users" and user_id == ADMIN_ID:
        text = "⚫ أدخل العدد الجديد:"
        msg = bot.send_message(chat_id, text)
        bot.register_next_step_handler(msg, edit_total_users, chat_id)
        return
    elif call.data == "view_complaints" and user_id == ADMIN_ID:
        if data["complaints"]:
            text = "⚫ الشكاوى:"
            markup = InlineKeyboardMarkup()
            for i, complaint in enumerate(data["complaints"]):
                markup.add(InlineKeyboardButton(f"⚫ @{complaint['username']} - ID: {complaint['user_id']}", callback_data=f"reply_complaint_{i}"))
            markup.add(InlineKeyboardButton("🔳 رجوع", callback_data="admin_panel"))
        else:
            text = "🌑 لا شكاوى!"
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("🔳 رجوع", callback_data="admin_panel"))
    elif call.data.startswith("reply_complaint_") and user_id == ADMIN_ID:
        complaint_index = int(call.data.split("_")[2])
        complaint = data["complaints"][complaint_index]
        text = f"⚫ شكوى من @{complaint['username']} - ID: {complaint['user_id']}\n🌑 {complaint['text']}\n⚫ أدخل الرد:"
        msg = bot.send_message(chat_id, text)
        bot.register_next_step_handler(msg, reply_complaint, chat_id, complaint["user_id"])
        return
    elif call.data == "edit_about" and user_id == ADMIN_ID:
        text = "⚫ أدخل نص التعريف الجديد:"
        msg = bot.send_message(chat_id, text)
        bot.register_next_step_handler(msg, edit_about, chat_id)
        return

    msg = bot.send_message(chat_id, text, reply_markup=markup)
    data["last_message"][user_id] = msg.message_id
    with open(BOT_FILE, "w") as f:
        json.dump(data, f)

# دوال مساعدة
def get_rank(points, ranks):
    for rank, (min_points, max_points) in ranks.items():
        if min_points <= points <= max_points:
            return rank
    return "رماد الظلال"

def save_bot(message, chat_id, user_id):
    user_id = str(user_id)
    with open(BOT_FILE, "r") as f:
        data = json.load(f)
    lang = data["language"].get(user_id, "ar")
    bot.delete_message(chat_id, message.message_id)

    if not check_channel_membership(user_id):
        text = messages["subscribe"][lang]
        msg = bot.send_message(chat_id, text)
        data["last_message"][user_id] = msg.message_id
        with open(BOT_FILE, "w") as f:
            json.dump(data, f)
        return

    try:
        text = message.text.split(" - ")
        bot_link, desc = text[0], text[1] if len(text) > 1 else "بدون وصف"
        if user_id not in data["users"]:
            data["users"][user_id] = []
        if not data["allow_duplicates"] and any(bot["bot"] == bot_link for bot in data["users"][user_id]):
            text = "⚫ لا يمكن تكرار البوت!"
        else:
            data["users"][user_id].append({"bot": bot_link, "desc": desc})
            text = messages["add_bot_success"][lang] + "\n" + random.choice(random_notifications)
            bot.send_message(ADMIN_ID, f"⚫ إضافة من @{message.from_user.username or 'مجهول'}:\n🔻 {bot_link}\n🌑 {desc}")
        with open(BOT_FILE, "w") as f:
            json.dump(data, f)
    except Exception:
        text = messages["add_bot_error"][lang]
    msg = bot.send_message(chat_id, text)
    data["last_message"][user_id] = msg.message_id
    with open(BOT_FILE, "w") as f:
        json.dump(data, f)
    time.sleep(2)
    main_menu(chat_id, user_id)

def edit_bot_save(message, chat_id, user_id, bot_index):
    user_id = str(user_id)
    with open(BOT_FILE, "r") as f:
        data = json.load(f)
    lang = data["language"].get(user_id, "ar")
    bot.delete_message(chat_id, message.message_id)

    try:
        text = message.text.split(" - ")
        new_bot, new_desc = text[1], text[2] if len(text) > 2 else data["users"][user_id][bot_index]["desc"]
        data["users"][user_id][bot_index] = {"bot": new_bot, "desc": new_desc}
        text = messages["edit_bot_success"][lang]
        with open(BOT_FILE, "w") as f:
            json.dump(data, f)
    except Exception:
        text = messages["edit_bot_error"][lang]
    msg = bot.send_message(chat_id, text)
    data["last_message"][user_id] = msg.message_id
    with open(BOT_FILE, "w") as f:
        json.dump(data, f)
    time.sleep(2)
    main_menu(chat_id, user_id)

def delete_bot_save(message, chat_id, user_id, bot_index):
    user_id = str(user_id)
    with open(BOT_FILE, "r") as f:
        data = json.load(f)
    lang = data["language"].get(user_id, "ar")
    bot.delete_message(chat_id, message.message_id)

    try:
        index = int(message.text) - 1
        if 0 <= index < len(data["users"][user_id]):
            del data["users"][user_id][index]
            text = messages["delete_bot_success"][lang]
            with open(BOT_FILE, "w") as f:
                json.dump(data, f)
        else:
            text = messages["delete_bot_error"][lang]
    except Exception:
        text = messages["delete_bot_error"][lang]
    msg = bot.send_message(chat_id, text)
    data["last_message"][user_id] = msg.message_id
    with open(BOT_FILE, "w") as f:
        json.dump(data, f)
    time.sleep(2)
    main_menu(chat_id, user_id)

def save_complaint(message, chat_id, user_id):
    user_id = str(user_id)
    with open(BOT_FILE, "r") as f:
        data = json.load(f)
    lang = data["language"].get(user_id, "ar")
    bot.delete_message(chat_id, message.message_id)

    data["complaints"].append({
        "user_id": user_id,
        "username": message.from_user.username or "مجهول",
        "text": message.text
    })
    text = messages["complaint_received"][lang]
    bot.send_message(ADMIN_ID, f"⚫ شكوى من @{message.from_user.username or 'مجهول'} - ID: {user_id}\n🌑 {message.text}")
    msg = bot.send_message(chat_id, text)
    data["last_message"][user_id] = msg.message_id
    with open(BOT_FILE, "w") as f:
        json.dump(data, f)
    time.sleep(2)
    main_menu(chat_id, user_id)

def add_points(message, chat_id, target_id):
    bot.delete_message(chat_id, message.message_id)
    with open(BOT_FILE, "r") as f:
        data = json.load(f)
    try:
        points = int(message.text)
        data["stats"][target_id]["points"] += points
        text = f"⚫ تم إضافة {points} نقطة!"
        bot.send_message(target_id, f"⚫ تم إضافة {points} نقطة إلى رصيدك!")
        with open(BOT_FILE, "w") as f:
            json.dump(data, f)
    except Exception:
        text = "⚫ خطأ في الرقم!"
    msg = bot.send_message(chat_id, text)
    data["last_message"][str(chat_id)] = msg.message_id
    with open(BOT_FILE, "w") as f:
        json.dump(data, f)
    time.sleep(2)
    callback_handler(telebot.types.CallbackQuery(id="fake", from_user=bot.get_me(), message=msg, chat_instance=str(chat_id), data=f"manage_user_{target_id}"))

def remove_points(message, chat_id, target_id):
    bot.delete_message(chat_id, message.message_id)
    with open(BOT_FILE, "r") as f:
        data = json.load(f)
    try:
        points = int(message.text)
        data["stats"][target_id]["points"] = max(0, data["stats"][target_id]["points"] - points)
        text = f"⚫ تم خصم {points} نقطة!"
        bot.send_message(target_id, f"⚫ تم خصم {points} نقطة من رصيدك!")
        with open(BOT_FILE, "w") as f:
            json.dump(data, f)
    except Exception:
        text = "⚫ خطأ في الرقم!"
    msg = bot.send_message(chat_id, text)
    data["last_message"][str(chat_id)] = msg.message_id
    with open(BOT_FILE, "w") as f:
        json.dump(data, f)
    time.sleep(2)
    callback_handler(telebot.types.CallbackQuery(id="fake", from_user=bot.get_me(), message=msg, chat_instance=str(chat_id), data=f"manage_user_{target_id}"))

def admin_save_bot(message, chat_id):
    bot.delete_message(chat_id, message.message_id)
    with open(BOT_FILE, "r") as f:
        data = json.load(f)
    try:
        text = message.text.split(" - ")
        bot_link, desc = text[0], text[1] if len(text) > 1 else "بدون وصف"
        data["verified"].append({"bot": bot_link, "desc": desc})
        text = "⚫ تمت الإضافة!"
        with open(BOT_FILE, "w") as f:
            json.dump(data, f)
    except Exception:
        text = "⚫ خطأ في الصيغة!"
    msg = bot.send_message(chat_id, text)
    data["last_message"][str(chat_id)] = msg.message_id
    with open(BOT_FILE, "w") as f:
        json.dump(data, f)
    time.sleep(2)
    callback_handler(telebot.types.CallbackQuery(id="fake", from_user=bot.get_me(), message=msg, chat_instance=str(chat_id), data="manage_library"))

def save_task(message, chat_id):
    bot.delete_message(chat_id, message.message_id)
    with open(BOT_FILE, "r") as f:
        data = json.load(f)
    try:
        text = message.text.split(" - ")
        desc, points = text[0], int(text[1])
        data["tasks"].append({"desc": desc, "points": points})
        text = "⚫ تمت الإضافة!"
        for user in data["user_list"]:
            bot.send_message(user["id"], f"⚫ مهمة جديدة: {desc} - {points} نقطة")
        with open(BOT_FILE, "w") as f:
            json.dump(data, f)
    except Exception:
        text = "⚫ خطأ في الصيغة!"
    msg = bot.send_message(chat_id, text)
    data["last_message"][str(chat_id)] = msg.message_id
    with open(BOT_FILE, "w") as f:
        json.dump(data, f)
    time.sleep(2)
    callback_handler(telebot.types.CallbackQuery(id="fake", from_user=bot.get_me(), message=msg, chat_instance=str(chat_id), data="manage_tasks"))

def create_points_link(message, chat_id):
    bot.delete_message(chat_id, message.message_id)
    with open(BOT_FILE, "r") as f:
        data = json.load(f)
    try:
        points = int(message.text)
        link = f"https://t.me/{bot.get_me().username}?start=points_{points}"
        text = f"⚫ رابط النقاط: {link}"
    except Exception:
        text = "⚫ خطأ في الرقم!"
    msg = bot.send_message(chat_id, text)
    data["last_message"][str(chat_id)] = msg.message_id
    with open(BOT_FILE, "w") as f:
        json.dump(data, f)
    time.sleep(2)
    callback_handler(telebot.types.CallbackQuery(id="fake", from_user=bot.get_me(), message=msg, chat_instance=str(chat_id), data="manage_points"))

def send_admin_message(message, chat_id):
    bot.delete_message(chat_id, message.message_id)
    with open(BOT_FILE, "r") as f:
        data = json.load(f)
    try:
        parts = message.text.split(" - ")
        msg_text = parts[0]
        target_id = parts[1] if len(parts) > 1 else None
        if target_id:
            bot.send_message(target_id, f"⚫ رسالة من الأدمن:\n{msg_text}")
            text = "⚫ تم الإرسال!"
        else:
            for user in data["user_list"]:
                bot.send_message(user["id"], f"⚫ رسالة من الأدمن:\n{msg_text}")
            text = "⚫ تم الإرسال للجميع!"
    except Exception:
        text = "⚫ خطأ!"
    msg = bot.send_message(chat_id, text)
    data["last_message"][str(chat_id)] = msg.message_id
    with open(BOT_FILE, "w") as f:
        json.dump(data, f)
    time.sleep(2)
    callback_handler(telebot.types.CallbackQuery(id="fake", from_user=bot.get_me(), message=msg, chat_instance=str(chat_id), data="admin_panel"))

def save_shop_item(message, chat_id):
    bot.delete_message(chat_id, message.message_id)
    with open(BOT_FILE, "r") as f:
        data = json.load(f)
    try:
        text = message.text.split(" - ")
        name, price, desc = text[0], int(text[1]), text[2] if len(text) > 2 else "بدون وصف"
        data["shop"].append({"name": name, "price": price, "desc": desc})
        text = "⚫ تمت الإضافة!"
        with open(BOT_FILE, "w") as f:
            json.dump(data, f)
    except Exception:
        text = "⚫ خطأ في الصيغة!"
    msg = bot.send_message(chat_id, text)
    data["last_message"][str(chat_id)] = msg.message_id
    with open(BOT_FILE, "w") as f:
        json.dump(data, f)
    time.sleep(2)
    callback_handler(telebot.types.CallbackQuery(id="fake", from_user=bot.get_me(), message=msg, chat_instance=str(chat_id), data="manage_shop"))

def edit_total_users(message, chat_id):
    bot.delete_message(chat_id, message.message_id)
    with open(BOT_FILE, "r") as f:
        data = json.load(f)
    try:
        data["total_users"] = int(message.text)
        text = "⚫ تم التعديل!"
        with open(BOT_FILE, "w") as f:
            json.dump(data, f)
    except Exception:
        text = "⚫ خطأ في الرقم!"
    msg = bot.send_message(chat_id, text)
    data["last_message"][str(chat_id)] = msg.message_id
    with open(BOT_FILE, "w") as f:
        json.dump(data, f)
    time.sleep(2)
    callback_handler(telebot.types.CallbackQuery(id="fake", from_user=bot.get_me(), message=msg, chat_instance=str(chat_id), data="admin_stats"))

def reply_complaint(message, chat_id, target_id):
    bot.delete_message(chat_id, message.message_id)
    with open(BOT_FILE, "r") as f:
        data = json.load(f)
    bot.send_message(target_id, f"⚫ رد من الأدمن:\n{message.text}")
    text = "⚫ تم الرد!"
    msg = bot.send_message(chat_id, text)
    data["last_message"][str(chat_id)] = msg.message_id
    with open(BOT_FILE, "w") as f:
        json.dump(data, f)
    time.sleep(2)
    callback_handler(telebot.types.CallbackQuery(id="fake", from_user=bot.get_me(), message=msg, chat_instance=str(chat_id), data="view_complaints"))

def edit_about(message, chat_id):
    bot.delete_message(chat_id, message.message_id)
    with open(BOT_FILE, "r") as f:
        data = json.load(f)
    data["about"] = message.text
    text = "⚫ تم تعديل التعريف!"
    msg = bot.send_message(chat_id, text)
    data["last_message"][str(chat_id)] = msg.message_id
    with open(BOT_FILE, "w") as f:
        json.dump(data, f)
    time.sleep(2)
    callback_handler(telebot.types.CallbackQuery(id="fake", from_user=bot.get_me(), message=msg, chat_instance=str(chat_id), data="admin_panel"))

# الإحالات
@bot.message_handler(func=lambda message: message.text.startswith("/start points_"))
def command_start_points(message):
    user_id = str(message.from_user.id)
    chat_id = message.chat.id
    points = int(message.text.split("_")[1])
    delete_previous_message(chat_id, user_id)

    with open(BOT_FILE, "r") as f:
        data = json.load(f)
    lang = data["language"].get(user_id, "ar")

    if not check_channel_membership(user_id):
        text = messages["subscribe"][lang]
        msg = bot.send_message(chat_id, text)
        data["last_message"][user_id] = msg.message_id
        with open(BOT_FILE, "w") as f:
            json.dump(data, f)
        return

    if user_id not in data["stats"]:
        data["stats"][user_id] = {"points": 0}
    data["stats"][user_id]["points"] += points
    text = f"⚫ تم إضافة {points} نقطة!"
    msg = bot.send_message(chat_id, text)
    data["last_message"][user_id] = msg.message_id
    with open(BOT_FILE, "w") as f:
        json.dump(data, f)
    time.sleep(2)
    main_menu(chat_id, user_id)

# تسجيل الرسائل
@bot.message_handler(func=lambda message: True)
def log_user_data(message):
    user_id = str(message.from_user.id)
    chat_id = message.chat.id
    with open(BOT_FILE, "r") as f:
        data = json.load(f)
    lang = data["language"].get(user_id, "ar")

    if user_id in data["banned_users"]:
        return

    if not check_channel_membership(user_id) and message.text != "/start":
        delete_previous_message(chat_id, user_id)
        text = messages["subscribe"][lang]
        msg = bot.send_message(chat_id, text)
        data["last_message"][user_id] = msg.message_id
        with open(BOT_FILE, "w") as f:
            json.dump(data, f)
        return

    logging.info(f"📅 {time.ctime(message.date)} | 🆔 {user_id} | 👤 @{message.from_user.username or 'مجهول'} | 💬 {message.text}")

# تشغيل البوت
print("⚫ انفجار الهاوية يبدأ الآن...")
bot.polling()