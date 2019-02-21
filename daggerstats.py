#!/usr/bin/python3
import tabulate

with open("SAVE1/SAVEVARS.DAT", "rb") as savevars:
    initial_offset = 6096
    record_size = 92
    savevars.seek(initial_offset,0)
    requests = [("Faction Name",3,26,"c"),\
                ("Character Reputation", 29, 1,"s")]
    results = []
    for i in range(0, 366):
        pos = 0
#       print("Record "+ str(i)+":")
        result = {}
        for request in requests:
            desc = request[0]
            seek = request[1] - pos
            read = request[2]
            dtype = request[3]
            if dtype == "s": read = read*2
            savevars.seek(seek,1)
            pos = pos + seek
            data = savevars.read(read)
            pos = pos + read
            data_str =""
            if dtype == "b":
                data_s = data
            elif dtype == "c":
                stripped_data = data.rstrip(b'\0')
                data_s = str(stripped_data)[2:-1]
            elif dtype == "s":
                data_s = int.from_bytes(data, byteorder='little', signed=True)
#           print("\t"+desc+":\t"+data_s)
            result[desc] = data_s
        results.append(result)
#       print("\n")
        seek_value = record_size - pos
        savevars.seek(seek_value,1)
    sorted_results = sorted(results, key=lambda k: k['Character Reputation'])
    haters = sorted_results[:15]
    lovers = sorted_results[-15:]
    lovers.reverse()

    hater_table = "=============\n    HATERS\n"+tabulate.tabulate(haters,headers="keys",tablefmt="rst")+"\n"
    lover_table = "=============\n    LOVERS\n"+tabulate.tabulate(lovers,headers="keys",tablefmt="rst")+"\n"

    with open("haters.txt", "w") as txt_file: txt_file.write(hater_table)
    with open("lovers.txt", "w") as txt_file: txt_file.write(lover_table)

