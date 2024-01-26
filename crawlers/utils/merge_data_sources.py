import Levenshtein

# def find_largest_list(data):
#     largest_list = []
#     max_list_key = None
#     for key, value in data.items():
#         if len(value) > len(largest_list):
#             largest_list = value
#             max_list_key = key
#     return max_list_key


def find_key_of_largest_list(dict_of_lists):
    # Finding the key of the largest list in the dictionary
    return max(dict_of_lists, key=lambda k: len(dict_of_lists[k]), default=None)


def string_similarity(string1, string2):
    ratio = Levenshtein.ratio(string1, string2)
    return ratio


def merge_sources_v2(sources):
    merged_products = {}
    threshold = 0.8
    key_of_maxlength_source = find_key_of_largest_list(sources)

    if key_of_maxlength_source is not None:
        # Extracting the longest list and its key
        maxlength_source = sources[key_of_maxlength_source]

        # Creating a new dictionary excluding the key of the longest list
        rest_sources = {
            k: v for k, v in sources.items() if k != key_of_maxlength_source
        }

    # fetch similarity list
    for item in maxlength_source:
        product_name = item["name"]
        for source, data in rest_sources.items():
            similar_product_name = None
            similar_product_index = 0
            highest_similarity = 0
            for index, products in enumerate(data):
                other_product_name = " ".join(
                    [
                        products["specification"].get("producer"),
                        products.get("name", ""),
                    ]
                    if source == "tabletennis_reference_equipments"
                    else products.get("name", "")
                )
                similarity = string_similarity(product_name, other_product_name)
                if similarity >= threshold and similarity > highest_similarity:
                    highest_similarity = similarity
                    similar_product_name = other_product_name
                    similar_product_index = index
            if similar_product_name:
                rest_sources[source].pop(similar_product_index)
                merged_products[product_name] = {
                    "similar_product_name": {source: similar_product_name}
                }

    print(merged_products)

    return merged_products
