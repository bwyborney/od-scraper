"""
OD-scraper by Ben Wyborney
Hey, thanks for using this thing I made! I apologize in advance for the low quality of my code, and I need
to make it clear that I am NOT a programmer and I have NO idea what I'm doing - I just bodged this thing
together to make my life at work a little bit easier. Feel free to use this however you'd like, and
definitely feel free to fork this project if you're a more skilled coder than me. If you do choose to fork
this and improve it, I'll probably end up using your version, honestly. You can send me feedback at
bwyborney@protonmail.com as well. Thanks again for checking out my project!
"""
# Used for saving and manipulating files
import os.path
import os
from os import path
from shutil import copy
# Used to generate a PDF file from an HTML file
import weasyprint
# Used to send HTTP requests
import requests
# Used to parse the webpages for specific tags
from bs4 import BeautifulSoup
from bs4 import SoupStrainer
# Used to create barcodes from any number. I'm using Code128 because it is widely used and can support my need for just 6-8 numbers and nothing else
from barcode import Code128
from barcode.writer import ImageWriter
# Gets the date and time, which is important because I've seen availability change by the day or even the hour
from datetime import datetime


### Scraper - sends HTTP requests to the pages for each SKU, then checks for availability
def scraper(txtSKUS, category) :
    # Open a file from the skuLists directory
    skuListFileName = ("skuLists/" + txtSKUS)
    skus = open(skuListFileName)

    # These are all the possible terms I've found on the website so far, and we'll check for each one until we've found a match
    searchTerms = ["Free delivery", "Free next business day delivery", "Out of stock for delivery", "Available for future delivery", "This item is no longer available", "other"]
    # Count the number of lines in the file, to be used as the denominator to calculate completion percent
    numerator = 0.0
    denominator = 0.0
    for counter in skus :
        denominator +=1
    skus.close()
    strDenominator = denominator
    denomInt = int(denominator)
    print("Checking " + str(denomInt) + " skus in " + category)
    skus = open(skuListFileName)
    for l in skus :
        # Call the barcoder function and pass it l, which is the SKU number
        barcoder(l)
        statusFound = False
        # Type this URL and add any SKU number to the end and you'll get redirected to the correct product page
        url = ("https://officedepot.com/a/products/" + l)
        # Make HTTP request
        webpage1 = requests.get(url)
        # Only parse div tags
        onlyStatus = SoupStrainer("div")
        soup1 = BeautifulSoup(webpage1.text, "lxml", parse_only=onlyStatus)
        # Every page I've seen so far labels these divs with the id "skuAvailability"
        soup2 = soup1.find(id="skuAvailability")
        # It's late and I'm tired, so this variable is called stringyThingy. Before, it was a thingy, but now, now it is also stringy
        stringyThingy = str(soup2)
        # Reset the index
        stIndex = 0
        # Print the SKU that's currently being checked
        stripThis = l
        strippedSkuOnly = stripThis.strip()
        # Print the current SKU and completion percent
        percent = numerator / denominator * 100.0
        percentRnd = round(percent, 2)
        percentStr = str(percentRnd)
        print("Completion: " + percentStr + "%... checking sku " + strippedSkuOnly, end="\r")

        # Check the contents of the skuAvailability tag for each possible value, and once the correct one is found, send it to the resulter function
        while statusFound == False and stIndex < 5 :
            checkFor = searchTerms[stIndex]
            if checkFor in stringyThingy :
                status = searchTerms[stIndex]
                # Call the titleGrabber function to get the title of the product from the webpage
                itemTitle = titleGrabber(url)
                # Call the resulter function and pass it the SKU status that we found, the name of the product which we got from titleGrabber, and the SKU number
                resulter(status, itemTitle, l)
                statusFound = True
            else :
                stIndex += 1
        numerator += 1

        # Fallback in case none of the search terms are found. This will label the SKU status as "other"
        # I've only needed this so far for pages with "this product is no longer available," which don't have any elements using the skuAvailability id
        if stIndex == 5 :
            status = searchTerms[stIndex]
            itemTitle = titleGrabber(url)
            resulter(status, itemTitle, l)

    skus.close()
    # Call the "finisher" function, which puts everything together into a nice PDF
    denominator = 0
    finisher(category)

