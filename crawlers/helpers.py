import re


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
