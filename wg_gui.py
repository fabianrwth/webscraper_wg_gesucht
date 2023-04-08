import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import os
import logging
from unidecode import unidecode
import tkinter as tk
from tkinter import ttk


class WGScraperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("WG-Gesucht Scraper")
        self.create_widgets()

    def create_widgets(self):
        self.city_label = ttk.Label(root, text="City:")
        self.city_label.grid(row=0, column=0, padx=5, pady=5)
        self.city_entry = ttk.Entry(root)
        self.city_entry.grid(row=0, column=1, padx=5, pady=5)

        self.max_rent_label = ttk.Label(root, text="Maximum Rent:")
        self.max_rent_label.grid(row=1, column=0, padx=5, pady=5)
        self.max_rent_entry = ttk.Entry(root)
        self.max_rent_entry.grid(row=1, column=1, padx=5, pady=5)

        self.min_size_label = ttk.Label(root, text="Minimum Size:")
        self.min_size_label.grid(row=2, column=0, padx=5, pady=5)
        self.min_size_entry = ttk.Entry(root)
        self.min_size_entry.grid(row=2, column=1, padx=5, pady=5)

        self.results_table = ttk.Treeview(root, height=20, columns=("Title", "Price", "Size", "WG Type", "City", "District"))
        self.results_table.heading("Title", text="Title")
        self.results_table.heading("Price", text="Price")
        self.results_table.heading("Size", text="Size")
        self.results_table.heading("WG Type", text="WG Type")
        self.results_table.heading("City", text="City")
        self.results_table.heading("District", text="District")

        self.results_table.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

        self.status_label = ttk.Label(root, text="")
        self.status_label.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

        # Add a button to calculate BMI
        # calculate_button = tk.Button(input_frame, text="Calculate BMI", command=self.calculate_bmi)
        search_button = ttk.Button(root, text="Search", command=self.start_scraping)
        search_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

    def start_scraping(self):
        # get user inputs
        city = self.city_entry.get()
        max_rent = int(self.max_rent_entry.get())
        min_size = int(self.min_size_entry.get())

        # specify the URL of the search results page for the city on wg-gesucht.de
        url = f"https://www.wg-gesucht.de/wg-zimmer-in-{unidecode(city.lower())}.73.0.1.0.html?offer_filter=1&city_id=73&sort_order=0&noDeact=1&categories%5B%5D=0&rent_types%5B%5D=0&sMin={min_size}&rMax={max_rent}"
        print(url)
        # send a GET request to the URL and get the HTML content of the page
        response = requests.get(url)
        html_content = response.content
        # print(html_content)

        # parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(html_content, "html.parser")

        # find all listings on the page
        listings = soup.find_all(class_="wgg_card offer_list_item")
        # print(listings)
        # define a regular expression pattern to match the relevant information in the string
        pattern = r"(\d+)er WG[\s|]*(\S+)[\s|]*(\S+)[\s|]*(\S+.*)"

        # create an empty list to store the data
        data = []

        # set up logging
        logging.basicConfig(filename="merged_info.log", level=logging.INFO, format="%(asctime)s:%(message)s")

        # loop through each listing and extract the information
        for listing in listings:
            title = listing.find(class_="truncate_title noprint").text.strip()
            price = listing.find(class_="col-xs-3").text.strip()
            size = listing.find(class_="col-xs-3 text-right").text.strip()

            # parse single informations with regex
            merged_infos = listing.find(class_="col-xs-11").text.replace("\n", "")

            # log the value of merged_infos
            logging.info(merged_infos)

            match = re.search(pattern, merged_infos, re.MULTILINE)
            if match is not None:
                # extract the relevant information from the match object
                wg_type = match.group(1)
                city = match.group(2).strip()
                district = match.group(3).strip()
                street = match.group(4).strip()

                # append the extracted data to the list
                data.append([title, price, size, wg_type, city, district, street])

            else:
                print("No match found")

        # create a pandas DataFrame from the extracted data
        df = pd.DataFrame(data, columns=["Title", "Price", "Size", "WG Type", "City", "District", "Street"])

        # save the DataFrame to a CSV file in the current working directory
        file_path = os.path.join(os.getcwd(), "wg_listings.csv")
        df.to_csv(file_path, index=False)

        # print a message to confirm that the file has been saved
        print(f"DataFrame saved to {file_path}")

        # clear the table
        self.results_table.delete(*self.results_table.get_children())

        # loop through the rows of the DataFrame and insert each row into the table
        for row in df.itertuples(index=False):
            self.results_table.insert("", "end", values=row)


root = tk.Tk()
root.geometry("12000x600")
wg_webscraper = WGScraperGUI(root)
root.mainloop()
