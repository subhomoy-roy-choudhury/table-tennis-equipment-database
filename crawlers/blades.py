import requests
from bs4 import BeautifulSoup

url = "https://revspin.net/blade/"


def match_id(tag):
    return tag.name == "div" and tag.get("id", "").startswith("brand-")


def fetch_blades():
    # Create a session object
    session = requests.Session()
    url = "https://revspin.net/blade/"

    payload = {}
    headers = {"User-Agent": "Mozilla/5.0"}

    response = session.request("GET", url, headers=headers, data=payload)

    ## Check if the request was successful
    if response.status_code == 200:

        def match_id(tag):
            return tag.name == "tr" and "head" not in tag.get("class", "")

        res_blades_list = []
        soup = BeautifulSoup(response.content, "html.parser")
        blades_div_list = soup.find_all(
            lambda tag: tag.name == "div" and tag.get("id", "").startswith("brand-")
        )
        for blades_div in blades_div_list:
            brand_name = blades_div["id"]
            for blade_stats_divs in blades_div.find_all(
                match_id
                # lambda tag: tag.name == "tr" and tag.get("class", "") != "head"
            ):
                name = blade_stats_divs.find("td", {"class": "cell_name"}).text
                speed = (
                    blade_stats_divs.find_all("td", {"class": "cell_char"})[0]
                    .text.replace("\t", "")
                    .replace("\n", "")
                )
                control = (
                    blade_stats_divs.find("td", {"class": "cell_char cell_even"})
                    .text.replace("\t", "")
                    .replace("\n", "")
                )
                stiffness = (
                    blade_stats_divs.find_all("td", {"class": "cell_char"})[2]
                    .text.replace("\t", "")
                    .replace("\n", "")
                )
                overall = blade_stats_divs.find("td", {"class": "cell_overall"}).text
                price = blade_stats_divs.find("td", {"class": "cell_price"}).text
                rating = blade_stats_divs.find("td", {"class": "cell_numratings"}).text

                res_blades_list.append(
                    {
                        "name": name,
                        "brand_name": brand_name,
                        "speed": speed,
                        "control": control,
                        "stiffness": stiffness,
                        "overall": overall,
                        "price": price,
                        "rating": rating,
                    }
                )
        
        print("Blade scraping Completed Successfully !")
    else:
        print("Failed to retrieve the webpage")
