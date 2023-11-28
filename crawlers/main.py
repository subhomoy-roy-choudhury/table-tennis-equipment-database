import sys
import argparse
import avro.schema
from avro.datafile import DataFileWriter
from avro.io import DatumWriter

from equipments import RevSpinEquipments, TableTennisReferenceEquipments
from helpers import merge_sources, save_json, read_json
    
def main(option):
    if option == "blade":
        revspin_data = revspin_equipments.fetch_blades()
        tabletennis_reference_data = tabletennis_reference_equipments.fetch_blades()
        raw_data = {
            "revspin_data": revspin_data,
            "tabletennis_reference_equipments": tabletennis_reference_data,
        }
        save_json(f"data/{option}/raw_data.json", raw_data)
        
        master_json = merge_sources(raw_data)

        save_json(f"data/{option}/master_data.json", master_json)

        # Load schema
        # schema = avro.schema.parse(open("schema.avsc", "rb").read())
        # with open("data/sample_data.json", "r") as file:
        #     data = json.load(file)
        #     # Write data in Avro format
        # with open("data/data.avro", "wb") as file:
        #     writer = DataFileWriter(file, DatumWriter(), schema)
        #     for item in data["revspin_data"]:
        #         writer.append(item)
        #     writer.close()

    else:
        raise Exception("Option Not Implemented")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Example script with arguments")
    parser.add_argument(
        "-o", "--option", help="type you want to fetch", default="blades"
    )
    args = parser.parse_args()
    revspin_equipments = RevSpinEquipments()
    tabletennis_reference_equipments = TableTennisReferenceEquipments()
    main(args.option)

    
    sys.exit()
