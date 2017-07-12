import codecs
from os import listdir
from os.path import isfile, isdir, join
import os
from kitchen.text.converters import to_bytes, to_unicode
inputPath1 = "C:\Users\Al\Documents\\tests\\1960a.sec01.txt"
folder = "C:\Users\Al\Dropbox\@VU\Ve\BOM"

def bom_copy (folder, extension_condition=".txt"):

    check = ""
    try:
    # if True:
        # LIST OF FILES IN THE FOLDER
        files = [f for f in listdir(folder) if isfile(join(folder, f))]
        print "\nThis folder contains {} files out of which:\n".format(len(files))

        for i in range(len(files)):

            bom = ""
            split_name = os.path.splitext(files[i])
            # print files[i]

            if len(split_name) == 2:
                file_name = split_name[0]
                extension = split_name[1]

                # FILES THAT SATISFY THE FILE EXTENSION CONDITION
                if extension.lower() == extension_condition.lower():

                    cur_path = join(folder, files[i])
                    copy_name = "{}_copy{}".format(file_name, extension)
                    copy_path = join(folder, "copied", copy_name)

                    if not os.path.exists(join(folder, "copied")):
                        os.makedirs(join(folder, "copied"))
                        # os.chmod(join(folder, "copied"), 0o777)

                    # READ FILE FROM DISK
                    read_file = open(cur_path, 'rb')

                    # READ THE FIRST LINE
                    first_line = to_bytes(read_file.readline())


                    if first_line.startswith(to_bytes(codecs.BOM_UTF8)):
                        # print "FIRST LINE:", first_line

                        # COPY FILE TO DISK
                        write_file = open(copy_path, 'wb')

                        print "{:3} [{}] contains BOM".format(i + 1, files[i])
                        print "{:3} and was copied without the BOM as [{}]\n".format("", copy_name)
                        bom += first_line[:len(to_bytes(codecs.BOM_UTF8))]
                        first_line = first_line.replace(bom, '')

                        # WRITE THE FIRST LINE WITHOUT THE BOM
                        write_file.write(first_line)

                        # WRITE THE REST OF TEXT
                        while True:
                            line = to_unicode(read_file.readline())

                            if not line:
                                # print "Done"
                                write_file.close()
                                break
                            check = line
                            write_file.write(to_bytes(line))

                        read_file.close()

    except Exception as err:
        print "\tProblem at line: ", check
        print "\tProblem:", err

bom_copy(folder, extension_condition=".txt")
