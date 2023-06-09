import redis

k = redis.Redis().from_url("redis://localhost:6379")

k.set("fe", "ff")

print(k.get("fe"))
