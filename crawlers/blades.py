import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from crawlers.helpers import format_string

BASE_URL = "https://revspin.net/"


class TableTennisEquipments(object):
    def __init__(self) -> None:
        self.base_url = "https://revspin.net/"
        self.headers = {"User-Agent": "Mozilla/5.0"}
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def table_details(self, table):
        # Assuming format_string is a predefined function
        key_list = [
            format_string(key.text.lower()).replace(" ", "")
            for key in table.find_all("td", {"class": "cell_label"})
        ]
        value_list = [
            format_string(value.text)
            for value in table.find_all("td", {"class": "cell_rating"})
        ]

        return dict(zip(key_list, value_list))

    def fetch_blade_details(self, url):
        details = {}
        try:
            response = self.session.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser")

                product_details = soup.select_one("#UserRatingsTable")
                manufacturer_details = soup.select(".ProductRatingTable")[1]
                product_image = soup.select_one(".product_detail_image")

                details = {
                    **self.table_details(product_details),
                    "manufacturer_details": self.table_details(manufacturer_details),
                    "product_image": product_image.get("src", None)
                    if product_image
                    else None,
                }
        except Exception as e:
            # Handle exceptions (e.g., network issues, parsing errors)
            print(f"Error fetching details: {e}")
        return details

    def fetch_blades(self):
        url = f"{self.base_url}blade/"
        response = self.session.get(url, headers=self.headers)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            blades_div_list = soup.select("div[id^='brand-']")
            res_blades_list = []

            for blades_div in blades_div_list:
                brand_name = blades_div["id"]
                print(f"===== Scraping Table Tennis Blade: {brand_name.upper()} =====")
                blade_rows = blades_div.select("tr:not(.head)")

                for blade_row in tqdm(blade_rows, desc="Processing"):
                    cells = blade_row.select("td")
                    url = f'{self.base_url}{cells[0].select_one("a")["href"]}'
                    blade_details = {
                        "name": cells[0].text.strip(),
                        "url": url,
                        "speed": format_string(cells[1].text.strip()),
                        "control": format_string(cells[2].text.strip()),
                        "stiffness": format_string(cells[3].text.strip()),
                        "overall": cells[4].text.strip(),
                        "price": cells[5].text.strip(),
                        "rating": cells[6].text.strip(),
                        "brand_name": brand_name,
                        **self.fetch_blade_details(url),
                    }
                    res_blades_list.append(blade_details)

            print("Blade scraping Completed Successfully !")
            return res_blades_list
        else:
            print("Failed to retrieve the webpage")
            return []