import telebot
from telebot.types import ChatMemberUpdated

API_TOKEN  = "8730756644:AAHdHnhibA6FTebmdpi-IzdVWuH9CpgD3Ro"
CHANNEL_ID = -1003422607901

bot = telebot.TeleBot(API_TOKEN)

user_links      = {}  # user_id -> invite_link
link_owners     = {}  # invite_link -> user_id
referral_counts = {}  # user_id -> count


@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(
        message,
        "Welcome to the Yash X Prime Referral Bot! 🚀\n\n"
        "Invite people and earn rewards!\n\n"
        "👉 /mylink - Get your unique invite link\n"
        "👉 /stats - Check your score"
    )


@bot.message_handler(commands=["mylink"])
def get_link(message):
    user_id = message.from_user.id

    if user_id in user_links:
        bot.reply_to(message, f"Your invite link:\n{user_links[user_id]}")
        return

    try:
        invite_link = bot.create_chat_invite_link(
            CHANNEL_ID,
            name=f"User_{user_id}"
        ).invite_link

        user_links[user_id]      = invite_link
        link_owners[invite_link] = user_id
        referral_counts[user_id] = 0

        bot.reply_to(
            message,
            f"Your unique invite link:\n{invite_link}\n\n"
            "Share this link with your friends!\n"
            "Your count will increase for everyone who joins using it."
        )

    except Exception as e:
        bot.reply_to(
            message,
            "Error: Make sure the bot is an Admin in the channel\n"
            "with 'Invite Users via Link' permission."
        )


@bot.message_handler(commands=["stats"])
def get_stats(message):
    user_id = message.from_user.id
    count   = referral_counts.get(user_id, 0)
    bot.reply_to(message, f"📊 Your Stats\n\nYou have added {count} members to the channel!")


@bot.chat_member_handler()
def handle_new_member(update: ChatMemberUpdated):
    new_status = update.new_chat_member.status
    old_status = update.old_chat_member.status

    if new_status != "member" or old_status in ("member", "administrator", "creator"):
        return

    invite_info = update.invite_link
    if not invite_info:
        return

    link_used = invite_info.invite_link

    if link_used in link_owners:
        referrer_id = link_owners[link_used]
        referral_counts[referrer_id] = referral_counts.get(referrer_id, 0) + 1
        count = referral_counts[referrer_id]

        bot.send_message(
            referrer_id,
            f"Someone joined using your link!\n"
            f"Your new score: {count}"
        )


print("Bot is running...")
bot.infinity_polling(allowed_updates=["message", "chat_member"])