### Results sorter - checks the contents of the skuAvailability tag from the scraper function, and puts it in a list that corresponds to its availablitiy
def resulter(writeValue, writeTitle, itemSKU) :
    if writeValue == "Free delivery" :
        # Add the title of the product to a list of other product titles that are listed as availabel for free delivery
        freeDel.append(writeTitle)
        # Add the SKU number to a separate but parallel list
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

### Barcode generator
def barcoder(badSku) :
    # Convert the SKU number into a string and strip the blankspace
    goodSku = str(badSku)
    itemNumber = goodSku.strip()
    # Create a filename for the barcode image, which will be the SKU number with a .png extension
    filename = "results/barcodes/" + itemNumber
    barcode = Code128(itemNumber, writer=ImageWriter())
    barcode.save(filename)


### Finalize - write all the product titles to a file under a heading that shows their availability
def finisher(catName) :
    # Reset all the indexes to 0, only makes a difference if you're using multiple skuLists files since this function will need to be run multiple times
    sr1 = 0
    sr2 = 0
    sr3 = 0
    sr4 = 0
    sr5 = 0
    sr6 = 0
    # Strings with HTML inside. There will be a line of HTML for every item, and these particular strings will be reused for each one
    # Start new div and create a hyperlink to the product page
    aTag1 = "<div class=\"product\"><a href=\"https://officedepot.com/a/products/"
    aTag2 = "\">"
    aTag3 = "</a>"
    # The product title will go in here
    pTag1 = "<p class=\"sku "
    pTag2 = "\">"
    pTag3="</p>"
    brTag = "<br>"
    # This is where the barcode file will go
    imgTag1 = "<img class=\"barcode\" src=\"./barcodes/"
    imgTag2 = ".png\"></div>"
    # Get the date and time, and add the <h1> tag to the HTML file
    todaysDate = datetime.now()
    dateString = todaysDate.strftime("%m/%d @ %H:%M")
    fileDate = todaysDate.strftime("_%m-%d_%H%M")
    # Copy the results.html file, which is essentially a template, and name the copy after the skuList file
    resultsWebPageName = ("results/results_" + catName + ".html")
    copy("resources/results.html", resultsWebPageName)
    resultWebPage = open(resultsWebPageName, 'a+')
    webPageTitle = ("<h1>" + catName + " - " + dateString + "</h1>")
    resultWebPage.write(webPageTitle)
    # Write in a new div for available SKUs
    resultWebPage.write("</div>")
    resultWebPage.write("<div id=\"contents\">")
    resultWebPage.write("<div class=\"sectionHeader\">Available</div>")
    resultWebPage.write("<div class=\"SKUS\">")
    # Write in every "available" product, along with its corresponsing hyperlink and barcode. Each product gets its own div too
    # Products marked with "Free delivery" or "Free next business day delivery" are listed as available
    for r1 in freeDel :
        sSr1 = str(sfreeDel[sr1])
        strippedSkuFD = sSr1.strip()
        resultWebPage.write(aTag1 + strippedSkuFD + aTag2 + pTag1 + catName + " " + "available" + pTag2 + strippedSkuFD + brTag + r1 + pTag3 + aTag3  + imgTag1 + str(strippedSkuFD) + imgTag2 + '\n')
        sr1 += 1
    for r2 in freeNex :
        sSr2 = str(sfreeNex[sr2])
        strippedSkuFN = sSr2.strip()
        resultWebPage.write(aTag1 + strippedSkuFN + aTag2 + pTag1 + catName + " " + "available" + pTag2 + strippedSkuFN + brTag + r2 + pTag3 + aTag3 + imgTag1 + str(strippedSkuFN) + imgTag2 + '\n')
        sr2 += 1
    # Start the backordered section
    resultWebPage.write("</div>")
    resultWebPage.write("<div class=\"sectionHeader\">Backordered</div>")
    resultWebPage.write("<div class=\"SKUS\">")

    # Products marked with "Available for future delivery" are listed as backordered
    for r3 in futDel :
        sSr3 = str(sfutDel[sr3])
        strippedSkuFU = sSr3.strip()
        resultWebPage.write(aTag1 + strippedSkuFU + aTag2 + pTag1 + catName + " " + "backordered" + pTag2 + strippedSkuFU + brTag + r3 + pTag3 + aTag3  + imgTag1 + str(strippedSkuFU) + imgTag2 + '\n')
        sr3 += 1
    # Start the unavailable section
    resultWebPage.write("</div>")
    resultWebPage.write("<div class=\"sectionHeader\">Unavailable</div>")
    resultWebPage.write("<div class=\"SKUS\">")

    # Products marked with "Out of stock for delivery," "This item is no longer available," or "other" are listed as unavailable
    for r4 in outStk :
        sSr4 = str(soutStk[sr4])
        strippedSkuOS = sSr4.strip()
        resultWebPage.write(aTag1 + strippedSkuOS + aTag2 + pTag1 + catName + " " + "unavailable" + pTag2 + strippedSkuOS + brTag + r4 + pTag3 + aTag3 + imgTag1 + str(strippedSkuOS) + imgTag2 + '\n')
        sr4 += 1
    for r5 in cantHave :
        sSr5 = str(scantHave[sr5])
        strippedSkuCH = sSr5.strip()
        resultWebPage.write(aTag1 + strippedSkuCH + aTag2 + pTag1 + catName + " " + "unavailable" + pTag2 + strippedSkuCH + brTag + r5 + pTag3 + aTag3 + imgTag1 + str(strippedSkuCH) + imgTag2 + '\n')
        sr5 += 1
    for r6 in other :
        sSr6 = str(sother[sr6])
        strippedSkuOT = sSr6.strip()
        resultWebPage.write(aTag1 + strippedSkuOT + aTag2 + pTag1 + catName + " " + "unavailable" + pTag2 + strippedSkuOT + brTag + r6 + pTag3 + aTag3 + imgTag1 + str(strippedSkuOT) + imgTag2 + '\n')
        sr6 += 1
    # Write the closing lines of HTML
    resultWebPage.write("</div>")
    resultWebPage.write("</div>")
    resultWebPage.write("</body>")
    resultWebPage.write("</html>")

    # Empty the lists because they need to be empty for the next skuList
    freeDel.clear()
    freeNex.clear()
    outStk.clear()
    futDel.clear()
    cantHave.clear()
    other.clear()

    sfreeDel.clear()
    sfreeNex.clear()
    soutStk.clear()
    sfutDel.clear()
    scantHave.clear()
    sother.clear()

    resultWebPage.close()
    # Convert the HTML file into a PDF. Useful because PDFs can be easily shared and viewed on any device, and don't require external images files like a webpage
    # Name the PDF file
    resultPdfPageName = ("results/" + catName + fileDate + ".pdf")
    # Use weasyprint to convert the HTML file into a PDF
    resultPdfPage = weasyprint.HTML(resultsWebPageName).write_pdf()
    open(resultPdfPageName, 'wb').write(resultPdfPage)

    # Now that we have a PDF with everything we need, we are essentially done with this skuList, or possibly the whole program, so we can clean up the unecessary files we created
    # Delete the HTML file
    os.remove(resultsWebPageName)
    # Delete all the barcode images
    for barcodeFile in os.listdir("results/barcodes") :
        removeThis = "results/barcodes/" + barcodeFile
        os.remove(removeThis)

