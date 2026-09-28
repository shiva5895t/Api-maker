import os
import threading
from datetime import datetime, timezone, timedelta

import uvicorn

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

import database
from api import app as fastapi_app


APP_NAME = "KRUTIK CYBER EXPERT API"

BOT_TOKEN = os.getenv(
    "BOT_TOKEN",
    "",
).strip()

OWNER_CHAT_ID = os.getenv(
    "OWNER_CHAT_ID",
    "",
).strip()

PORT = int(
    os.getenv(
        "PORT",
        "10000",
    )
)


# =========================================================
# HELPERS
# =========================================================

def is_owner(user_id):
    return (
        OWNER_CHAT_ID
        and str(user_id)
        == str(OWNER_CHAT_ID)
    )


async def owner_only(update):
    user = update.effective_user

    if not is_owner(user.id):
        if update.message:
            await update.message.reply_text(
                "❌ Owner only."
            )
        return False

    return True


def back_markup():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🔙 Back",
                callback_data="home",
            )
        ]
    ])


# =========================================================
# USER MENU
# =========================================================

def user_menu():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                database.get_setting(
                    "button_plans",
                    "🔑 API Plans",
                ),
                callback_data="plans",
            )
        ],
        [
            InlineKeyboardButton(
                database.get_setting(
                    "button_request",
                    "🚀 Request API Access",
                ),
                callback_data="request",
            )
        ],
        [
            InlineKeyboardButton(
                database.get_setting(
                    "button_keys",
                    "🔐 My API Keys",
                ),
                callback_data="keys",
            )
        ],
        [
            InlineKeyboardButton(
                database.get_setting(
                    "button_usage",
                    "📊 My Usage",
                ),
                callback_data="usage",
            )
        ],
        [
            InlineKeyboardButton(
                database.get_setting(
                    "button_howto",
                    "📖 How to Use API",
                ),
                callback_data="howto",
            )
        ],
        [
            InlineKeyboardButton(
                database.get_setting(
                    "button_docs",
                    "📚 API Docs",
                ),
                callback_data="docs",
            )
        ],
        [
            InlineKeyboardButton(
                database.get_setting(
                    "button_support",
                    "🆘 Support",
                ),
                callback_data="support",
            )
        ],
    ])


# =========================================================
# ADMIN MENU
# =========================================================

def admin_menu():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "📊 Dashboard",
                callback_data="admin_dashboard",
            )
        ],
        [
            InlineKeyboardButton(
                "📨 Requests",
                callback_data="admin_pending",
            )
        ],
        [
            InlineKeyboardButton(
                "👥 Users",
                callback_data="admin_users",
            ),
        ],
        [
            InlineKeyboardButton(
                "🔑 API Keys",
                callback_data="admin_keys",
            ),
        ],
        [
            InlineKeyboardButton(
                "📈 Usage",
                callback_data="admin_usage",
            ),
        ],
        [
            InlineKeyboardButton(
                "🎨 Customize Panel",
                callback_data="admin_customize",
            ),
        ],
        [
            InlineKeyboardButton(
                "⚙️ API Settings",
                callback_data="admin_settings",
            ),
        ],
        [
            InlineKeyboardButton(
                "🟢 API ON",
                callback_data="admin_apion",
            ),
            InlineKeyboardButton(
                "🔴 API OFF",
                callback_data="admin_apioff",
            ),
        ],
        [
            InlineKeyboardButton(
                "📖 API Docs",
                callback_data="admin_docs",
            )
        ],
    ])


# =========================================================
# START
# =========================================================

async def start_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    user = update.effective_user

    database.save_user(
        user.id,
        user.username,
        user.first_name,
    )

    if database.is_user_blocked(
        user.id
    ):
        await update.message.reply_text(
            "🚫 Access blocked."
        )
        return

    await update.message.reply_text(
        database.get_setting(
            "welcome_text",
            "Welcome!",
        ),
        reply_markup=user_menu(),
    )


# =========================================================
# ADMIN
# =========================================================

async def admin_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if not await owner_only(update):
        return

    await update.message.reply_text(
        f"👑 {APP_NAME}\n\n"
        "ADMIN PANEL",
        reply_markup=admin_menu(),
    )


# =========================================================
# USER CALLBACKS
# =========================================================

