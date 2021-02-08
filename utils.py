import string
import random


def random_str():
    return ''.join(random.choices(string.ascii_uppercase +
                                  string.digits, k=8))
# stream_recorder({'uri' : url, 'uuid': uuid})

# thread = threading.Thread(target=stream_recorder, args=(url, uuid))
# thread.start()
# threads.append((thread, uuid))
