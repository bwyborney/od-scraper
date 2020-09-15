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
    searchTerms = ["Free delivery", "Free next business day delivery", "Out of stock for delivery", "Available for future delivery", "This item is no longer available", "other"]

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
        while statusFound == False and stIndex < 5 :
            checkFor = searchTerms[stIndex]
            if checkFor in stringyThingy :
                status = searchTerms[stIndex]
                # Get the title of the product from the webpage
                itemTitle = titleGrabber(url)
                resulter(status, itemTitle, l)
                statusFound = True
            else :
                stIndex += 1

        # Failback in case none of the search terms are found
        if stIndex == 5 :
            status = searchTerms[stIndex]
            itemTitle = titleGrabber(url)
            resulter(status, itemTitle, l)

    skus.close()
    finisher()

### Results sorter - pretty simple, just adds the product name to the correct list
def resulter(writeValue, writeTitle, itemSKU) :
    if writeValue == "Free delivery" :
        freeDel.append(writeTitle)
        sfreeDel.append(itemSKU)
    elif writeValue == "Free next business day delivery" :
        freeNex.append(writeTitle)
        sfreeNex.append(itemSKU)
    elif writeValue == "Out of stock for delivery" :
        outStk.append(writeTitle)
        soutStk.append(itemSKU)
    elif writeValue == "Available for future delivery" :
        futDel.append(writeTitle)
        sfutDel.append(itemSKU)
    elif writeValue == "This item is no longer available" :
        cantHave.append(writeTitle)
        scantHave.append(itemSKU)
    elif writeValue == "other" :
        other.append(writeTitle)
        sother.append(itemSKU)


### Finalize - write all the product titles to a file under a heading that shows their availability
def finisher() :
    sr1 = 0
    sr2 = 0
    sr3 = 0
    sr4 = 0
    sr5 = 0
    sr6 = 0

    # Append the results to a file called results. If there isn't such a file already, creates one
    resultPage = open("results", "a")

    # Products marked with "Free delivery" or "Free next business day delivery" are listed as available
    resultPage.write("---AVAILABLE---" + '\n')
    for r1 in freeDel :
        resultPage.write(sfreeDel[sr1])
        resultPage.write(r1 + '\n' + '\n')
        sr1 += 1
    for r2 in freeNex :
        resultPage.write(sfreeNex[sr2])
        resultPage.write(r2 + '\n' + '\n')
        sr2 += 1

    # Products marked with "Available for future delivery" are listed as backordered
    resultPage.write("----------" + '\n' + '\n' + '\n' + "---Backordered---" + '\n')
    for r3 in futDel :
        resultPage.write(sfutDel[sr3])
        resultPage.write(r3 + '\n' + '\n')
        sr3 += 1

    # Products marked with "Out of stock for delivery" or "This item is no longer available" are listed as unavailable
    resultPage.write("----------" + '\n'+ '\n' + '\n'  + "---Unavailable---" + '\n')
    for r4 in outStk :
        resultPage.write(soutStk[sr4])
        resultPage.write(r4 + '\n' + '\n')
        sr4 += 1
    for r5 in cantHave :
        resultPage.write(scantHave[sr5])
        resultPage.write(r5 + '\n' + '\n')
        sr5 += 1
    for r6 in other :
        resultPage.write(sother[sr6])
        resultPage.write(r6 + '\n' + '\n')
        sr6 += 1


    resultPage.close()


### Title grabber - gets the name of the product from the webpage
def titleGrabber(URL) :
    # Make HTTP request
    webpage = requests.get(URL)
    asoup = BeautifulSoup(webpage.text, "lxml")
    bsoup = asoup.find(class_="semi_bold fn", itemprop="name")

    # Sometimes, if a SKU is permanently unavailable, its page will use slightly different code,
    # so the search for itemprop name will be unsuccessful. If that happens, this if/else will
    # search for these other tags instead, because we still want the title.
    if str(bsoup) == "None" :
        csoup = asoup.find(class_="fn clear")
    else :
        csoup = bsoup

    # Not sure why I chose this name
    thingy = 0
    # This is a clunky and lazy way to deal with the fact that the parser above return extra information, including tons of blankspace and the contents of the p tag inside the h1 tag
    # Strip the blankspace, and only pull the first line, which is the title of the product
    for stringy in csoup.stripped_strings :
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
other = []

sfreeDel = []
sfreeNex = []
soutStk = []
sfutDel = []
scantHave = []
sother = []

print("---OD-Scraper by Ben Wyborney--")
print("Would you like insructions? Type yes or no, then hit the enter key.")
instructAsk = input("~:>")
while instructAsk != "yes" and instructAsk != "no" :
    print("Hmmm I'm looking for yes or no. ")
    instructAsk = input("~:>")

if instructAsk == "yes" :
    print("Alright, it's pretty simple. The program will look for a text file called skus.txt.")
    print("You should see that you already have this file, and when you open it, that it's empty.")
    print("All you need to do is fill that file with the SKUs you want to search for. There should be one SKU per line, with no spaces before.")
    print("For example:")
    print("101095")
    print("102866")
    print("119694")
    print("163691")
    print("216230")
    print('\n' + "Once you've done that, go ahead and save the file, then come back here and type ok, and hit enter.")
    readyOrNot = input("~:>")
    while readyOrNot != "ok" :
        print("Hmmm I'm looking for ok.")
        readyOrNot = input("~:>")
    scraper("skus.txt")
else :
    print("Alright, I'll go ahead and get started.")
    scraper("skus.txt")
