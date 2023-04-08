import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

# prompt the user to enter the desired city, maximum rent price, and minimum room size
city = input("Enter the desired city: ")
max_price = int(input("Enter the maximum rent price: "))
min_size = int(input("Enter the minimum room size: "))

# construct the URL for the search results page for the desired city and with the specified filters
url = f"https://www.wg-gesucht.de/1-zimmer-wohnungen-in-Koeln.73.1.1.0.html?offer_filter=1&city_id=73&sort_order=0&noDeact=1&categories%5B%5D=1&rent_types%5B%5D=0&sMin={min_size}&rMax={max_price}"

# send a GET request to the URL and get the HTML content of the page
response = requests.get(url)

html_content = response.content

# parse the HTML content using BeautifulSoup
soup = BeautifulSoup(html_content, 'html.parser')

# find all listings on the page
listings = soup.find_all(class_='wgg_card offer_list_item')

# define a regular expression pattern to match the relevant information in the string
pattern = r"(\der WG)[\s|]*(\S+)[\s|]*(\S+)[\s|]*(\S+.*)"

# create a list to store the details of each listing
details_list = []

# loop through each listing and extract the details
for listing in listings:
    title = listing.find(class_='truncate_title noprint').text.strip()
    price = listing.find(class_='col-xs-3').text.strip()
    size = listing.find(class_='col-xs-3 text-right').text.strip()
    merged_infos = listing.find(class_='col-xs-11').text.replace('\n', '')

    # use regex to extract the relevant information from the merged_infos string
    match = re.search(pattern, merged_infos, re.MULTILINE)
    if match is not None:
        wg_type = match.group(1)
        city = match.group(2).strip()
        district = match.group(3).strip()
        street = match.group(4).strip()
    else:
        print("No match found")

    # add the details to the list if the price is below the maximum and the size is above the minimum
    if int(price.split()[0]) <= max_price and int(size.split()[0]) >= min_size:
        details_list.append([title, price, size, wg_type, city, district, street])

# create a pandas dataframe from the details list
df = pd.DataFrame(details_list, columns=["Title", "Price", "Size", "Type", "City", "District", "Street"])

# save the dataframe to a CSV file in the current directory
df.to_csv("wg_results.csv", index=False)
