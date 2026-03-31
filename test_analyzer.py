from devmap.analyzer import analyze   # make sure filename is analyzer.py

result = analyze(".")

print("FILES:")
print(result["files"])

print("\nFUNCTIONS:")
for k, v in result["functions"].items():
    print(k, ":", v)

print("\nIMPORTS:")
for k, v in result["imports"].items():
    print(k, ":", v)