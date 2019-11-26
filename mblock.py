import csv
import sys
import lkml
import shutil
import time
import os

# for program runtime calculation
start_time = time.time()

# The first argument of this program should be a path to a folder (A lookML project folder with model/dashboards/views)
# The second argument of this program should be a path to their desired destination
# The output will be two folders inside their specified destination -- CORE & CONFIG
# This script DOES NOT ALTER the original source project!

# STEP 1 define source folder and destination folder from arguments
ogproj = str(sys.argv[1])
ccdest = str(sys.argv[2])

# STEP 2 create CORE & CONFIG folders in destination folder
def mtcoreconfig(destinationpath):
  print(f"Creating blank destination directories")
  [os.makedirs("{0}/{1}".format(destinationpath, y), exist_ok=True) for y in ['CORE', 'CONFIG']]
  return

mtcoreconfig(ccdest)

# STEP 3 create LICENSE text files in each of the destination folders
def license(sourcepath, destinationpath):
  print(f"Adding License files")
# iterates through source directory
  for file in os.listdir(sourcepath):     
    ogfilename = os.fsdecode(file)
  # skips any files that start with .
    if ogfilename.startswith("."):    
      continue
  # If LICENSE already exists in source folder, then just copy it to both CORE & CONFIG
    if ogfilename == "LICENSE":       
      print(f"License copied from source project")
      [shutil.copy2(f'{sourcepath}/{ogfilename}', f'{destinationpath}/{x}/{ogfilename}') for x in ['CORE', 'CONFIG']]
  # If LICENSE does NOT exist already, we write it to both CORE & CONFIG
  if not os.path.exists(f'{sourcepath}/LICENSE'): 
    print(f"License file not found in source project, writing License for CORE & CONFIG projects")
    for l in ['CORE', 'CONFIG']:
      f = open(f'{destinationpath}/{l}/LICENSE', 'w+')
      f.write(f"""By downloading/using the source code files located in this GitHub repository (“Components”), you agree to the terms below.

All Components listed herein are Copyright © 2019 Looker Data Sciences, Inc.  All rights reserved.

Certain Components may disclose inventions that may be claimed within patents owned or patent applications filed by Looker Data Sciences, Inc. (Looker). Subject to the terms of the master subscription license agreement located at https://looker.com/terms (the MSA) and this notice, Customers and other users, are granted the limited license set forth in MSA. All terms, including but not limited to, Product Warranty, License and License Restrictions, Disclaimers, and Liability are governed by the MSA terms. Notwithstanding anything to the contrary, all Components are intended for use only with the Looker Product. All capitalized terms not fully defined herein, shall have the same meaning as ascribed to them in the MSA.""")
  return

license(ogproj, ccdest)


def coremodel(sourcepath, destinationpath):
  blockname = sourcepath.split("/")[-1]
  print(f"Writing CORE & CONFIG Manifest files...")
  mfcore = open(f"{destinationpath}/CORE/manifest.lkml", "a+")
  mfcore.write(f"""project_name: "block-{blockname}"
  
################ Constants ################

constant: CONFIG_PROJECT_NAME {{
  value: "block-{blockname}-config"
  export: override_required
}}

constant: CONNECTION_NAME {{
  value: "choose connection"
  export: override_required
}}

### If needed TODO Add more constants here

################ Dependencies ################

local_dependency: {{
  project: "@{{CONFIG_PROJECT_NAME}}"

  #### If needed TODO Add CONFIG constants here that we want overridden by CORE constants

}}
""")

  mfconfig = open(f"{destinationpath}/CONFIG/manifest.lkml", "a+")
  mfconfig.write(f"""project_name: "block-{blockname}-config"
  
################ Constants ################

# If needed TODO Define constants with "export: override_required" declared

""")

# iterates through source directory
  for file in os.listdir(sourcepath):     
    ogfilename = os.fsdecode(file)
    if len(ogfilename.split(".")) <= 1:
      continue
    else:
    # if the source file is a dashboard, we simply copy it over to the CORE
      if ogfilename.split(".")[1] == 'dashboard':
        shutil.copy2(f'{sourcepath}/{ogfilename}', f'{destinationpath}/CORE/{ogfilename}')
    # if the source file is the model, we have to take elements to build explores in CORE & CONFIG
      if ogfilename.split(".")[1] == 'model':
        f = open(f"{destinationpath}/CORE/block_{blockname}_{ogfilename}", 'a+')
        j = open(f"{destinationpath}/CONFIG/{blockname}_{ogfilename}", 'a+')
        print(f"Writing CORE model...")
        f.write(f"""connection: "@{{CONNECTION_NAME}}"

include: "*.view.lkml"
include: "*.explore.lkml"
include: "*.dashboard.lookml"
include: "//@{{CONFIG_PROJECT_NAME}}/*.view.lkml"
include: "//@{{CONFIG_PROJECT_NAME}}/*.model.lkml"
include: "//@{{CONFIG_PROJECT_NAME}}/*.dashboard"

""")
        print(f"Writing CONFIG includes...")
        j.write(f"""include: "*.view
        
""")
      # opens up the source model file 
        with open(f"{sourcepath}/{ogfilename}", 'r') as mfile:
        # uses lkml package to parse through the model file
          parsed = lkml.load(mfile)
          print(f"Parsing source model file...")
          print(f"Writing CORE & CONFIG explores...")
          for a in parsed['explores']:
          # For each source explore, we opens/creates a new file named by the explore, in the specifed destination given by argument
            g = open(f"{destinationpath}/CORE/{a['name']}.explore.lkml", 'w+')    
          # Removes name key, as parser dump includes it for some reason
            b = a.pop("name")                                                     
          # Inside newly created explore file, we write the contents of the original explores
            g.write(f"""explore: {b}_core {{
  extension: required 
  {lkml.dump(a)} 
}}""")                
            g.close()
          # Inside the new model file, we write the content layer explore!  
            f.write(f"""explore: {b} {{
  extends: [{b}_config]
}}

""")        
            j.write(f"""explore: {b}_config {{
  extends: [{b}_core]
  extension: required
}}

""")
          f.close()
          j.close() 
      
      if ogfilename.split(".")[1] == 'view':
        vname = ogfilename.split(".")[0]
        h = open(f"""{destinationpath}/CORE/{vname}_core.view.lkml""", 'w+')
        h.write(f"""include: "//@{{CONFIG_PROJECT_NAME}}/{ogfilename}"

view: {vname} {{
  extends: [{vname}_config]
}}

""")
        d = open(f"""{destinationpath}/CONFIG/{ogfilename}""", 'w+')
        d.write(f"""view: {vname}_config {{
  extends: [{vname}_core]
  extension: required

  # Add view customizations here
  
}}""")

        c = open(f"{sourcepath}/{ogfilename}", 'r')
        contents = c.read()
        h.write(contents)
  print(f"Writing CORE & CONFIG view files...")
  return

coremodel(ogproj, ccdest)

print(f"Don't forget to check for #TODOs in the LookML, and double check project names")
print(f"{sys.argv[0]} program took --- %s seconds ---" % round(time.time() - start_time, 3))
