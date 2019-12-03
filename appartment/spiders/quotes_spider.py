import scrapy
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pkgutil, json

class QuotesSpider(scrapy.Spider):
    name = "quotes"
    headers = {
        'Host': 'www.leboncoin.fr',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
    }
    is_valid = True

    def start_requests(self):
        url = 'https://www.leboncoin.fr/ventes_immobilieres/offres/ile_de_france/'
        cnt = 0
        while self.is_valid:
            yield scrapy.Request(url=url, callback=self.parse, headers=self.headers)
            cnt = cnt + 1
            url = 'https://www.leboncoin.fr/ventes_immobilieres/offres/ile_de_france/p-%s/' % cnt


    def insert(self, data):
        jsdt = pkgutil.get_data("appartment", "spiders/client_secret.json")
        jsdt = json.loads(jsdt.decode("UTF-8"))

        # use creds to create a client to interact with the Google Drive API
        scope = ['https://www.googleapis.com/auth/spreadsheets']
        creds = ServiceAccountCredentials.from_json_keyfile_dict(jsdt, scope)
        client = gspread.authorize(creds)

        # Find a workbook by name and open the first sheet
        # Make sure you use the right name here.
        sheet = client.open_by_key("1AMR2-ChgnCpOJMTT1S9lidCIReodJlG9QExIV_mcefw").sheet1

        # sheet.resize(1)
        sheet.append_row(data)

    def getValue(self, soup, query, num):
        try:
            return soup.select(query)[num].text.strip()
        except:
            return ''

    def parse_unit(self, response):
        """
        Web Content Parsing Unit
        :param response: response
        :return: None
        """
        soup = BeautifulSoup(response.body, "html.parser")
        data = [response.url]

        title = self.getValue(soup, 'h1._3MDJa.dgtty', 0)
        price = self.getValue(soup, 'span._1F5u3', 0)
        date_pub = self.getValue(soup, 'div._14taM', 0).replace(title, '').replace(price, '')
        i = 0
        category = self.getValue(soup, 'div._3-hZF', i)
        type = "type is undefined"
        pieces = "Pièces is undefined"
        surfaces = "Surface is undefined"
        reference = "Référence is undefined"
        while category != "":
            itemValue = self.getValue(soup, 'div._3Jxf3', i)
            if category == 'Type de bien':
                type = itemValue
            elif category == "Pièces":
                pieces = itemValue
            elif category == "Surface":
                surfaces = itemValue
            elif category == "Référence":
                reference = itemValue
            i = i + 1
            category = self.getValue(soup, 'div._3-hZF', i)

        ges = self.getValue(soup, 'div._1sd0z', 0)
        class_energies = self.getValue(soup, 'div._1sd0z', 1)
        description = self.getValue(soup, 'span.content-CxPmi', 0)
        location = self.getValue(soup, 'div._1aCZv', 0)

        data.append(title)
        data.append(price)
        data.append(date_pub)
        data.append(type)
        data.append(pieces)
        data.append(surfaces)
        data.append(reference)
        data.append(ges)
        data.append(class_energies)
        data.append(description)
        data.append(location)
        self.insert(data)


    def parse(self, response):
        soup = BeautifulSoup(response.body, "html.parser")
        atags = soup.find_all('a', {'class' : 'clearfix trackable'})

        html_urls = []

        jsdt = pkgutil.get_data("appartment", "spiders/client_secret.json")
        jsdt = json.loads(jsdt.decode("UTF-8"))

        # use creds to create a client to interact with the Google Drive API
        scope = ['https://www.googleapis.com/auth/spreadsheets']
        creds = ServiceAccountCredentials.from_json_keyfile_dict(jsdt, scope)
        client = gspread.authorize(creds)

        # Find a workbook by name and open the first sheet
        # Make sure you use the right name here.
        sheet = client.open_by_key("1AMR2-ChgnCpOJMTT1S9lidCIReodJlG9QExIV_mcefw").sheet1
        gsheet_urls = sheet.col_values(1)


        for tag in atags:
            try:
                html_urls.append('https://www.leboncoin.fr' + tag['href'])
            except:
                pass
        real_urls = []
        for url in html_urls:
            if not url in gsheet_urls:
                real_urls.append(url)


        if len(html_urls) == 0:
            self.is_valid = False
            return

        for url in real_urls:
            yield scrapy.Request(url=url, callback=self.parse_unit, headers=self.headers)