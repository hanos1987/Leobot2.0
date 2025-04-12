# Leobot2.0
A Discord bot for managing conversations, player cards, tokens, trivia, and more.

## Setup
1. Clone this repository.
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `.env` file based on `.env.example` with your API keys.
4. Create `bot_settings.json` and `config.json` in `data/` based on their example files.
5. Run `python -m leobot.main` to start the bot.

## Commands
- `!time`: Display current times in various cities.
- `!trivia`: Start a trivia game with Open TDB questions.
- `!changecolor`: Select from 20 predefined color roles.
- `!playercard`: Create a player card with personal details.
- `!conversation`: Start a conversation with the bot (GPT-powered).
- `!end_conversation`: End your conversation with the bot.
- `!givetokens`: (Mod) Give sleep tokens to members.
- `!tokens`: Check your sleep token balance.
- `!modcommands`: (Mod) List moderator commands.
- `!summary`: Summarize recent channel conversations (Grok3-powered).
- `!setupleobot`: (Owner) Configure bot settings.
- `!setadmin`, `!setplayercardchannel`, `!settriviachannel`, `!setmodchannel`: (Owner) Adjust specific settings.
