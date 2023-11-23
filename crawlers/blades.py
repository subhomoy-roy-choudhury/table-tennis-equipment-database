import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from crawlers.helpers import format_string

BASE_URL = "https://revspin.net/"


class TableTennisEquipments(object):
    def __init__(self) -> None:
        self.base_url = "https://revspin.net/"
        self.headers = {"User-Agent": "Mozilla/5.0"}

    def table_details(self, table):
        result = {}
        for item in table.find_all("tr"):
            key = format_string(
                item.find("td", {"class": "cell_label"}).text.lower()
            ).replace(" ", "")
            value = format_string(item.find("td", {"class": "cell_rating"}).text)
            result[key] = value
        return result

    def fetch_blade_details(self, url):
        response = requests.get(url, headers=self.headers, data={})
        details = {}
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            product_details = soup.find("table", {"id": "UserRatingsTable"})
            manufacturer_details_table = soup.find_all(
                "table", {"class": "ProductRatingTable"}
            )[1]
            product_image_element = soup.find("img", {"class": "product_detail_image"})
            product_image = (
                product_image_element.get("src", None)
                if product_image_element
                else None
            )

            details = {
                **self.table_details(product_details),
                "manufacturer_details": self.table_details(manufacturer_details_table),
                "product_image": product_image,
            }
        return details

    def fetch_blades(self):
        # Create a session object
        session = requests.Session()
        url = f"{self.base_url}blade/"
        response = session.request("GET", url, headers=self.headers, data={})

        ## Check if the request was successful
        if response.status_code == 200:
            res_blades_list = []
            soup = BeautifulSoup(response.content, "html.parser")
            blades_div_list = soup.find_all(
                lambda tag: tag.name == "div" and tag.get("id", "").startswith("brand-")
            )
            for blades_div in blades_div_list:
                brand_name = blades_div["id"]
                print(f"Scraping Tables Tennis Blade {brand_name.upper()}")
                for blade_stats_divs in tqdm(
                    blades_div.find_all(
                        lambda tag: tag.name == "tr"
                        and "head" not in tag.get("class", "")
                    ),
                    desc="Processing",
                ):
                    name = blade_stats_divs.find("td", {"class": "cell_name"}).text
                    url = f'{self.base_url}{blade_stats_divs.find("td", {"class": "cell_name"}).find("a")["href"]}'
                    speed = format_string(
                        blade_stats_divs.find_all("td", {"class": "cell_char"})[0].text
                    )
                    control = format_string(
                        blade_stats_divs.find(
                            "td", {"class": "cell_char cell_even"}
                        ).text
                    )
                    stiffness = format_string(
                        blade_stats_divs.find_all("td", {"class": "cell_char"})[2].text
                    )
                    overall = blade_stats_divs.find(
                        "td", {"class": "cell_overall"}
                    ).text
                    price = blade_stats_divs.find("td", {"class": "cell_price"}).text
                    rating = blade_stats_divs.find(
                        "td", {"class": "cell_numratings"}
                    ).text

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
                            "url": url,
                            **self.fetch_blade_details(url),
                        }
                    )

            print("Blade scraping Completed Successfully !")
            return res_blades_list
        else:
            print("Failed to retrieve the webpage")