async def plans_callback(
    update,
    context,
):
    query = update.callback_query
    await query.answer()

    basic_daily = database.get_setting(
        "basic_daily",
        "1000",
    )

    basic_days = database.get_setting(
        "basic_days",
        "30",
    )

    pro_daily = database.get_setting(
        "pro_daily",
        "10000",
    )

    pro_days = database.get_setting(
        "pro_days",
        "30",
    )

    custom_daily = database.get_setting(
        "custom_daily",
        "50000",
    )

    custom_days = database.get_setting(
        "custom_days",
        "30",
    )

    text = (
        f"🔑 {APP_NAME}\n\n"
        "API PLANS\n\n"
        f"🟢 BASIC\n"
        f"• {basic_daily} requests/day\n"
        f"• {basic_days} days\n\n"
        f"🔵 PRO\n"
        f"• {pro_daily} requests/day\n"
        f"• {pro_days} days\n\n"
        f"🟣 CUSTOM\n"
        f"• {custom_daily} requests/day\n"
        f"• {custom_days} days\n\n"
        "Access requires owner approval."
    )

    await query.edit_message_text(
        text,
        reply_markup=back_markup(),
    )


async def request_callback(
    update,
    context,
):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [
            InlineKeyboardButton(
                "🟢 Basic",
                callback_data="request_basic",
            )
        ],
        [
            InlineKeyboardButton(
                "🔵 Pro",
                callback_data="request_pro",
            )
        ],
        [
            InlineKeyboardButton(
                "🟣 Custom",
                callback_data="request_custom",
            )
        ],
        [
            InlineKeyboardButton(
                "🔙 Back",
                callback_data="home",
            )
        ],
    ]

    await query.edit_message_text(
        "🚀 Select API plan:",
        reply_markup=InlineKeyboardMarkup(
            keyboard
        ),
    )


async def submit_request_callback(
    update,
    context,
):
    query = update.callback_query
    await query.answer()

    user = query.from_user

    plan = query.data.replace(
        "request_",
        "",
    )

    request_id = (
        database.create_access_request(
            user.id,
            user.username,
            plan,
        )
    )

    if OWNER_CHAT_ID:
        try:
            keyboard = [[
                InlineKeyboardButton(
                    "✅ Approve",
                    callback_data=(
                        f"approve_{request_id}"
                    ),
                ),
                InlineKeyboardButton(
                    "❌ Reject",
                    callback_data=(
                        f"reject_{request_id}"
                    ),
                ),
            ]]

            await context.bot.send_message(
                chat_id=int(OWNER_CHAT_ID),
                text=(
                    f"🔔 {APP_NAME}\n\n"
                    "NEW API REQUEST\n\n"
                    f"Request ID: {request_id}\n"
                    f"User ID: {user.id}\n"
                    f"Username: "
                    f"@{user.username or 'none'}\n"
                    f"Plan: {plan.upper()}"
                ),
                reply_markup=InlineKeyboardMarkup(
                    keyboard
                ),
            )

        except Exception as exc:
            print(
                "OWNER NOTIFICATION ERROR:",
                exc,
            )

    await query.edit_message_text(
        f"✅ Request submitted.\n\n"
        f"Request ID: {request_id}\n"
        f"Plan: {plan.upper()}\n\n"
        "Please wait for owner approval.",
        reply_markup=back_markup(),
    )


async def keys_callback(
    update,
    context,
):
    query = update.callback_query
    await query.answer()

    keys = database.get_user_keys(
        query.from_user.id
    )

    if not keys:
        await query.edit_message_text(
            "🔐 You don't have any API keys.",
            reply_markup=back_markup(),
        )
        return

    lines = [
        "🔐 YOUR API KEYS",
        "",
    ]

    for key in keys:
        lines.extend([
            f"🆔 ID: {key['id']}",
            f"📛 Name: {key['key_name']}",
            f"📦 Plan: {key['plan'].upper()}",
            f"📌 Status: {key['status']}",
            f"📊 Today: "
            f"{key['today_requests']}/"
            f"{key['daily_limit']}",
            f"📈 Total: "
            f"{key['total_requests']}/"
            f"{key['total_limit'] or '∞'}",
            f"⏱ Rate/min: "
            f"{key['rate_limit'] or '∞'}",
            f"⌛ Expiry: "
            f"{key['expires_at'] or 'Never'}",
            "",
        ])

    await query.edit_message_text(
        "\n".join(lines),
        reply_markup=back_markup(),
    )


