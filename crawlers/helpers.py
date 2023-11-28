import re
import json
import Levenshtein

def format_string(input_string):
    return input_string.replace("\t", "").replace("\n", "").replace("\r", "")


def slugify(text, separator="-"):
    # Convert to lowercase
    text = text.lower()
    # Replace spaces and special characters with hyphens
    text = re.sub(r"\s+", separator, text)
    # Remove non-alphanumeric characters except hyphens
    text = re.sub(r"[^\w-]", "", text)
    return text

def save_json(filepath, data):
    with open(filepath, "w") as file:
        json.dump(data, file, indent=4)

def read_json(filepath):
    with open(filepath, "r") as file:
        data = json.load(file, indent=4)
    return data


def string_similarity(string1, string2):
    ratio = Levenshtein.ratio(string1, string2)
    return ratio


def find_best_match(product_name, other_sources):
    best_match = None
    highest_similarity = 0

    for source, products in other_sources.items():
        for prod in products:
            other_product_name = " ".join(
                [prod["specification"].get("producer"), prod.get("name", "")]
                if source == "tabletennis_reference_equipments"
                else prod.get("name", "")
            )
            similarity = Levenshtein.ratio(product_name, other_product_name)
            if similarity > highest_similarity:
                highest_similarity = similarity
                best_match = (source, prod)

    return best_match, highest_similarity


def merge_sources(sources, threshold=0.8):
    merged_products = {}

    for source, products in sources.items():
        for product in products:
            product_name_slug = slugify(product.get("name", ""))

            # Prepare the structure if not already present
            if product_name_slug not in merged_products:
                merged_products[product_name_slug] = {}

            other_sources = {s: p for s, p in sources.items() if s != source}
            best_match, similarity = find_best_match(product["name"], other_sources)

            if similarity >= threshold:
                match_source, match_product = best_match
                merged_products[product_name_slug][match_source] = match_product

            merged_products[product_name_slug][source] = product

    return merged_products
