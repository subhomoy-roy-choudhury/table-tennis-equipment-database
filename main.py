import argparse
import json
from crawlers.blades import fetch_blades

def save_data(data):
    with open('data/blades_data.json', 'w') as file:
        json.dump(data, file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Example script with arguments")
    parser.add_argument(
        "-o", "--option", help="type you want to fetch", default="blades"
    )
    args = parser.parse_args()

    if args.option == "blade":
        data = fetch_blades()
        save_data(data)
    else:
        raise Exception("Option Not Implemented")