async def usage_callback(
    update,
    context,
):
    query = update.callback_query
    await query.answer()

    keys = database.get_user_keys(
        query.from_user.id
    )

    if not keys:
        await query.edit_message_text(
            "📊 No API usage found.",
            reply_markup=back_markup(),
        )
        return

    lines = [
        "📊 MY API USAGE",
        "",
    ]

    for key in keys:
        daily_remaining = max(
            0,
            key["daily_limit"]
            - key["today_requests"],
        )

        total_remaining = (
            "∞"
            if key["total_limit"] is None
            else max(
                0,
                key["total_limit"]
                - key["total_requests"],
            )
        )

        lines.extend([
            f"🔑 {key['key_name']}",
            f"Today: "
            f"{key['today_requests']}/"
            f"{key['daily_limit']}",
            f"Remaining: {daily_remaining}",
            f"Total: "
            f"{key['total_requests']}/"
            f"{key['total_limit'] or '∞'}",
            f"Total Remaining: "
            f"{total_remaining}",
            "",
        ])

    await query.edit_message_text(
        "\n".join(lines),
        reply_markup=back_markup(),
    )


async def howto_callback(
    update,
    context,
):
    query = update.callback_query
    await query.answer()

    api_url = database.get_setting(
        "api_url"
    )

    text = database.get_setting(
        "howto_text"
    )

    text += (
        f"\n\nEndpoint:\n"
        f"{api_url}/api/search\n\n"
        "Example:\n"
        f"{api_url}/api/search?"
        "api_key=YOUR_KEY&"
        "query=TEST&limit=20\n\n"
        f"Docs:\n"
        f"{api_url}/docs"
    )

    await query.edit_message_text(
        text,
        reply_markup=back_markup(),
    )


async def docs_callback(
    update,
    context,
):
    query = update.callback_query
    await query.answer()

    api_url = database.get_setting(
        "api_url"
    )

    text = database.get_setting(
        "docs_text"
    )

    text += (
        f"\n\n{api_url}/docs"
    )

    await query.edit_message_text(
        text,
        reply_markup=back_markup(),
    )


async def support_callback(
    update,
    context,
):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        database.get_setting(
            "support_text"
        ),
        reply_markup=back_markup(),
    )


# =========================================================
# ADMIN CALLBACK
# =========================================================

