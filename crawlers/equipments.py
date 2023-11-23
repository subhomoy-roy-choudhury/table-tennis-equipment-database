import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from crawlers.helpers import format_string, slugify


class RevSpinEquipments(object):
    def __init__(self) -> None:
        self.base_url = "https://revspin.net"
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
                    "product_image": f'{self.base_url}{product_image.get("src", None)}'
                    if product_image
                    else None,
                }
        except Exception as e:
            # Handle exceptions (e.g., network issues, parsing errors)
            print(f"Error fetching details: {e}")
        return details

    def fetch_blades(self):
        url = f"{self.base_url}/blade/"
        response = self.session.get(url, headers=self.headers)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            blades_div_list = soup.select("div[id^='brand-']")
            res_blades_list = []

            def process_blade_row(blade_row, brand_name):
                cells = blade_row.select("td")
                url = f'{self.base_url}/{cells[0].select_one("a")["href"]}'
                return {
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

            with ThreadPoolExecutor() as executor:
                for blades_div in blades_div_list:
                    brand_name = blades_div["id"]
                    print(f"===== Scraping Table Tennis Blade: {brand_name.upper()} =====")
                    blade_rows = blades_div.select("tr:not(.head)")
                    futures = [executor.submit(process_blade_row, blade_row, brand_name) for blade_row in blade_rows]
                    for future in tqdm(futures, desc=f"Processing {brand_name.upper()}"):
                        res_blades_list.append(future.result())

            print("Blade scraping Completed Successfully!")
            return res_blades_list
        else:
            print("Failed to retrieve the webpage")
            return []


class TableTennisReferenceEquipments(object):
    def __init__(self) -> None:
        self.base_url = "https://tabletennis-reference.com/"
        self.headers = {"User-Agent": "Mozilla/5.0"}
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def table_details(self, table):
        # Assuming format_string is a predefined function
        key_list = [
            format_string(key.text.lower()).replace(" ", "")
            for key in table.find_all("dt")
        ]
        value_list = [
            format_string(value.text).strip("  ") for value in table.find_all("dd")
        ]

        return dict(zip(key_list, value_list))

    def fetch_blade_details(self, url) -> dict:
        response = self.session.get(url)
        details = {}
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")

            # Fetch Images
            images_list = [img["src"] for img in soup.select("div.floatL img[src]")]

            # Description
            description = (
                format_string(soup.select_one("dl.desc").text)
                if soup.select_one("dl.desc")
                else ""
            )

            # Everyone's Rating
            everyones_rating_string = (
                soup.select_one("td.top-content").text.strip()
                if soup.select_one("td.top-content")
                else ""
            )

            # Evaluation and no. of Reviews
            evaluation_review_details = {
                slugify(item.text.split(": ")[0].lower()): item.text.split(": ")[1]
                for item in soup.select("div.pointBox li")
                if ": " in item.text
            }

            # Variants
            variants = [variant.text for variant in soup.select("ul.sizeBox li")]

            # Specification
            spec_table = soup.select_one("div.dataBox2")
            specification = self.table_details(spec_table) if spec_table else {}

            # Players
            players_list = [
                format_string(player.text) for player in soup.select("em.slantGray")
            ]

            # User Reviews
            user_review_details = []
            for user_review_div in soup.select("div#usrRevBlk li[id^='review_']"):
                dt_tag = user_review_div.select_one("dt.usrBox.clearfix")

                experience = (
                    dt_tag.select_one("p").contents[-3].strip()
                    if dt_tag and dt_tag.select_one("p")
                    else None
                )
                comment = (
                    dt_tag.select_one("p span").text
                    if dt_tag and dt_tag.select_one("p span")
                    else None
                )
                long_comment = user_review_div.select_one("div.comnt p").text

                user_stats = user_review_div.select_one("div.floatR")
                key_list = [
                    format_string(key.text.lower()).replace(" ", "")
                    for key in user_stats.select("th")
                ]
                value_list = [
                    format_string(value.text).strip()
                    for value in user_stats.select("td")
                ]

                stats = dict(zip(key_list, value_list))

                recommended_rubber_div = user_review_div.select_one("div.recomRub")
                key_list = [
                    format_string(key.text[key.text.find("(") + 1 : key.text.find(")")])
                    .lower()
                    .replace(" ", "")
                    for key in recommended_rubber_div.select("span")
                ]
                value_list = [
                    {
                        "link": value.get("href", ""),
                        "name": format_string(value.text).strip(),
                    }
                    for value in recommended_rubber_div.select("a")
                ]

                recommended_rubber_list = dict(zip(key_list, value_list))

                user_review_details.append(
                    {
                        "experience": experience,
                        "comment": comment,
                        "comment_long": long_comment,
                        "stats": stats,
                        "recommended_rubbers": recommended_rubber_list,
                    }
                )

            details = {
                "images": images_list,
                "description": description,
                "variants": variants,
                "everyones_rating": everyones_rating_string,
                "specification": specification,
                "players_list": players_list,
                "user_reviews": user_review_details,
                **evaluation_review_details,
            }

        return details

    def fetch_blades(self) -> list:
        page_index = 0
        res_blades_list = []

        def process_blade(blade_div):
            name = blade_div.find("em").text
            blade_detail_url = blade_div["href"]

            # Stats
            stats = {}
            point_box_ul = blade_div.find("ul", {"class": "pointBox"})
            if point_box_ul:
                for item in point_box_ul.find_all("li"):
                    key_value = item.text.split("：")
                    if len(key_value) == 2:
                        key, value = key_value
                        stats[key.lower()] = value

            return {
                "name": name,
                "url": blade_detail_url,
                **stats,
                **self.fetch_blade_details(blade_detail_url),
            }

        with tqdm(desc="Fetching Blades", unit="page") as pbar:
            while True:
                url = f"{self.base_url}racket/search/all_average/{page_index}"
                response = self.session.get(url)
                if response.status_code != 200 or "404.html" in response.url:
                    break

                soup = BeautifulSoup(response.content, "html.parser")
                blades_listing = soup.find("ul", {"class": "listCont"})
                if not blades_listing:
                    break

                with ThreadPoolExecutor() as executor:
                    futures = [executor.submit(process_blade, blade_div) for blade_div in blades_listing.find_all("a")]
                    for future in futures:
                        res_blades_list.append(future.result())

                page_index += 1
                pbar.update(1)

        return res_blades_list