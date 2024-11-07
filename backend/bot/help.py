from .db_functions import get_all_admin_telegram_ids


async def is_admin(user_id):
    admin_list = await get_all_admin_telegram_ids()
    return user_id in admin_list
