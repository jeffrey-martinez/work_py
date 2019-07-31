# takes the name of a view and puts it into config view definition syntax
# start by copying the base view name to your clipboard 
#
# If I have the text "columns" copied to my clipboard, then I run 
# python config_view.py
# the contents of my clipboard becomes the following:
# 
#   view: columns_config {
#       extends: [columns_core]
#       extension: required
#   }

import sys
import clipboard

x = clipboard.paste()
# str(sys.argv[1]) # this is if we want to use an argument instead (i.e. python config_view.py columns)

f = "view: " + x + "_config {\n\textends: [" + \
    x + "_core]\n\textension: required\n}"

clipboard.copy(f)
print("\n" + f + "\n\n\n\n^^^ Text above copied to clipboard ^^^\n")
