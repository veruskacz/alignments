import os
import shutil
from shutil import copytree, ignore_patterns
import codecs
from os import listdir
from os.path import isfile, join
from kitchen.text.converters import to_bytes, to_unicode


inputPath1 = "C:\Users\Al\Documents\\tests\\1960a.sec01.txt"
folder = "C:\Users\Al\Dropbox\@VU\Ve\BOM"


def bom_copy(directory, extension_condition=".txt"):

    check = ""
    try:
        # LIST OF FILES IN THE FOLDER
        files = [f for f in listdir(directory) if isfile(join(directory, f))]
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

                    cur_path = join(directory, files[i])
                    copy_name = "{}_copy{}".format(file_name, extension)
                    copy_path = join(directory, "copied", copy_name)

                    if not os.path.exists(join(directory, "copied")):
                        os.makedirs(join(directory, "copied"))
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


def move_file(directory, extension_condition=".txt", ignore=".txt"):
    copytree("E:\data\experiments_2017\Voice recorder", "D:\data\VoiceRecorder20170827", ignore=ignore_patterns('*.txt'))
    src = "E:\data\experiments_2017\Voice recorder"
    dst = "D:\data\VoiceRecorder20170827"
    print "Done!!!!"
    # names = os.listdir(src)
    # if ignore is not None:
    #     ignored_names = ignore(src, names)
    # else:
    #     ignored_names = set()
    #
    # os.makedirs(dst)
    # errors = []
    # for name in names:
    #     if name in ignored_names:
    #         continue
    #     srcname = os.path.join(src, name)
    #     dstname = os.path.join(dst, name)
    #     try:
    #         if symlinks and os.path.islink(srcname):
    #             linkto = os.readlink(srcname)
    #             os.symlink(linkto, dstname)
    #         elif os.path.isdir(srcname):
    #             copytree(srcname, dstname, symlinks, ignore)
    #         else:
    #             copy2(srcname, dstname)
    #         # XXX What about devices, sockets etc.?
    #     except (IOError, os.error) as why:
    #         errors.append((srcname, dstname, str(why)))
    #     # catch the Error from the recursive copytree so that we can
    #     # continue with other files
    #     except Error as err:
    #         errors.extend(err.args[0])
    # try:
    #     copystat(src, dst)
    # except WindowsError:
    #     # can't copy file access times on Windows
    #     pass
    # except OSError as why:
    #     errors.extend((src, dst, str(why)))
    # if errors:
    #     raise Error(errors)


move_file("", extension_condition=".txt")

"http://visjs.org/showcase/index.html"