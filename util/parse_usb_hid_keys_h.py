# modified from https://gist.github.com/gsora/45ba7b98d31929e75317908a97488ef1

file = open("usb_hid_keys.h", "r")

module_str = 'hid_key_map = {'

for line in file:
    goodline = line[8:].split(" ")
    if line.startswith("#define ") and len(goodline)>1:
        key = goodline[0]
        value = ""
        for i in range(1, len(goodline)):
            if goodline[i] == "":
                continue
            else:
                value = goodline[i].rsplit()[0]
                break

        module_str += "\'{}\': {},\n".format(key, value)

module_str += '}'
with open('hid_keys.py', 'w') as file:
    file.write(module_str)
    file.flush()
    file.close()
