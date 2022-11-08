import math

from bs4 import BeautifulSoup
import requests
import csv


class AssociatedProduct:
    sku: str = ""
    name: str = ""
    img: str = ""
    description: str = ""

    # init method or constructor
    def __init__(self, sku: str, name: str, img: str, description: str):
        self.sku = sku
        self.name = name
        self.img = img
        self.description = description

    def as_configurable_variation(self):
        return f"sku={self.sku},color={self.name}"


base_url = "https://www.simplywigs.co.uk/ladies-wigs/wig-brands/gisela-mayer-wigs/"

brands = {
    "1283": "Classic Collection",
    "1839": "Human Hair Wigs",
    "2439": "High Tech",
    "3488": "New Modern Hair",
    "3670": "Visconti",
    "4671": "New Generation",
    "4672": "Cosmopolitan",
    "4674": "End Comfort",
    "4675": "Duo Fibre",
    "4677": "Modern Hair",
    "4678": "Diamond Collection",
    "4679": "Sun Hair Collection",
    "4704": "Hair to Go",
    "4816": "Prime",
    "4905": "Fashion Classics",
    "5460": "Supreme"
}

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/39.0.2171.95 Safari/537.36'}

csv_header = ["sku", "store_view_code", "attribute_set_code", "product_type", "categories", "name", "description",
              "short_description", "visibility", "price", "base_image", "small_image", "thumbnail_image",
              "swatch_image", "additional_attributes", "qty", "is_in_stock", "websites_id", "additional_images",
              "configurable_variations", "associated_skus", "color", "product_websites", "status", "state"]


def scrap():
    # file = open('data-simply-supreme.csv', 'w')
    # writer = csv.writer(file)
    # writer.writerow(csv_header)

    for k, v in brands.items():

        file = open(f'data-{k}.csv', 'w')
        writer = csv.writer(file)
        writer.writerow(csv_header)

        product_urls = get_all_products_by_brand_code(k)
        for product_url in product_urls:
            print(f"Scrap page {product_url}")
            images = []

            response = requests.get(product_url, headers=headers)
            product_soup = BeautifulSoup(response.content, 'html.parser')
            product_images = product_soup.find("div", {"class": "product-img-box"}) \
                .find_all("img", {"class": "fancybox"})

            for product_image in product_images:
                images.append(product_image["data-src"])

            try:
                sku = product_soup.find("span", {"itemprop": "sku"})['content']
            except:
                sku = None

            try:
                price = product_soup.find("span", {"class": "price-including-tax"}) \
                    .text.replace('£', "") \
                    .replace('inc. VAT', "").strip()
                price = round(float(price)*5.71, 2)
            except:
                price = None

            try:
                name = product_soup.find("h1", {"class": "h1"}).text.replace('\n', "").strip()
            except:
                name = None

            try:
                short_description = product_soup.find("dt", {"id": "overview"}) \
                    .find_next("dd", {"class": "tab-container"})
                short_description.find("strong", {"data-renderer-mark": "true"}).parent.decompose()
                short_description.find("h3").decompose()
                short_description = short_description.text.strip()
            except:
                short_description = None

            try:
                description = product_soup.find("dt", {"id": "details"}).find_next("dd", {"class": "tab-container"})
                description.find("div", {"class", "measurement-image"}).decompose()
                description.find("script").decompose()
            except:
                description = None

            associated_skus = product_soup.find("div", {"class": "ruk_rating_snippet"})['data-sku']
            associated_skus = associated_skus.split(";")
            del associated_skus[0]

            configurable_variations = []
            for associated_product in get_associated_products(product_soup, associated_skus):
                product_row = [
                    associated_product.sku,
                    "peruci_profesionale",
                    "Default",
                    "simple",
                    f"Shop/Peruci Femei/Gisela Mayer/{brands[k]}",
                    associated_product.name,
                    associated_product.description,
                    "",
                    "Not Visible Individually",
                    price,
                    associated_product.img,
                    associated_product.img,
                    associated_product.img,
                    associated_product.img,
                    "",
                    100,
                    1,
                    1,
                    associated_product.img,
                    "",
                    "",
                    associated_product.name,
                    "peruci_profesionale",
                    1,
                    1
                ]
                writer.writerow(product_row)
                configurable_variations.append(associated_product.as_configurable_variation())

            product_row = [
                sku,
                "",
                "Default",
                "configurable",
                f"Shop/Peruci Femei/Gisela Mayer/{brands[k]}",
                name,
                description,
                short_description,
                "Catalog, Search",
                price,
                images[0],
                images[0],
                images[0],
                images[0],
                "",
                100,
                1,
                1,
                ",".join(images),
                "|".join(configurable_variations),
                ",".join(associated_skus),
                "",
                "peruci_profesionale",
                1,
                1
            ]
            writer.writerow(product_row)


def get_associated_products(product_soup: BeautifulSoup, associated_skus: []) -> []:
    products = []
    for associated_sku in associated_skus:
        simple_product = product_soup.find("div", {"class": "colours-modal", "id": associated_sku})
        if simple_product:
            simple_product_img = simple_product.find("img")["data-src"]
            simple_product_name = simple_product.find("h3").text
            simple_product_description = simple_product.find("div", {"class": "modal-shop"}).find("p").text
            products.append(
                AssociatedProduct(
                    associated_sku,
                    simple_product_name,
                    simple_product_img,
                    simple_product_description
                )
            )

    return products


def is_last_page(content) -> bool:
    soup = BeautifulSoup(content, 'html.parser')
    if not soup.select("a.next.i-next"):
        return True
    else:
        return False


def get_all_products_by_brand_code(brand_code: str) -> []:
    print(brands[brand_code])
    product_list = []
    current_page = 1
    url = get_url_by_brand_code(brand_code)
    while True:
        response = requests.get(f"{url}&p={current_page}", headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        for a in soup.select("li.item a.product-image"):
            product_list.append(a.get('href'))

        if is_last_page(response.content):
            break

        current_page += 1

    return product_list


def get_url_by_brand_code(brand_code: str) -> str:
    return f"{base_url}?detail_wig_brands={brand_code}&limit=100"


if __name__ == '__main__':
    scrap()
