# takes the name of a view and puts it into core view content layer extension syntax
# start by copying the root view name (no _config/_core) to your clipboard 
#
# If I have the text "redshift_data_loads" copied to my clipboard, then I run 
# python core_view_ext.py
# the contents of my clipboard becomes the following:
# 
#   include: "//@{CONFIG_PROJECT_NAME}/redshift_data_loads_config.view"
#
#   view: redshift_data_loads {
#       extends: [redshift_data_loads_config]
#   }

import sys
import clipboard

x = clipboard.paste()
# str(sys.argv[1])

f = "include: \"//@{CONFIG_PROJECT_NAME}/" + x + "_config.view\"\n\nview: " + \
    x + " {\n\textends: [" + x + "_config]\n}"

clipboard.copy(f)
print(f + "\n\n\n\n^^^ Text above copied to clipboard ^^^\n")
