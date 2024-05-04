import hashlib
import json
import time
import logging

import redis

FORMAT = "[%(asctime)s] %(levelname).1s %(message)s"
logging.basicConfig(format=FORMAT, level=logging.INFO)
LOGGER = logging.getLogger(__name__)


class Store:
    r = redis.Redis()
    cache = {}
    cache_time = 60

    def is_connected(self):
        try:
            self.r.ping()
            return True
        except redis.exceptions.ConnectionError:
            for i in range(0, 1):
                time.sleep(1)
                try:
                    return self.r.ping()
                except redis.exceptions.ConnectionError:
                    continue
            return False

    def cache_get(self, key):
        try:
            if self.is_connected():
                result = self.r.get(key)
                if result:
                    return float(result)
                else:
                    return None
            else:
                raise TimeoutError
        except TimeoutError as e:
            LOGGER.info(f"Не удалось подключиться к redis: {e}")
            try:
                return self.cache[key]
            except KeyError:
                LOGGER.info("Нет запрашиваемого значения")
                return None

    def cache_set(self, key, val, time):
        try:
            if self.is_connected():
                if isinstance(val, list):
                    return self.r.lpush(key, *val)
                return self.r.set(key, val)
            else:
                raise TimeoutError
        except TimeoutError as e:
            LOGGER.info(f"Не удалось подключиться к redis: {e}")
            self.cache[key] = val
            self.cache_time = time

    def get(self, arg):
        k = arg.split(":")[1]
        key = "uid:" + hashlib.md5("".join(str(k)).encode("utf-8")).hexdigest()
        data = []
        try:
            if self.is_connected():
                data = self.r.lrange(key, 0, -1)
                data = [el.decode("utf-8") for el in data]
            else:
                raise TimeoutError
        except TimeoutError as e:
            LOGGER.info(f"Не удалось подключиться к redis: {e}")
            data = self.cache[key]
        finally:
            return json.dumps({k: data})

    def clear_cache(self):
        try:
            if self.is_connected():
                return self.r.flushdb()
            else:
                raise TimeoutError
        except TimeoutError as e:
            LOGGER.info(f"Не удалось подключиться к redis: {e}")
            self.cache.clear()
