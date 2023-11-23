import argparse
import json
from crawlers.equipments import RevSpinEquipments, TableTennisReferenceEquipments


def save_data(data):
    with open("data/blades_data.json", "w") as file:
        json.dump(data, file, indent=4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Example script with arguments")
    parser.add_argument(
        "-o", "--option", help="type you want to fetch", default="blades"
    )
    args = parser.parse_args()
    revspin_equipments = RevSpinEquipments()
    tabletennis_reference_equipments = TableTennisReferenceEquipments()

    if args.option == "blade":
        revspin_data = revspin_equipments.fetch_blades()
        tabletennis_reference_data = tabletennis_reference_equipments.fetch_blades()
        data = {
            "revspin_data": revspin_data,
            "tabletennis_reference_equipments": tabletennis_reference_data,
        }
        save_data(data)
    else:
        raise Exception("Option Not Implemented")