### Title grabber - gets the name of the product from the webpage
def titleGrabber(URL) :
    # Make HTTP request
    webpage = requests.get(URL)
    # Parse the webpage with beautiful soup
    asoup = BeautifulSoup(webpage.text, "lxml")
    # Narrow it down to just the element that contains the product title
    bsoup = asoup.find(class_="semi_bold fn", itemprop="name")

    # Fallback in case the webpage doesn't has an element with itemprop = "name". So far, in all these cases, the product title has instead been in an element with class="fn clear"
    if str(bsoup) == "None" :
        csoup = asoup.find(class_="fn clear")
    else :
        csoup = bsoup

    # Not sure why I chose this name
    thingy = 0
    # The value from the bs parser usually contains extra information, including a lot of blankspace and an unwanted <p> tag, so this will remove that
    for stringy in csoup.stripped_strings :
        if thingy == 0 :
            bstitle = stringy
        thingy += 1
    # Now we've got the name of the product
    return bstitle


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

# Pull all the text files placed in the the skuLists directory
skulists = os.listdir("skuLists")

# The beginning of the program
print("---OD-Scraper by Ben Wyborney--")
for sl in skulists :
    # Determine what the name of this list, or "category" will be by taking the name of the file and removing the ".txt"
    slr  = sl.replace(".txt", "")
    # Pass the filename with and without the .txt extension to the scraper function
    scraper(sl, slr)
