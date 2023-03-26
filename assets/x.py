import re
import sys
import json

with open(sys.argv[1]) as f:
    d = dict()
    for line in f:
        res = re.search(r'^(.*) (http://.*)', line)
        d[res.group(1)] = res.group(2)
    
with open('links.json', 'w') as f:
    f.write(json.dumps(d, indent=4))
