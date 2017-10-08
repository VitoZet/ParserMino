import sys
import csv
import requests
import lxml.html
from PyQt5.QtWidgets import QMainWindow, QApplication
from UI_parser_MINO import UI_parser_MINO

class OlxParser:
    def __init__(self, base_url):
        self.base_url = base_url

    def get_page(self):

        try:
            res = requests.get(self.base_url)
        except:
            return

        if res.status_code < 400:
            return res.content

    def parse_product(self, html):
        html_tree = lxml.html.fromstring(html)
        h1 = html_tree.xpath(".//h1")[0].text_content().strip()
        try:
            description = html_tree.xpath(".//div[@class ='product_description']")[0].text_content().strip()
        except:
            description = 'Описание товара в процессе заполнения'

        image_URLs = html_tree.xpath(".//div[@class ='product-images']//a")[0].get('href')
        for im in html_tree.xpath(".//div[@class ='more-images']//a"):
            image_URLs = image_URLs + ',' + im.get('href')
        reference = \
            html_tree.xpath(".//div[@class='product-template-default']//tr[@class='item']//td[@class='text-left']")[
                0].text_content().strip()

        open_file = open('product.csv', 'w', encoding='utf-8', newline='')
        header = ['Product ID', 'Active (0/1)', 'Name *', 'Categories', 'Price tax excluded or Price tax included',
                  'Tax rules ID', 'Wholesale price', 'On sale (0/1)', 'Discount amount', 'Discount percent',
                  'Discount from (yyyy-mm-dd)', 'Discount to (yyyy-mm-dd)', 'Reference', 'Supplier reference',
                  'Supplier', 'Manufacturer', 'EAN13', 'UPC', 'Ecotax', 'Width', 'Height', 'Depth', 'Weight',
                  'Quantity', 'Minimal quantity', 'Visibility', 'Additional shipping cost', 'Unity', 'Unit price',
                  'Short description', 'Description', 'Tags', 'Meta title', 'Meta keywords', 'Meta description',
                  'URL rewritten', 'Text when in stock', 'Text when backorder allowed', 'Available for order',
                  'Product available date', 'Product creation date', 'Show price', 'Image URLs',
                  'Delete existing images', 'Feature', 'Available online only', 'Condition', 'Customizable',
                  'Uploadable files', 'Text fields', 'Out of stock', 'ID  Name of shop', 'Advanced stock management',
                  'Depends On Stock', 'Warehouse']
        wrtr = csv.DictWriter(open_file, delimiter=';', fieldnames=header)
        wrtr.writeheader()
        wrtr.writerow({'Active (0/1)': '1', 'Name *': h1, 'Reference': reference, 'Description': description,
                       'Image URLs': image_URLs})

    # Атрибуты!
    def parse_product_attribute(self, html):
        html_tree = lxml.html.fromstring(html)
        head_attribute_str = ''
        head_parsing = html_tree.xpath(".//thead//th")[1:-3]
        for en, hd_at in enumerate(head_parsing):
            head_attribute_str = head_attribute_str + hd_at.text_content().strip() + ':select:' + str(en) + ','
        open_file = open('product_attribute.csv', 'w', encoding='utf-8', newline='')
        header = ['Product ID', 'Reference', 'Attribute', 'Value', 'Supplier reference', 'EAN13', 'UPC',
                  'Wholesale price', 'Impact on price', 'Ecotax', 'Quantity', 'Minimal quantity', 'Impact on weight',
                  'Default', 'Combination available date', 'Image position', 'Image URL', 'Delete existing images',
                  'ID Name of shop', 'Advanced Stock Managment', 'Depends on stock', 'Warehouse']

        wrtr = csv.DictWriter(open_file, delimiter=';', fieldnames=header)
        wrtr.writeheader()

        product_models = html_tree.xpath(".//div[@class='product-template-default']//tr[@class='item']")
        for m in product_models:
            model_attribute = ''
            for en, option in enumerate(m[1:-3]):
                model_attribute = model_attribute + option.text_content().strip() + ':' + str(en) + ','
            wrtr.writerow({'Attribute': head_attribute_str[:-1], 'Value': model_attribute[:-1],
                           'Reference': m[0].text_content().strip()})

class GuiParser(QMainWindow, UI_parser_MINO):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.initSignal()

    def initSignal(self):
        self.startButton.clicked.connect(self.work)

    def work(self):
        parser = OlxParser(self.paste_url.text())
        page = parser.get_page()
        parser.parse_product(page)
        parser.parse_product_attribute(page)
        self.paste_url.setText('ГОТОВО! ДАЛЬШЕ ИМПОРТ!!!')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    parser = GuiParser()
    parser.show()
    sys.exit(app.exec_())