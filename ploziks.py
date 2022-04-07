import numpy as np

res_ploziks = []
ploziks = []
str_res = ''

with open('res/ploziks.txt', mode='r', encoding='utf8') as file:
    for line in file:
        res_ploziks.append(line)

for i, elem in enumerate(res_ploziks):
    try:
        if elem != '\n' and res_ploziks[i + 1] == '\n':
            str_res += elem
            ploziks.append(str_res)
            str_res = ''
        elif elem != '\n' and res_ploziks[i + 1] != '\n':
            str_res += elem
    except:
        str_res += elem
        ploziks.append(str_res)
        str_res = ''

ploziks = np.array(ploziks)


def rand_ploz():
    global ploziks
    np.random.shuffle(ploziks)
    return ploziks[0]