async def admin_callback(
    update,
    context,
):
    query = update.callback_query
    await query.answer()

    if not is_owner(
        query.from_user.id
    ):
        await query.answer(
            "Owner only.",
            show_alert=True,
        )
        return

    data = query.data

    if data == "admin_dashboard":

        stats = database.get_usage_stats()

        status = (
            "🟢 ON"
            if stats["global_api_enabled"]
            else "🔴 OFF"
        )

        await query.edit_message_text(
            f"📊 {APP_NAME}\n\n"
            f"API: {status}\n\n"
            f"👥 Users: {stats['users']}\n"
            f"🚫 Blocked: {stats['blocked']}\n"
            f"🔑 Keys: {stats['keys']}\n"
            f"🟢 Active: {stats['active_keys']}\n"
            f"🔒 Revoked: {stats['revoked_keys']}\n"
            f"⌛ Expired: {stats['expired_keys']}\n"
            f"📈 Requests: {stats['requests']}\n"
            f"✅ Success: {stats['successful']}\n"
            f"❌ Failed: {stats['failed']}\n"
            f"📨 Pending: {stats['pending']}\n"
            f"📊 Total Usage: {stats['total_usage']}",
            reply_markup=admin_menu(),
        )
        return

    if data == "admin_pending":

        requests = database.get_pending_requests()

        if not requests:
            text = "📨 No pending requests."

        else:
            lines = [
                "📨 PENDING REQUESTS",
                "",
            ]

            for req in requests:
                lines.extend([
                    f"ID: {req['id']}",
                    f"User: {req['chat_id']}",
                    f"Plan: {req['plan'].upper()}",
                    "",
                ])

            text = "\n".join(lines)

        await query.edit_message_text(
            text,
            reply_markup=admin_menu(),
        )
        return

    if data == "admin_users":

        users = database.get_users(50)

        lines = [
            "👥 USERS",
            "",
        ]

        for user in users:
            lines.append(
                f"{'🚫' if user['blocked'] else '🟢'} "
                f"{user['chat_id']} "
                f"@{user['username'] or 'none'}"
            )

        await query.edit_message_text(
            "\n".join(lines),
            reply_markup=admin_menu(),
        )
        return

    if data == "admin_keys":

        keys = database.get_all_keys(50)

        lines = [
            "🔑 API KEYS",
            "",
        ]

        for key in keys:
            lines.extend([
                f"ID: {key['id']}",
                f"User: {key['chat_id']}",
                f"Name: {key['key_name']}",
                f"Plan: {key['plan'].upper()}",
                f"Status: {key['status']}",
                "",
            ])

        await query.edit_message_text(
            "\n".join(lines),
            reply_markup=admin_menu(),
        )
        return

    if data == "admin_usage":

        logs = database.get_recent_logs(30)

        lines = [
            "📈 RECENT API USAGE",
            "",
        ]

        for log in logs:
            icon = (
                "✅"
                if log["success"]
                else "❌"
            )

            lines.append(
                f"{icon} "
                f"User:{log['chat_id']} "
                f"HTTP:{log['status_code']} "
                f"Query:{log['query'][:30]}"
            )

        await query.edit_message_text(
            "\n".join(lines) or "No requests.",
            reply_markup=admin_menu(),
        )
        return

    if data == "admin_customize":

        await query.edit_message_text(
            "🎨 CUSTOMIZE USER PANEL\n\n"
            "Commands:\n\n"
            "/setwelcome TEXT\n"
            "/setsupport TEXT\n"
            "/sethowto TEXT\n"
            "/setdocs TEXT\n"
            "/setapiurl URL\n\n"
            "Button names:\n"
            "/setbutton plans TEXT\n"
            "/setbutton request TEXT\n"
            "/setbutton keys TEXT\n"
            "/setbutton usage TEXT\n"
            "/setbutton howto TEXT\n"
            "/setbutton docs TEXT\n"
            "/setbutton support TEXT\n\n"
            "Plans:\n"
            "/setplan basic DAILY DAYS\n"
            "/setplan pro DAILY DAYS\n"
            "/setplan custom DAILY DAYS",
            reply_markup=admin_menu(),
        )
        return

    if data == "admin_settings":

        files = os.listdir(
            os.getenv("DATA_DIR", "data")
        ) if os.path.exists(
            os.getenv("DATA_DIR", "data")
        ) else []

        json_count = len([
            x for x in files
            if x.lower().endswith(".json")
        ])

        await query.edit_message_text(
            f"⚙️ API SETTINGS\n\n"
            f"API: "
            f"{'🟢 ON' if database.is_global_api_enabled() else '🔴 OFF'}\n"
            f"JSON datasets: {json_count}\n"
            f"API URL:\n"
            f"{database.get_setting('api_url')}",
            reply_markup=admin_menu(),
        )
        return

    if data == "admin_apion":

        database.set_global_api_enabled(True)

        await query.edit_message_text(
            "🟢 Global API enabled.",
            reply_markup=admin_menu(),
        )
        return

    if data == "admin_apioff":

        database.set_global_api_enabled(False)

        await query.edit_message_text(
            "🔴 Global API disabled.",
            reply_markup=admin_menu(),
        )
        return

    if data == "admin_docs":

        api_url = database.get_setting(
            "api_url"
        )

        await query.edit_message_text(
            f"📖 API DOCS\n\n"
            f"{api_url}/docs\n\n"
            f"{api_url}/health\n\n"
            f"{api_url}/api/stats",
            reply_markup=admin_menu(),
        )
        return

    if data == "home":

        await query.edit_message_text(
            database.get_setting(
                "welcome_text"
            ),
            reply_markup=user_menu(),
        )
        return


# =========================================================
# APPROVE / REJECT
# =========================================================

async def owner_decision(
    update,
    context,
):
    query = update.callback_query
    await query.answer()

    if not is_owner(
        query.from_user.id
    ):
        return

    data = query.data

    request_id = int(
        data.split("_")[-1]
    )

    request = database.get_access_reques
