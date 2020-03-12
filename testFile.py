import json

'''
detail_url_list = []
with open("I:\Temp\movie_url_1.json", "r", encoding="utf-8") as f:
    dict_data = json.load(f)
    print(type(dict_data))
    movie_url_list = []
    #   dict.pop(key="url",default=None)
    for v in dict_data.values():
        # print(v,type(v))
        movie_url_list.append(v)
    print(list(movie_url_list))
    print("read end!")
    with open("I:\Temp\movie_url_pcopy.json", "w", encoding="utf-8") as f:
        url_data = {}
        #movie_url_list = movie_url_list
        for index, value in enumerate(movie_url_list, start=1):
            rank_url = "url_" + str(index)
            url_data[rank_url] = value
        url_data = json.dumps(url_data, ensure_ascii=False, indent=4,separators=(",",":"))
        f.write(url_data)
        print("write end!")
'''

import json


def read_item(path):
    fpr = open(path, mode="r", encoding="utf-8")
    return fpr

def write_item(path):
    fpw = open(path, mode="a", encoding="utf-8")
    return fpw

def close_file(fp):
    fp.close()


fpr = read_item("I:\Temp\movie_url_1.json")
data = json.load(fpr)
print(type(data))
fpw = write_item("I:\Temp\movie_wa.json")
count = 1
for item in data.items():
    fpw.write(json.dumps(item, ensure_ascii=False))
    fpw.flush()
    count += 1
    print(count)
    if count == 250:
        try:
            # fpw.seek(offset= 10) # 看看offset起始值，whence 在w w+ a 时的变化
            fpw.write(json.dumps(item, ensure_ascii=False))
            print(count)
        except IndexError as e:
            print(e)
        finally:
            close_file(fpr)
            close_file(fpw)
close_file(fpr)
close_file(fpw)

# def fib(max):
#     n, a, b = 0, 0, 1
#     while n < max:
#         yield b
#         a, b = b, a + b
#         n = n + 1
#     return 'done'
#
# for i in fib(5):
#     print(i)
