import os.path
from os import path
import os


# Pull all the text files placed in the the skuLists directory
skulists = os.listdir("skuLists")

# Run through the program once for every sku list
for sl in skulists :
    slr  = sl.replace(".txt", "")
    specific = ("skuLists/" + sl)
    print(specific)
