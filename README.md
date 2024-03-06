# pyGPT IRC BOT
pyGPT is a simple IRC bot written in Python. It connects to OpenAI endpoints to answer questions.

ChatGPT uses official bindings from OpenAI to interact with the API through HTTP requests: https://platform.openai.com/docs/api-reference


# REQUIREMENTS
Create an account and obtain your API key: https://platform.openai.com/account/api-keys

Install python3 and the official Python bindings:


# INSTALL
* apt install python3 python3-pip (Debian/Ubuntu)
* yum install python3 python3-pip (RedHat/CentOS)
* pip3 install openai pyshorteners
* git clone https://github.com/rootopt/chatgpt.git


# CONFIGURE
* Fetch a OpenAI key from OpenAI.com
* Set the IRC server and Channel to join.
* Edit the botnick and realname.
* Change the IP/Vhost of the bot.
* Decide if you want the bot to connect to SSL or not.


# CONNECTING
* python3 chatgpt.py
* You can use screen to run the bot in background.

# INTERACTING
* The bot will respond if you address it as such.
* Bare in mind, there is a rate limit function.
