import csv
import os
import os.path
from os import path
import pandas as pd
import pyfastcopy
import shutil
import sys
import time

# I want to input a directory of csvs, and 
# combine those csvs into one single csv (partyfile)


def main():
  # program runtime calculation
  start_time = time.time()

  def oldestfile(string):   # takes a directory and outputs the oldest file
    list_of_files = os.listdir(string)
    full_path = [string + "/{0}".format(x) for x in list_of_files]
    return min(full_path, key=os.path.getctime)

  def newestfile(string):   # takes a directory and outputs the newest file
    list_of_files = os.listdir(string)
    full_path = [string + "/{0}".format(x) for x in list_of_files]
    return max(full_path, key=os.path.getctime)

  def copyparty(astring):   
    # Takes a path to a directory, looks for partyfile csv. If it does not exist, we create it
    # Then we check if partyfilecp (copy of partyfile) exists.
    # If previous copy already exists, we remove it, then create a fresh copy
    party_path = astring + "/partyfile.csv"
    copy_path = astring + "/partyfilecp.csv"

    if not os.path.exists(party_path):
      first = oldestfile(astring)
      firstdf = pd.read_csv(first)
      pd.DataFrame([firstdf.pop(x) for x in ['Row', 'Export Time UTC']]).T
      firstdf.to_csv(party_path, index=False)
      print(f'Party file did not already exists, so we create a new partyfile')

    # if os.path.exists(copy_path):
    #   os.remove(copy_path)
      # print(f'Copy file already exists, so we delete it and create a new copy')
    shutil.copy2(party_path, copy_path) 
    # print(f'Copyparty function finished')
    return

  copyparty(str(sys.argv[1]))   # takes the first argument as the path for copyparty
  
  def addnewinfo(string, string2):
    # Takes a new file string2, compares it to partyfilecp, then appends only new rows to partyfile
    party_path = string + "/partyfile.csv"
    copy_path = string + "/partyfilecp.csv"

    p1 = pd.read_csv(copy_path) 
    p2 = pd.read_csv(string2)
    pd.DataFrame([p2.pop(x) for x in ['Row', 'Export Time UTC']]).T

    p1.to_csv("p1.csv", index=False)
    p2.to_csv("p2.csv", index=False)
    with open('p1.csv', 'r') as q1, open('p2.csv', 'r') as q2:
      
      fileone = q1.readlines()
      filetwo = q2.readlines()

      with open(party_path, 'a') as outFile:
        for line in filetwo:
          if line not in fileone:
            outFile.write(line)
    [os.remove(x) for x in ['p1.csv', 'p2.csv']]

    shutil.copy2(party_path, copy_path)
    return

  list_of_files = os.listdir(sys.argv[1])
  # full_path = [sys.argv[1] + "/{0}".format(x) for x in list_of_files]
  ct = 0

  for fp in list_of_files:
    if fp.startswith(".") or fp.startswith("partyfile"):
      continue
    addnewinfo(str(sys.argv[1]), str(sys.argv[1]) + "/" + fp)
    ct += 1

  print(str(ct) + " files scanned and added to partyfile.csv")
  # print the program runtime
  print(f'Program took --- %s seconds ---' % round(time.time() - start_time, 3))

if __name__== "__main__":
  main()
