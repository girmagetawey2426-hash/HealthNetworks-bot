import os
import sqlite3
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ChatMemberHandler,
    ContextTypes,
    filters
)

TOKEN = os.getenv("BOT_TOKEN")

REQUIRED_INVITES = 5

# Database setup
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    invites INTEGER DEFAULT 0,
    unlocked INTEGER DEFAULT 0
)
""")
conn.commit()


def add_user(user_id):
    cursor.execute(
        "INSERT OR IGNORE INTO users(user_id) VALUES(?)",
        (user_id,)
    )
    conn.commit()


def get_progress(user_id):
    cursor.execute(
        "SELECT invites, unlocked FROM users WHERE user_id=?",
        (user_id,)
    )
    return cursor.fetchone()


def add_invite(user_id):
    cursor.execute(
        "UPDATE users SET invites = invites + 1 WHERE user_id=?",
        (user_id,)
    )
    conn.commit()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id)

    await update.message.reply_text(
        "Welcome! Invite 5 members to unlock posting.\nUse /mylink to get your invite link."
    )


async def progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    data = get_progress(user_id)

    if data:
        await update.message.reply_text(
            f"Your progress: {data[0]}/{REQUIRED_INVITES} invites"
        )
    else:
        await update.message.reply_text("Use /start first.")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/mylink - get your invite link\n"
        "/progress - check your invites"
    )


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("progress", progress))
    app.add_handler(CommandHandler("help", help_command))

    app.run_polling()


if __name__ == "__main__":
    main()
