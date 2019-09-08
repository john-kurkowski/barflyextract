import json
import sys


def print_markdown(items):
    for item in items:
        print(f"# {item['title']}")
        print()
        print(f"# {item['description']}")


def run():
    items = json.load(sys.stdin)
    print_markdown(items)


if __name__ == "__main__":
    run()
