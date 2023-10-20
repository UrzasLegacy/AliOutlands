def parse_csv_file():
    file_path = "C:\\Users\\Sean\\Desktop\\UO\\Orion Script Backups\\VSC Orion Workspace\\AliOutlands\\ItemData_3.csv"
    new_file_path = "C:\\Users\\Sean\\Desktop\\UO\\Orion Script Backups\\VSC Orion Workspace\\AliOutlands\\ItemData_3parsedWEAPON.csv"
    with open(file_path, 'r') as read_file, open(new_file_path, 'w') as write_file:
        for line in read_file:
            line = line.strip()
            if line[0] == '#':
                write_file.write(line)
                continue
            split_line = line.split(';')
            ItemID = split_line[1]
            Name = split_line[2]
            Weight_Quantity = split_line[3]
            Layer_Quality = split_line[4]
            Gump_AnimID = split_line[5]
            Height = split_line[6]
            Class_Quantity = split_line[8]
            StackingOffset = split_line[9]
            MiscData = split_line[10]
            Background = split_line[14]
            Weapon = split_line[15]
            Transparent = split_line[16]
            Translucent = split_line[17]
            Wall = split_line[18]
            Damage = split_line[19]
            Impassible = split_line[20]
            Wet = split_line[21]
            Unknow1 = split_line[22]
            Surface = split_line[23]
            Bridge = split_line[24]
            Generic = split_line[25]
            Window = split_line[26]
            NoShoot = split_line[27]
            PrefixA = split_line[28]
            PrefixAn = split_line[29]
            Internal = split_line[30]
            Foliage = split_line[31]
            PartialHue = split_line[32]
            Unknow2 = split_line[33]
            Map = split_line[34]
            Container_Height = split_line[35]
            Wearable = split_line[36]
            Lightsource = split_line[37]
            Animation = split_line[38]
            HoverOver = split_line[39]
            Unknow3 = split_line[40]
            Armor = split_line[41] # all armor is covered by Wearable
            Roof = split_line[42]
            Door = split_line[43]
            StairBack = split_line[44]
            StairRight = split_line[45]



            out_write = line + '\n'#ItemID + '|'
            # if Window != '0':
            #     write_file.write(out_write)
            # continue
#INCLUSIVES
    #PreExclude
            if Layer_Quality == '11': # hairstyles
                continue
            if Class_Quantity == '11': # hairstyles
                continue
    #Include
            if Wearable == '1':
                write_file.write(out_write)
                continue
            if Weapon == '1': # 4 graphics not covered by Wearable: 4139|4235|5742|5743
                write_file.write(out_write)
                continue
#EXCLUSIVES
            if Name == '' or Name == 'spelleffect' or Name == 'NoName' or Name == 'Missing_Name':
                continue
            if "bodytattoo" in Name:
                continue
            if Wall != '0':
                continue
            if Door != '0':
                continue
            if Damage != '0':
                continue
            if Surface != '0':
                continue
            if Wet != '0':
                continue
            if Foliage != '0':
                continue
            if Window != '0':
                continue
            if Bridge != '0':
                continue
            if Roof != '0':
                continue
            if StairBack != '0':
                continue
            if StairRight != '0':
                continue
            # if Weight_Quantity == '255' and (Layer_Quality == '11' or Layer_Quality == '5'):
            #     continue
            write_file.write(out_write)

parse_csv_file()