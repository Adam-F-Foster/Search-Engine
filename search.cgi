#!/usr/bin/python3
import cgitb
cgitb.enable()
print("Content-type: text/html\n")
import re
from bs4 import BeautifulSoup
import cgi
import math
import nltk.stem.porter as p


#using regex to find all links on a page
def getNetworkLinks(file):
    with open(file, "r", encoding = "utf-8") as f:
        contents = f.read()
    linkList = re.findall('(?<=href=").*?(?=")', contents)
    newList = []
    for link in linkList:
        if "javascript" not in link:
            newList.append(link)
    return newList, contents

#this method goes through the html files and finds all of the links within
#that file and determines whether they are in the index, and if so
#adds them to the local network dictionary to calculate pagerank
def crawlNetwork(): 
    file = open("bfs\\index.dat", "r", encoding = "utf-8")
    contents = [item.strip().split() for item in file.readlines()]
    links = []
    for i in range(len(contents) - 1):
        links.append(contents[i][1])
    file.close()
    network = {}
    for i in range(50):
        lst, contents = getNetworkLinks("bfs\\" + str(i) + ".html")
        for link in lst:
            for compare in links:
                #because internal links don't need the news.google, we have to add it
                if "news.google" not in link:
                    link = "https://news.google.com/" + link
                if link in links:
                    if compare in network and link not in network[compare]:
                        network[compare].append(link)
                    else:
                        network[compare] = [link]
    return network, links
    
def nodeProb(probs, inv_index, numNode, p, calls):
    print("CALLS:", calls)
    print("SUM:", sum(probs.values()))
    copy = probs.copy()
    p1 = p/numNode
    for i in copy:
        total = 0
        for j in inv_index:
            if i in inv_index[j]:
                total += probs[j] / len(inv_index[j])
        copy[i] = p1 + (1-p) * total
    #if the difference between calls is marginal or 100 calls have happened
    if copy == probs or calls == 100:
        return copy, calls
    else:
        return nodeProb(copy, inv_index, numNode, p, calls + 1)
def visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
        return False
    elif re.match('<!--.*-->', str(element)):
        return False
    return True

def fileToLowerDict(fileIn):
    with open(fileIn, "r", encoding = "utf-8") as f:
        string = f.read()
    soup = BeautifulSoup(string, "html.parser")
    contents =  soup.find_all(text = True)     
    contents = filter(visible, contents)
    string = ""
    for content in contents:
        string += content + " "
    lst = string.split()
    #please download stopwords if necessary
    with open("stopwords.txt", "r") as f:
        stopWords = f.readlines()
    for i in range(len(stopWords)):
        stopWords[i] = stopWords[i].strip()

    stems = [stemmer.stem(word) for word in lst if word not in stopWords]
    return {str(fileIn) : lst}

def inv_indexer(mapping_dict, value_dict, inv_index):
    size = len(mapping_dict.keys())
    terms = []
    if list(value_dict.keys())[0] not in mapping_dict.values():
        mapping_dict[size] = list(value_dict.keys())[0]
        terms = list(value_dict.values())[0]
    for term in terms:
        if term not in inv_index.keys():
            inv_index[term] = {}
            inv_index[term][size] = 1 / len(terms) * math.log(len(terms)/(1 + 1))#computing tf-idf
        else:
            try:
                inv_index[term][size] += 1 / len(terms) * math.log(len(terms)/(1+1))#computing tf-idf
            except: 
                pass
#calculating pagerank
#network, links = crawlNetwork()
#probs = {}
#for link in links:
#    probs[link] = 1 / len(links)
#prob, calls = nodeProb(probs, network, len(links), 0.05, 0)
#with open("pagerank.txt", "w") as file:
#    for link in prob:
#        file.write(link + " " + str(prob[link]) + "\n")

pageRanks = {}
with open("pagerank.txt", "r") as f:
    ranks = f.readlines()
for i in range(len(ranks)):
    ranks[i] = ranks[i].strip().split()
    
mapping_dict = {}
inv_index = {}
for i in range(50):
    inv_indexer(mapping_dict, fileToLowerDict("bfs/" + str(i) + ".html"), 
inv_index)
form = cgi.FieldStorage()
query = form.getvalue("query")
if query is None:
    query = "the"
results = inv_index.get(query)
final = []
for result in results:
    final.append([results[result] * float(ranks[result][1]), "<a href = \"" + ranks[result][0] + "\">" + ranks[result][0] + "</a>"])
final.sort(reverse = True)

html = """<!doctype html>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <title>Results</title>
    </head>
    <body>
	<img src = "logo.png">

        <p>
        {content}
        </p>
     
    </body>
</html>"""

print(html.format(content = str(final))