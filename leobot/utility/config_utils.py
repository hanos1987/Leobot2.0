import json

def load_bot_settings():
    try:
        with open('data/bot_settings.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "colorRoles": {
                "Red": "#FF0000",
                "Green": "#00FF00",
                "Blue": "#0000FF",
                "Yellow": "#FFFF00",
                "Purple": "#800080",
                "Cyan": "#00FFFF",
                "Orange": "#FF6600",
                "Pink": "#FFC0CB",
                "Brown": "#A52A2A",
                "Gray": "#808080",
                "Navy": "#000080",
                "Teal": "#008080",
                "Violet": "#EE82EE",
                "Salmon": "#FA8072",
                "Gold": "#FFD700",
                "Silver": "#C0C0C0",
                "Turquoise": "#40E0D0",
                "Magenta": "#FF00FF",
                "The Archive": "#9bdeed",
                "Lime": "#00FF00"
            }
        }

def save_bot_settings(data):
    os.makedirs('data', exist_ok=True)
    with open('data/bot_settings.json', 'w') as f:
        json.dump(data, f, indent=4)

bot_settings = load_bot_settings()
