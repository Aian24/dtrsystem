import re
with open("login.html", "r", encoding="utf-8") as f:
    html = f.read()
classes = set(re.findall(r'max-w-[a-zA-Z0-9\-\[\]]+', html))
print(classes)
