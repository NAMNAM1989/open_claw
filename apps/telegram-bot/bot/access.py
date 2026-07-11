from telegram import Update


def is_allowed(update: Update, allowed: set[int]) -> bool:
    if not allowed:
        return False
    chat = update.effective_chat
    if not chat:
        return False
    return chat.id in allowed


def chat_id(update: Update) -> int | None:
    chat = update.effective_chat
    return chat.id if chat else None
