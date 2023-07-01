import re

string1 = "upload /asdf/dsad/file.txt asdf.txt"
string2 = "upload file.txt asdf.txt"
string3 = "upload file asdf.txt"
string4 = "upload /asdf/dsad/file asdf.txt"

pattern = r"upload\s+(/?[a-zA-Z0-9]+)+(\.[a-zA-Z0-9]+)?\s+([a-zA-Z0-9]+)+(\.[a-zA-Z0-9]+)?"

match1 = re.search(pattern, string1)
match2 = re.search(pattern, string2)
match3 = re.search(pattern, string3)
match4 = re.search(pattern, string4)

if match1:
    print("Pattern found in string1")
else:
    print("Pattern not found in string1")

if match2:
    print("Pattern found in string2")
else:
    print("Pattern not found in string2")

if match3:
    print("Pattern found in string3")
else:
    print("Pattern not found in string3")

if match4:
    print("Pattern found in string4")
else:
    print("Pattern not found in string4")