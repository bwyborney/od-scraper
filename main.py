"""
OD-scraper by Ben Wyborney
Hey, thanks for using this thing I made! I apologize in advance for the low quality of my code, and I need
to make it clear that I am NOT a programmer and I have NO idea what I'm doing - I just bodged this thing
together to make my life at work a little bit easier. Feel free to use this however you'd like, and
definitely feel free to fork this project if you're a more skilled coder than me. If you do choose to fork
this and improve it, I'll probably end up using your version, honestly. You can send me feedback at
bwyborney@protonmail.com as well. Thanks again for checking out my project, and stay safe!
"""


import os.path
from os import path
from bs4 import BeautifulSoup
from bs4 import SoupStrainer
import requests

### Scraper - sends HTTP requests to the pages for each SKU, then checks for availability
def scraper(txtSKUS) :
    skus = open(txtSKUS)

    # These are all the possible terms I've found on the website so far
    searchTerms = ["Free delivery", "Free next business day delivery", "Out of stock for delivery", "Available for future delivery", "This item is no longer available"]

    for l in skus :
        statusFound = False
        url = ("https://officedepot.com/a/products/" + l)
        # Make HTTP request and parse it using BeautifulSoup
        webpage1 = requests.get(url)
        # Only parse div tags
        onlyStatus = SoupStrainer("div")
        soup1 = BeautifulSoup(webpage1.text, "lxml", parse_only=onlyStatus)
        # Every page I've seen so far labels these divs with the id "skuAvailability"
        soup2 = soup1.find(id="skuAvailability")
        # It's late and I'm tired, so this variable is called stringyThingy. Before, it was a thingy, but now, now it is also stringy
        stringyThingy = str(soup2)

        stIndex = 0
        print("Checking sku " + l)

        # Check the contents of the skuAvailability tag for each possible value, and once the correct one is found, send it to the resulter function
        while statusFound == False :
            checkFor = searchTerms[stIndex]
            if checkFor in stringyThingy :
                status = searchTerms[stIndex]
                # Get the title of the product from the webpage
                itemTitle = titleGrabber(url)
                resulter(status, itemTitle)
                statusFound = True
            else :
                stIndex += 1

    skus.close()
    finisher()

### Results sorter - pretty simple, just adds the product name to the correct list
def resulter(writeValue, writeTitle) :
    if writeValue == "Free Delivery" :
        freeDel.append(writeTitle)
    elif writeValue == "Free next business day delivery" :
        freeNex.append(writeTitle)
    elif writeValue == "Out of stock for delivery" :
        outStk.append(writeTitle)
    elif writeValue == "Available for future delivery" :
        futDel.append(writeTitle)
    elif writeValue == "This item is no longer available" :
        cantHave.append(writeTitle)


### Finalize - write all the product titles to a file under a heading that shows their availability
def finisher() :
    # Append the results to a file called results. If there isn't such a file already, creates one
    resultPage = open("results", "a")

    # Products marked with "Free delivery" or "Free next business day delivery" are listed as available
    resultPage.write("---AVAILABLE---" + '\n')
    for r1 in freeDel :
        resultPage.write(r1 + '\n')
    for r2 in freeNex :
        resultPage.write(r2 + '\n')

    # Products marked with "Available for future delivery" are listed as backordered
    resultPage.write("----------" + '\n' + "---Backordered---" + '\n')
    for r3 in futDel :
        resultPage.write(r3 + '\n')

    # Products marked with "Out of stock for delivery" or "This item is no longer available" are listed as unavailable
    resultPage.write("----------" + '\n' + "---Unavailable---" + '\n')
    for r4 in outStk :
        resultPage.write(r4 + '\n')
    for r5 in cantHave :
        resultPage.write(r5 + '\n')


    resultPage.close()


### Title grabber - gets the name of the product from the webpage
def titleGrabber(URL) :
    # Make HTTP request
    webpage = requests.get(URL)
    # Parse only h1 tags with the two specific attributes that are used for the product title and only the product title on every page
    onlyTitle = SoupStrainer("h1")
    asoup = BeautifulSoup(webpage.text, "lxml", parse_only=onlyTitle)
    bsoup = asoup.find(class_="semi_bold fn", itemprop="name")
    # Not sure why I chose this name
    thingy = 0
    # This is a clunky and lazy way to deal with the fact that the parser above return extra information, including tons of blankspace and the contents of the p tag inside the h1 tag
    # Strip the blankspace, and only pull the first line, which is the title of the product
    for stringy in bsoup.stripped_strings :
        if thingy == 0 :
            bstitle = stringy
        thingy += 1

    return bstitle


### Initialize
# Creating these variables as lists. They won't be used until later, but they need to be set up ahead of time
freeDel = []
freeNex = []
outStk = []
futDel = []
cantHave = []

scraper("skus.txt")
