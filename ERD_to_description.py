from bs4 import BeautifulSoup
import lkml
import os
import pandas as pd
import PyPDF4
import requests
import time
import urllib3.request

def pdfurls(path): 
  # Takes a FiveTran Schema ERD PDF and extracts the urls, returns a list called "urls"

  PDF = PyPDF4.PdfFileReader(path)

  urls = []
  for page in range(PDF.numPages):
    pdfPage = PDF.getPage(page)
    try:
      for item in (pdfPage['/Annots']):
        urls.append(item['/A']['/URI'])
    except KeyError:
      pass
  return urls

def transurls(urls):
  # SQUARE USE CASE SPECIFIC
  # transforms list of urls for square into updated url syntax (square specific use case)
  newurls = []
  for el in urls:
    a = el.split("-")[-1]
    b = f"https://developer.squareup.com/reference/square/objects/{a}"
    newurls.append(b)
  newurls = list(set(newurls))
  return newurls

def tblmetadata(urlpage):
  # takes a Square documentation url, scrapes the page for the table meta data. Returns a dataframe of 
  # Ex1 urlpage = 'https://developer.squareup.com/reference/square/objects/InventoryCount'    # Based on square API docs
  # Ex2 urlpage = 'https://developer.squareup.com/reference/square/objects/Location'

  # use the requests library to get the HTML of the webpage
  response = requests.get(urlpage)

  # parse the html using beautiful soup and store in variable 'soup'
  soup = BeautifulSoup(response.content, 'html.parser')

  # get the title of the table, assign it to "tablename"
  b = soup.find('h1')
  tablename = b.find('span').get_text(strip="True")
  # print(tablename)

  df = pd.DataFrame(columns=['fieldname', 'datatype', 'description', 'tablename'])
  i = 0
  # go through the table of fields, pulling out the fieldname, datatype, and description and putting them in a dataframe
  for el in soup.find_all('tr'):
    fn = el.get('data-test-property')                 # fieldname # <tr class="property-item " data-test-property="calculated_at">
    dt = el.span.get_text(strip="True")               # datatype # <span class="property-item__type" data-test-property-type="">string</span>
    desc = [a.get_text() for a in el.find_all('p')][0]  # description # <p>A read-only timestamp in RFC 3339 format ... ... estimated count.</p>
  
    df.loc[i] = [fn] + [dt] + [desc] + [tablename]
    i += 1

  return tablename, df

def lookmldesc(df):

  for index, line in df.iterrows():             # for each row in the dataframe
    tablename = line[3].lower()           # this is our table name
    name = str(line[0].lower())           # this is our column/field name
    type = str(line[1].strip().lower())   # this is the datatype of the column/field
    description = str(line[2])            # the listed description for this column/field
  return name, tablename, type, description

def descriptions(online, parsed, z):
  # takes a dataframe "online" of online definitions/field descriptions 
  # and a lkml parsed view object "parsed" and adds descriptions to fields found in "online"
  for i in range(0, len(parsed['views'][0]['dimensions'])):
    for field in online['fieldname']:
      if field == parsed['views'][0]['dimensions'][i]['name']:
        desc = online.loc[field, 'description']
        parsed['views'][0]['dimensions'][i]['description'] = desc.replace('\n', ' ')  
        z += 1
  
  # for j in range(0, len(parsed['views'][0]['dimension_groups'])):
  #   for field in online['fieldname']:
  #     if field == parsed['views'][0]['dimension_groups'][j]['name']:
  #       desc = online.loc[field, 'description']
  #       parsed['views'][0]['dimension_groups'][j]['description'] = desc.replace('\n', ' ')  
  #       z += 1
  return z

def main():

  start_time = time.time()
  # dest = input(f"What is your destination folder?")
  # local path to the PDF file from FiveTran
  path = open(f"/Users/jeffreymartinez/Downloads/Square ERD.pdf", 'rb')
  destination = f"/Users/jeffreymartinez/Desktop/block_flo/squaredesc"
  try:
    os.mkdir(destination, )
  except OSError as error:
    print(error)
    print("Running...")

  urls = pdfurls(path)          # Reads PDF, gives list of urls
  newurls = transurls(urls)     # Takes urls, and gives valid square url syntax

  f = {}
  for url in newurls:
    tname, listt = tblmetadata(url) # calls tblmetadata() which creates a dataframe of each documentation page
    tname = tname.lower()
    tname = tname.encode('ascii', 'ignore').decode('unicode_escape')  # alters tname to avoid encoding errors
    f[tname] = listt.set_index("fieldname", drop = False)    # maps each webpage as a dictionary of key: tablename, value: dataframe of fields/descriptions/types
    # print(tname)      # prints each tablename found in online documentation
    # print(listt)

  viewfolder = f"/Users/jeffreymartinez/Desktop/block_flo/block-square/views"   # Get folder of views to edit
  list_of_files = os.listdir(viewfolder)    # creates list of view file names
  full_path = [viewfolder + "/{0}".format(x) for x in list_of_files]    # gives full path of view files

  nomatch = []
  count = 0
  z = 0
  for x in list_of_files:   # iterate through each view file in the folder
    full_path = f"{viewfolder}/{x}"
    count += 1
    s = open(full_path, "r+")
    k = lkml.load(s)
    webmatch = k['views'][0]['name'].replace("_", "")   # viewnames altered to match documentation titles (tnames)
    webmatch = webmatch.encode('ascii', 'ignore').decode('unicode_escape')
    print(f"""
    View name {k['views'][0]['name']} has the following fields:
    """)
    [print(k['views'][0]['dimensions'][i]['name']) for i in range(0, len(k['views'][0]['dimensions']))]
    print(f"""
    """)
    try:
      link = f[webmatch]
      descriptions(link, k, z)
      z = z
      # print(link)  
    except KeyError:
      print(f'No match found for view file named {webmatch}')
      # newmatch = input("Please input a new description tablename to try: ")
      # nlink = f[newmatch]
      # descriptions(nlink, k, z)
      nomatch.append(webmatch)
      pass

    h = open(f"{destination}/{x}", "w+")
    h.write(lkml.dump(k))

  print(f"""
  
  Successfully added descriptions to {z} fields in {count - len(nomatch)} view files. No descriptions found for {len(nomatch)} of {count} total view files. List of files without descriptions:  
  
  {nomatch}""")
  # print the program runtime
  print("--- %s seconds ---" % round(time.time() - start_time, 3))

if __name__== "__main__":
  main()