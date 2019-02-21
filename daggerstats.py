#!/usr/bin/python3
import tabulate
import os
from io import BytesIO

list_count = 7
#path_prefix="/usr/share/games/daggerfall/DAGGER/"
path_prefix=""
latest_save_id = 0
for i in range(0,6):
    path = path_prefix+"SAVE"+str(i)+"/SAVEVARS.DAT"
    mod_time = os.path.getmtime(path)
    if mod_time > latest_save_id: new_latest_id = i
    else: new_latest_id = latest_save_id
    latest_save_id = new_latest_id
#   print(mod_time)
#print(latest_save_id)

save_vars_path = path_prefix+"SAVE"+str(latest_save_id)+"/SAVEVARS.DAT"
with open(save_vars_path, "rb") as savevars:
    initial_offset = 6096
    record_size = 92
    savevars.seek(initial_offset,0)
    requests = [("Name",3,26,"c"),\
                ("Power",31,1,"s"),\
                ("Social",54,1,"b"),\
                ("Reputation", 29, 1,"s")]
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
    integers = []
    for i in range(0,8):
        integers.append(i.to_bytes(1,byteorder='little',signed=True))
    social_lookup = {integers[0]:"Commoner",
                     integers[1]:"Merchant",
                     integers[2]:"Scholar",
                     integers[3]:"Nobility",
                     integers[4]:"Underworld",
                     integers[6]:"Supernatural",
                     integers[7]:"Kni/Temp/Vamp"}
    for result in results:
        try: 
            social = social_lookup[result['Social']]
        except KeyError: social = "Undefined"
        result['Social'] = social
    sorted_results = sorted(results, key=lambda k: k['Reputation'])
    haters = sorted_results[:list_count]
    lovers = sorted_results[-list_count:]
    lovers.reverse()

    hater_table = "=============\n    HATERS\n"+tabulate.tabulate(haters,headers="keys",tablefmt="rst")+"\n"
    lover_table = "=============\n    LOVERS\n"+tabulate.tabulate(lovers,headers="keys",tablefmt="rst")+"\n"

    with open("haters.txt", "w") as txt_file: txt_file.write(hater_table)
    with open("lovers.txt", "w") as txt_file: txt_file.write(lover_table)

    sorted_results = sorted(results, key=lambda k: k['Power'], reverse=True)
    faction_table = "=============\n FACTIONS \n"+tabulate.tabulate(sorted_results,headers="keys",tablefmt="rst")+"\n"
    with open("factions.txt", "w") as txt_file: txt_file.write(faction_table)

save_tree_path = path_prefix+"SAVE"+str(latest_save_id)+"/SAVETREE.DAT"
with open(save_tree_path, "rb") as savetree:
    initial_offset = 19
    cur_record_size = 0

    savetree.seek(initial_offset,0)
    for i in range(0,442):
        cur_record_size = int.from_bytes(savetree.read(4),byteorder='little')
        if cur_record_size > 0:
            record_type_id = savetree.read(1)
            print("Record "+str(i)+": <"+str(cur_record_size)+"> "+record_type_id.hex())
            if record_type_id == int(3).to_bytes(1,byteorder='little',signed=True):
                print("CHARACTER_RECORD!!")
                character_record = BytesIO(savetree.read(cur_record_size))
                seek_offset = cur_record_size + 1
            else:
                seek_offset = cur_record_size + 1
                print(savetree.read(cur_record_size))
            seek = cur_record_size - seek_offset
            savetree.seek(seek,1)
        else: 
            print("Record "+str(i)+": <0>")
            pass
    character_record.seek(658)
    print(character_record.read(24))
    print(int.from_bytes(character_record.read(2),byteorder='little',signed=True))
    print(character_record.read(32))
