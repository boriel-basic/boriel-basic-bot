# Boriel BASIC Bot Helper
Welcome to the Boriel BASIC Bot Helper project!
This bot is designed to assist users with Boriel BASIC
documentation and code snippets through a Telegram bot interface.
Below you will find detailed information on how to set up and run this bot.

## Table of Contents
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Available Commands](#available-commands)
- [Code Overview](#code-overview)
- [Contributing](#contributing)
- [License](#license)

## Installation

### Prerequisites
- Python 3.8+
- A Telegram bot token from [BotFather](https://core.telegram.org/bots#botfather)
- ChromaDB installed and configured
- Necessary Python packages

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/boriel-basic-bot-helper.git
   cd boriel-basic-bot-helper
   ```
2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up your environment variable for the Telegram bot token:
   ```bash
   export BOT_TOKEN='your-telegram-bot-token'
   ```

## Configuration

### JSON Files
- **.users.json**: Contains the list of allowed users.
- **.admin_users.json**: Contains the list of admin users.

### Directory Structure
- **memory/**: Directory where conversations are stored in JSON format.

## Usage
To run the bot, execute the following command:

```bash
python bot.py
```

The bot will start polling and waiting for messages from users.

## Available Commands

### User Management

- `/adduser <user_id>`: Add a new user to the allowed users list. (Admin only)
- `/deluser <user_id>`: Delete a user from the allowed users list. (Admin only)
- `/promote <user_id>`: Promote a user to admin. (Admin only)
- `/demote <user_id>`: Demote an admin to a regular user. (Admin only)
- `/listusers`: List all allowed users and their admin status. (Admin only)

### General

- `/start`: Start interaction with the bot.
- `/help`: Display available commands.

## Code Overview

### Main Components

- **Command Enumeration**: Defines the bot commands.
- **User Management Functions**: Add, delete, promote, and demote users.
- **Message Handlers**: Handle incoming messages and execute commands.
- **Conversation Management**: Load, save, and manage user conversations.
- **Main Function**: Initialize the bot and start polling.

### Key Functions

- `is_user_allowed(message)`: Check if a user is allowed.
- `is_admin(message)`: Check if a user is an admin.
- `escape_markdown(text)`: Escape markdown characters for safe message formatting.
- `load_conversation(username)`: Load user conversation from JSON.
- `save_conversation(username, conversation)`: Save user conversation to JSON.
- `main()`: Initialize bot, load allowed users, and start the bot.

## Contributing

We welcome contributions! Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Commit your changes and push to your branch.
4. Create a pull request describing your changes.

## License

This project is licensed under the aGPLv3 License. See the [LICENSE](LICENSE) file for details.

---
Feel free to reach out if you have any questions or need further assistance. Happy coding!
