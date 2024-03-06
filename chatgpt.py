import ssl
import time
import openai
from irc.bot import SingleServerIRCBot
from irc.connection import Factory
from collections import defaultdict, deque
from threading import Lock

# Configuration
OPENAI_API_KEY = 'sk-'
SERVER = 'irc.efnet.org'
CHANNEL = '#computers'
NICKNAME = 'krashed'
REALNAME = 'evil'
RATE_LIMIT_SECONDS = 10
MAX_HISTORY_PER_USER = 5
MESSAGE_CHUNK_SIZE = 450
LOCAL_BIND_IP = 'vhost'  # Specify the IP address to bind to
USE_SSL = True
PORT = 6697 if USE_SSL else 6667
openai.api_key = 'sk-'

class RateLimiter:
    def __init__(self, rate_limit_seconds):
        self.rate_limit_seconds = rate_limit_seconds
        self.last_message_time = defaultdict(lambda: 0)
        self.lock = Lock()

    def is_allowed(self, user):
        with self.lock:
            current_time = time.time()
            if current_time - self.last_message_time[user] < self.rate_limit_seconds:
                return False
            self.last_message_time[user] = current_time
            return True

class ContextManager:
    """Manages context for personalized responses."""
    def __init__(self, max_history):
        self.user_history = defaultdict(lambda: deque(maxlen=max_history))

    def add_message(self, user, message):
        self.user_history[user].append(message)

    def get_history(self, user):
        return [{'role': 'user', 'content': msg} for msg in self.user_history[user]]

def split_message(message, chunk_size=MESSAGE_CHUNK_SIZE):
    """Splits message into specified chunk sizes."""
    return [message[i:i+chunk_size] for i in range(0, len(message), chunk_size)]


class GPTBot(SingleServerIRCBot):
    def __init__(self):
        # Initialize RateLimiter here
        self.rate_limiter = RateLimiter(RATE_LIMIT_SECONDS)
        self.context_manager = ContextManager(MAX_HISTORY_PER_USER)

        # Setup Factory for connection, with or without SSL
        if USE_SSL:
            ssl_factory = Factory(wrapper=ssl.wrap_socket, bind_address=(LOCAL_BIND_IP,0))
        else:
            ssl_factory = Factory(bind_address=(LOCAL_BIND_IP,0))

        # Initialize the bot
        super().__init__(server_list=[(SERVER, PORT)], nickname=NICKNAME, realname=REALNAME, connect_factory=ssl_factory)
        self.channel = CHANNEL

    def on_welcome(self, connection, event):
        connection.join(self.channel)
        print(f"Joined {CHANNEL}")

    def on_ping(self, connection, event):
        connection.pong(event.target)

    def on_pubmsg(self, connection, event):
        user = event.source.nick
        message = event.arguments[0]
        if not self.rate_limiter.is_allowed(user):
            return  # Enforce rate limiting
        
        self.context_manager.add_message(user, message)
        if message.strip().startswith(NICKNAME):
            self.respond(connection, event.target, user)

    def generate_response_and_send(self, connection, target, user):
        # Make sure to use self.rate_limiter here
        if not self.rate_limiter.is_allowed(user):
            return  # Skip processing if rate limit exceeded

    def respond(self, connection, target, user):
        context_messages = self.context_manager.get_history(user)
        try:
            response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=context_messages)
            reply = response.choices[0].message['content']
            sanitized_reply = reply.replace('\r', '').replace('\n', ' ')  # Sanitize reply
            for chunk in split_message(sanitized_reply):
                connection.privmsg(target, f"{user}: {chunk}")
                time.sleep(1)  # Prevent flooding
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    bot = GPTBot()
    bot.start()
