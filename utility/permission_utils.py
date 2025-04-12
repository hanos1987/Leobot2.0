from utility.config_utils import bot_settings

def is_mod(user):
    admins = bot_settings.get("admins", [])
    return str(user.id) in admins
