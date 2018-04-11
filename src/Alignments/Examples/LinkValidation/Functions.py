# encoding=utf-8

import os
import re
import math
import cStringIO as Buffer
import Alignments.UserActivities.Clustering as Cls
import Alignments.Settings as St
from os import listdir, system, path  # , startfile
from Alignments.Utility import normalise_path as nrm
from os.path import join, isdir, isfile
import codecs  # , subprocess
import Alignments.Utility as Ut

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    TEST FUNCTIONS
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""


def sigmoid(x, par=1.6):
    # return math.exp(x)/ (math.exp(x) + 10)
    return x / float(math.fabs(x) + par)


# for i in range(11):
#    print "{:14}  {:14} {:14}".format(sigmoid(i, 1.5), sigmoid(i, 1.6), sigmoid(i, 1.9))


def folder_check0(file_1, file_2, diff_1=False, diff_2=False, intersection=False,
                  tracking=None, track_dir=None, activated=False):

    if activated is False:
        return None
    print "PATH: ", file_1
    q_keyword = "\tQUALITY USED"
    # b_keyword = "\tBRIDGES USED"
    # d_keyword = "\tDIAMETER USED"
    set_a = set([])
    set_b = set([])
    folders_1 = []
    folders_2 = []

    if path.isdir(file_1):
        folders_1 = [f for f in listdir(nrm(file_1)) if isdir(join(nrm(file_1), f))]
        set_a = set(folders_1)

    if path.isdir(file_2):
        folders_2 = [f for f in listdir(nrm(file_2)) if isdir(join(nrm(file_2), f))]
        set_b = set(folders_2)

    print "\nPATH 1: {}".format(len(folders_1))
    print "PATH 2: {}".format(len(folders_2))

    # Dynamically get path to AcroRD32.exe
    # acro_read = winreg.QueryValue(winreg.HKEY_CLASSES_ROOT, 'Software\\Adobe\\Acrobat\Exe')

    if diff_1 is True:
        diff = set_a - set_b
        print "\nDIFF(FOLDER_1 [{}] - FOLDER_2 [{}]) = [{}]".format(len(folders_1),  len(folders_2), len(diff))
        count = 0
        good = 0
        # acceptable = 0
        uncertain = 0
        bad = 0
        print "diff"
        for item in diff:
            count += 1
            output = "\t>>> {}".format(item)
            target = join(nrm(file_1), item)
            doc = [f for f in listdir(nrm(target)) if join(nrm(target), f).endswith('.txt')]
            print item

            if doc:
                target_path = join(nrm(target), doc[0])
                read = open(target_path)
                while True:
                    node = read.readline()
                    print len(node)
                    if len(node) == 0:
                        break
                    if node.startswith(q_keyword):
                        print node
                        value = float(node.replace(q_keyword, "").replace(":", "").strip())
                        if value <= 0.1:
                            good += 1
                            output = "{:<22}{:12}\t{}".format(output, "GOOD", value)

                        elif value >= 0.25:
                            bad += 1
                            output = "{:<22}{:12}\t{}".format(output, "BAD", value)
                            break
                        elif (value > 0.1) and (value < 0.25):
                            uncertain += 1
                            output = "{:<22}{:12}\t{}".format(output, "UNDECIDED",  value)
                read.close()

            print "========================================================================="
            print output

            # doc2 = [f for f in listdir(nrm(target)) if join(nrm(target), f).endswith('.pdf')]

            # OPEN THE PDF FROM DEFAULT READER
            # target_path2 = join(nrm(target), doc2[0])
            # system(target_path2)
            # startfile(target_path2)

            # OPEN WITH ADOBE
            # cmd = '{0} /N /T "{1}" ""'.format(acro_read, target_path2)
            # print "PRINTING PDF"
            # subprocess.Popen(cmd)

            # reading = open(target_path2)
            # print reading.read()
            if doc and tracking is True:
                target_path = join(nrm(target), doc[0])
                read = open(target_path)
                for i in range(0, 6):
                    node = read.readline().strip()
                read.close()
                print "\t{}-TRACKING {}".  format(count, node)
                track(directory=track_dir, resource=node, activated=activated)
                next_step = raw_input("\n\tCONTINUE?\t")
                if next_step.lower() == "yes" or next_step.lower() == "y" or next_step.lower() == "1":
                    continue
                else:
                    exit(0)

        print "GOOD {0}/{3} BAD {1}/{3} UNCERTAIN {2}/{3}".format(good, bad, uncertain, len(diff))

    if diff_2 is True:
        count = 0
        good = 0
        bad = 0
        uncertain = 0
        diff = set_b - set_a
        print "\nDIFF(FOLDER_2 [{}] - FOLDER_1 [{}]) = [{}]".format(len(folders_2), len(folders_1), len(diff))
        for item in diff:
            count += 1
            output = "\t>>> {}".format(item)
            target = join(nrm(file_2), item)
            doc = [f for f in listdir(nrm(target)) if join(nrm(target), f).endswith('.txt')]
            # doc2 = [f for f in listdir(nrm(target)) if join(nrm(target), f).endswith('.pdf')]

            if doc:
                target_path = join(nrm(target), doc[0])
                read = open(target_path)
                while True:
                    node = read.readline()
                    if len(node) == 0:
                        break
                    if node.startswith(q_keyword):
                        value = float(node.replace(q_keyword, "").replace(":", "").strip())
                        if value <= 0.1:
                            good += 1
                            output = "{:<22}{:12}\t{}".format(output, "GOOD", value)
                        elif value >= 0.25:
                            bad += 1
                            output = "{:<22}{:12}\t{}".format(output, "BAD", value)
                            break
                        elif (value > 0.1) and (value < 0.25):
                            uncertain += 1
                            output = "{:<22}{:12}\t{}".format(output, "UNDECIDED",  value)
                read.close()
            print output

            if doc and tracking is True:
                target_path = join(nrm(target), doc[0])
                read = open(target_path)
                for i in range(0, 6):
                    node = read.readline().strip()
                read.close()
                print "\t{}-TRACKING {}".  format(count, node)
                track(directory=track_dir, resource=node, activated=activated)
                next_step = raw_input("\n\tCONTINUE?\t")
                if next_step.lower() == "yes" or next_step.lower() == "y" or next_step.lower() == "1":
                    continue
                else:
                    exit(0)
        print "GOOD {0}/{3} BAD {1}/{3} UNCERTAIN {2}/{3}".format(good, bad, uncertain, len(diff))

    if intersection is True:
        diff = set_a.intersection(set_b)
        print "\nINTERSECTION(FOLDER_1 [{}] - FOLDER_2 [{}]) [{}]".format(
            len(folders_1), len(folders_2), len(diff))
        good = 0
        bad = 0
        uncertain = 0
        for item in diff:
            output = "\t>>> {}".format(item)
            target = join(nrm(file_2), item)
            doc = [f for f in listdir(nrm(target)) if join(nrm(target), f).endswith('.txt')]
            # doc2 = [f for f in listdir(nrm(target)) if join(nrm(target), f).endswith('.pdf')]

            if doc:
                target_path = join(nrm(target), doc[0])
                read = open(target_path)
                while True:
                    node = read.readline()
                    if len(node) == 0:
                        break
                    if node.startswith(q_keyword):
                        value = float(node.replace(q_keyword, "").replace(":", "").strip())
                        if value <= 0.1:
                            good += 1
                            output = "{:<22}{:12}\t{}".format(output, "GOOD", value)
                        elif value >= 0.25:
                            bad += 1
                            output = "{:<22}{:12}\t{}".format(output, "BAD", value)
                            break
                        elif (value > 0.1) and (value < 0.25):
                            uncertain += 1
                            output = "{:<22}{:12}\t{}".format(output, "UNDECIDED",  value)
                read.close()
            print output
        print "GOOD {0}/{3} BAD {1}/{3} UNCERTAIN {2}/{3}".format(good, bad, uncertain, len(diff))


def folder_check(file_1, file_2, diff_1=False, diff_2=False, intersection=False, save_in="",
                 tracking=None, track_dir=None, plot_dict=None, detailed=False, activated=False,):

    if activated is False:
        return None

    # print "PATH: ", file_1
    q_keyword = "\tQUALITY USED"
    b_keyword = "\tBRIDGES"
    d_keyword = "\tDIAMETER"
    set_a = set([])
    set_b = set([])
    folders_1 = []
    folders_2 = []
    builder = Buffer.StringIO()

    if path.isdir(file_1):
        folders_1 = [f for f in listdir(nrm(file_1)) if isdir(join(nrm(file_1), f))]
        set_a = set(folders_1)

    if path.isdir(file_2):
        folders_2 = [f for f in listdir(nrm(file_2)) if isdir(join(nrm(file_2), f))]
        set_b = set(folders_2)

    # print "\nPATH 1: {}".format(len(folders_1))
    # print "PATH 2: {}".format(len(folders_2))

    # Dynamically get path to AcroRD32.exe
    # acro_read = winreg.QueryValue(winreg.HKEY_CLASSES_ROOT, 'Software\\Adobe\\Acrobat\Exe')
    line = "========================================================================="
    output_format = "{:<22}{:12}{:12}{:12}{:12}"
    plot_format = "({},{})"
    header = "\n{}\n\t{:<21}{:12}{:>12}{:>12}{:>12}\n{}".format(
        line, "NETWORK", "QUALITY", "ESTIMATION", "BRIDGE", "DIAMETER", line)

    if diff_1 is True:
        diff = set_a - set_b
        print "DIFF(FOLDER_1 [{}] - FOLDER_2 [{}]) = [{}]".format(len(folders_1),  len(folders_2), len(diff))
        print header

        count = 0
        good = 0
        acceptable = 0
        uncertain = 0
        bad = 0
        # print "diff"
        for item in diff:
            count += 1
            output = "\t>>> {}".format(item)
            target = join(nrm(file_1), item)
            doc = [f for f in listdir(nrm(target)) if join(nrm(target), f).endswith('.txt')]
            # print item

            if doc:
                b_value = 100
                d_value = 100
                target_path = join(nrm(target), doc[0])
                read = open(target_path)

                while True:

                    node = read.readline()
                    # print len(node)
                    if len(node) == 0:
                        break
                    # BRIDGE VALUE
                    if node.startswith(b_keyword):
                        b_value = float(node.replace(b_keyword, "").replace(":", "").strip())
                    # DIAMETER VALUE
                    if node.startswith(d_keyword):
                        d_value = float(node.replace(d_keyword, "").replace(":", "").strip())
                    # ESTIMATED QUALITY VALUE
                    if node.startswith(q_keyword):
                        q_value = float(node.replace(q_keyword, "").replace(":", "").strip())
                        # print node

                        if q_value <= 0.1:
                            good += 1
                            output = "{:<22}{:12}{:12}{:12}{:12}".format(output, "GOOD", q_value, b_value, d_value)

                        elif (b_value == 0) and (d_value < 3):
                            acceptable += 1
                            output = "{:<22}{:12}{:12}{:12}{:12}".format(output,
                                                                         "ACCEPTABLE", q_value, b_value, d_value)

                        elif ((q_value > 0.1) and (q_value < 0.25)) or (b_value == 0):
                            uncertain += 1
                            output = "{:<22}{:12}{:12}{:12}{:12}".format(output, "UNCERTAIN", q_value, b_value, d_value)

                        elif q_value >= 0.25:
                            bad += 1
                            output = "{:<22}{:12}{:12}{:12}{:12}".format(output, "BAD", q_value, b_value, d_value)
                            break

                read.close()

            if detailed is True:
                print output
                print line

            # doc2 = [f for f in listdir(nrm(target)) if join(nrm(target), f).endswith('.pdf')]

            # OPEN THE PDF FROM DEFAULT READER
            # target_path2 = join(nrm(target), doc2[0])
            # system(target_path2)
            # startfile(target_path2)

            # OPEN WITH ADOBE
            # cmd = '{0} /N /T "{1}" ""'.format(acro_read, target_path2)
            # print "PRINTING PDF"
            # subprocess.Popen(cmd)

            # reading = open(target_path2)
            # print reading.read()
            if doc and tracking is True:
                target_path = join(nrm(target), doc[0])
                read = open(target_path)
                for i in range(0, 6):
                    node = read.readline().strip()
                read.close()
                print "\t{}-TRACKING {}".  format(count, node)
                track(directory=track_dir, resource=node, activated=activated)
                next_step = raw_input("\n\tCONTINUE?\t")
                if next_step.lower() == "yes" or next_step.lower() == "y" or next_step.lower() == "1":
                    continue
                else:
                    exit(0)

        if len(diff) > 0:
            print "TOTAL [{3}]  GOOD [{0}]  ACCEPTABLE [{4}]    UNCERTAIN[{2}]  BAD [{1}]".format(
                good, bad, uncertain, len(diff), acceptable)

            print "TOTAL [{3}]  GOOD [{0}%]  ACCEPTABLE [{4}%]    UNCERTAIN[{2}%]  BAD [{1}%]".format(
                round(float(good) / len(diff) * 100, 2), round(float(bad) / len(diff) * 100, 2),
                round(float(uncertain) / len(diff) * 100, 2), len(diff), round(float(acceptable) / len(diff) * 100, 2))

    if diff_2 is True:
        count = 0
        good = 0
        acceptable = 0
        bad = 0
        uncertain = 0
        diff = set_b - set_a
        print "\nDIFF(FOLDER_2 [{}] - FOLDER_1 [{}]) = [{}]".format(len(folders_2), len(folders_1), len(diff))
        print header

        for item in diff:
            count += 1
            output = "\t>>> {}".format(item)
            target = join(nrm(file_2), item)
            doc = [f for f in listdir(nrm(target)) if join(nrm(target), f).endswith('.txt')]
            # doc2 = [f for f in listdir(nrm(target)) if join(nrm(target), f).endswith('.pdf')]

            if doc:
                b_value = 100
                d_value = 100
                target_path = join(nrm(target), doc[0])
                read = open(target_path)

                while True:

                    node = read.readline()
                    # print len(node)
                    if len(node) == 0:
                        break
                    # BRIDGE VALUE
                    if node.startswith(b_keyword):
                        b_value = float(node.replace(b_keyword, "").replace(":", "").strip())
                    # DIAMETER VALUE
                    if node.startswith(d_keyword):
                        d_value = float(node.replace(d_keyword, "").replace(":", "").strip())
                    # ESTIMATED QUALITY VALUE
                    if node.startswith(q_keyword):
                        q_value = float(node.replace(q_keyword, "").replace(":", "").strip())
                        # print node

                        if q_value <= 0.1:
                            good += 1
                            output = "{:<22}{:12}{:12}{:12}{:12}".format(output, "GOOD", q_value, b_value, d_value)

                        elif (b_value == 0) and (d_value < 3):
                            acceptable += 1
                            output = "{:<22}{:12}{:12}{:12}{:12}".format(
                                output, "ACCEPTABLE", q_value, b_value, d_value)

                        elif ((q_value > 0.1) and (q_value < 0.25)) or (b_value == 0):
                            uncertain += 1
                            output = "{:<22}{:12}{:12}{:12}{:12}".format(output, "UNCERTAIN", q_value, b_value, d_value)

                        elif q_value >= 0.25:
                            bad += 1
                            output = "{:<22}{:12}{:12}{:12}{:12}".format(output, "BAD", q_value, b_value, d_value)
                            break

                read.close()

            if detailed is True:
                print output
                print line

            if doc and tracking is True:
                target_path = join(nrm(target), doc[0])
                read = open(target_path)
                for i in range(0, 6):
                    node = read.readline().strip()
                read.close()
                print "\t{}-TRACKING {}".  format(count, node)
                track(directory=track_dir, resource=node, activated=activated)
                next_step = raw_input("\n\tCONTINUE?\t")
                if next_step.lower() == "yes" or next_step.lower() == "y" or next_step.lower() == "1":
                    continue
                else:
                    exit(0)

        if len(diff) > 0:
            print "TOTAL [{3}]  GOOD [{0}]  ACCEPTABLE [{4}]    UNCERTAIN[{2}]  BAD [{1}]".format(
                good, bad, uncertain, len(diff), acceptable)

            print "TOTAL [{3}]  GOOD [{0}%]  ACCEPTABLE [{4}%]    UNCERTAIN[{2}%]  BAD [{1}%]".format(
                round(float(good) / len(diff) * 100, 2), round(float(bad) / len(diff) * 100, 2),
                round(float(uncertain) / len(diff) * 100, 2), len(diff), round(float(acceptable) / len(diff) * 100, 2))

    if intersection is True:
        diff = set_a.intersection(set_b)
        builder.write("\nINTERSECTION(FOLDER_1 [{}] - FOLDER_2 [{}]) [{}]\n".format(
            len(folders_1), len(folders_2), len(diff)))
        # builder.write("LOOKING INTO FILE-2: {}\n".format(file_2))
        builder.write(header)
        good = 0
        acceptable = 0
        bad = 0
        uncertain = 0
        plot = ""
        plot_dic = dict()
        count = 0
        for item in diff:

            count += 1
            output = "\n\t>>> {}".format(item)

            target = join(nrm(file_2), item)
            doc = [f for f in listdir(nrm(target)) if join(nrm(target), f).endswith('.txt')]
            # doc2 = [f for f in listdir(nrm(target)) if join(nrm(target), f).endswith('.pdf')]

            if doc:
                b_value = 100
                d_value = 100
                target_path = join(nrm(target), doc[0])
                read = open(target_path)
                while True:

                    node = read.readline()
                    # print len(node)
                    if len(node) == 0:
                        break
                    # BRIDGE VALUE
                    if node.startswith(b_keyword):
                        b_value = float(node.replace(b_keyword, "").replace(":", "").strip())
                    # DIAMETER VALUE
                    if node.startswith(d_keyword):
                        d_value = float(node.replace(d_keyword, "").replace(":", "").strip())
                    # ESTIMATED QUALITY VALUE
                    if node.startswith(q_keyword):
                        q_value = float(node.replace(q_keyword, "").replace(":", "").strip())
                        # print node

                        if q_value <= 0.1:
                            good += 1
                            output = output_format.format(output, "GOOD", q_value, b_value, d_value)
                            plot += plot_format.format(count, "4")
                            plot_dic[item] = (count, "4")

                        elif (b_value == 0) and (d_value < 3):
                            acceptable += 1
                            output = output_format.format(output, "ACCEPTABLE", q_value, b_value, d_value)
                            plot += plot_format.format(count, "3")
                            plot_dic[item] = (count, "3")

                        elif ((q_value > 0.1) and (q_value < 0.25)) or (b_value == 0):
                            uncertain += 1
                            output = output_format.format(output, "UNCERTAIN", q_value, b_value, d_value)
                            plot += plot_format.format(count, "2")
                            plot_dic[item] = (count, "2")

                        elif q_value >= 0.25:
                            bad += 1
                            output = output_format.format(output, "BAD", q_value, b_value, d_value)
                            plot += plot_format.format(count, "1")
                            plot_dic[item] = (count, "1")
                            break

                read.close()

            if detailed is True:
                builder.write("{}\n".format(output))
                builder.write("{}".format(line))

        builder.write("\nTOTAL=[{3}]  GOOD=[{0}]  ACCEPTABLE=[{4}]    UNCERTAIN=[{2}]  BAD=[{1}]\n".format(
            good, bad, uncertain, len(diff), acceptable))
        if len(diff) > 0:
            builder.write("TOTAL=[{3}]  GOOD=[{0}%]  ACCEPTABLE=[{4}%]    UNCERTAIN=[{2}%]  BAD=[{1}%]\n".format(
                round(float(good) / len(diff) * 100, 2), round(float(bad) / len(diff) * 100, 2),
                round(float(uncertain) / len(diff) * 100, 2), len(diff), round(float(acceptable) / len(diff) * 100, 2)))

        #################
        # RANDOM CLUSTERS
        #################
        random_plot = "\\addplot [color=blue] coordinates {"
        count_in = 0
        for key, value in plot_dic.items():
            count_in += 1
            random_plot += plot_format.format(count_in, value[1])
        random_plot += "};"
        # print "\nRANDOM LIST OF CLUSTERS FOR PLOT\n\t{}".format(random_plot)

        #################
        # SORTED
        #################
        sorted_plot_dic = sorted(plot_dic.items(), key=lambda val: val[1][1], reverse=True)
        human_plot_1 = "\\addplot [color=red] coordinates {"
        human_plot = ""
        sored_plot = "\\addplot [color=blue] coordinates {"
        scatter = "\t\\addplot [color=red, only marks, mark=*, mark size=0.5pt] coordinates {"
        count_in = 0
        for item in sorted_plot_dic:
            count_in += 1
            machine_rank = item[1][1]
            sored_plot += plot_format.format(count_in, machine_rank)
            # print plot_dict
            if plot_dict is not None:
                if item[0] in plot_dict:
                    human_rank = plot_dict[item[0]]
                    human_plot_1 += plot_format.format(count_in, human_rank)
                    # print type(machine_rank), type(human_rank)
                    if int(machine_rank) != human_rank:
                        scatter += plot_format.format(count_in, human_rank)
                        human_plot += "\t\\addplot [black, dashed, dash pattern=on 1pt off 1pt, ->] " \
                                      "coordinates {{ ({0},{1}) ({0},{2}) }};\n".\
                            format(count_in, machine_rank, human_rank)
                else:
                    builder.write("{} {}".format(item[0], "???"))

        sored_plot += "};"
        human_plot_1 += "};"
        scatter += "};"
        # print "\nORDERED LIST OF CLUSTERS FOR PLOT\n\t{}".format(sored_plot)

        # print "\nORDERED HUMAN LIST OF CLUSTERS FOR PLOT\n{} \n{}".format(scatter, human_plot)=

        comment = "\nDifference between FILE-1 and FILE-2 but looking into FILE-2.\n\t{}\n\t{}".format(file_1, file_2)
        builder.write(comment)


        if save_in is not None and len(save_in.strip()) > 0:

            diff_path = "{}\Diff_{}_Found_{}.text".format(
                save_in, Ut.hash_it(comment), len(diff))

            if isdir(save_in) is False:
                os.makedirs(save_in)

            with open(diff_path, "wb") as new_file:
                new_file.write(builder.getvalue())

            print builder.getvalue()
            print "file created at: {}".format(diff_path)
            return diff_path


def track(directory, resource, activated=False):

    if activated is False:
        return None

    print "\nMAIN DIRECTORY {}".format(directory)
    # LOOK FOR MAIN FOLDERS IN MAIN DIRECTORY
    main_folders = [f for f in listdir(nrm(directory)) if isdir(join(nrm(directory), f))]

    # GO THROUGH EACH MAIN FOLDER
    for main_folder in main_folders:
        main_path = join(directory, main_folder)
        # print "\tMAIN-FOLDER: {}".format(main_folder)
        # FOREACH MAIN FOLDER GAT THE SUB-FOLDER
        sub_folders = [f for f in listdir(nrm(main_path)) if isdir(join(nrm(main_path), f))]

        for sub_folder in sub_folders:
            sub_path = join(main_path, sub_folder)
            # print "\t\tSUB-FOLDER: {}".format(sub_folder)

            # TARGET FOLDERS
            target_folder = [f for f in listdir(nrm(sub_path)) if isdir(join(nrm(sub_path), f))]

            for target in target_folder:
                i_folder = "{}".format(join(main_path, sub_path, target))
                # print "\t\t\tTARGET-FOLDER: {}".format(target)
                i_file = [f for f in listdir(nrm(i_folder)) if isfile(join(nrm(i_folder), f))]

                for target_file in i_file:
                    if target_file.lower().endswith(".txt"):
                        target_path = join(main_path, sub_path, target, target_file)
                        wr = codecs.open(target_path, "rb")
                        text = wr.read()
                        wr.close()

                        result = text.__contains__(resource)

                        if result is True:
                            print "\n\tMAIN-FOLDER: {}".format(main_folder)
                            print "\t\tSUB-FOLDER: {}".format(sub_folder)
                            print "\t\t\tTARGET-FOLDER: {}".format(target)
                            print "\t\t\t\tTARGET FILE: {}".format(target_file)
                            target = join(main_path, sub_path, target)
                            print "\tPATH: {}".format(target)

                            pdf = [f for f in listdir(nrm(target)) if join(nrm(target), f).endswith('.pdf')]
                            # txt = [f for f in listdir(nrm(target)) if join(nrm(target), f).endswith('.txt')]
                            trg_path = join(nrm(target), pdf[0])
                            # txt_path = join(nrm(target), txt[0])
                            system(trg_path)
                            # system(txt_path)
                            # print "\t\t\t\t{}".format(result)


def investigate(target_directory, track_directory=None, activated=False):

    if activated is False:
        return None

    folders = [f for f in listdir(nrm(target_directory)) if isdir(join(nrm(target_directory), f))]
    print "\nINVESTIGATING NO: {}".format(len(folders))
    count = 0
    for item in folders:
        count += 1
        print "\t>>> {}".format(item)
        target = join(nrm(target_directory), item)
        doc = [f for f in listdir(nrm(target)) if join(nrm(target), f).endswith('.txt')]
        pdf = [f for f in listdir(nrm(target)) if join(nrm(target), f).endswith('.pdf')]

        if doc and pdf:
            doc_path = join(nrm(target), doc[0])

            read = open(doc_path)
            node = ""
            for i in range(0, 6):
                node = read.readline().strip()

            if track_directory and path.isdir(track_directory):
                print "\t{}-TRACKING {}".format(count, node)
                track(directory=track_directory, resource=node, activated=activated)
                # system(doc_path)
            elif pdf:
                pdf_path = join(nrm(target), pdf[0])
                system(pdf_path)
                # system(doc_path)

            next_step = raw_input("\tCONTINUE?\t")
            print ""
            if next_step.lower() == "yes" or next_step.lower() == "y" or next_step.lower() == "1":
                continue
            else:
                exit(0)


def generate_eval_sheet(alignment, network_size, greater_equal=True, targets=None):
    # RUN THE CLUSTER
    count = 0
    # tabs = "\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t"
    a_builder = Buffer.StringIO()
    a_builder.write("Count	ID					STRUCTURE	E-STRUCTURE-SIZE	NETWORK QUALITY		REFERENCE\n")
    clusters_0 = Cls.links_clustering(alignment, None)
    for i_cluster in clusters_0.items():
        children = i_cluster[1][St.children]
        check = len(children) >= network_size if greater_equal else len(children) == network_size
        # first = False
        if check:
            count += 1

            # 2: FETCHING THE CORRESPONDENTS
            smallest_hash = float('inf')
            for child in children:
                hashed = hash(child)
                if hashed <= smallest_hash:
                    smallest_hash = hashed
            test(targets, count, smallest_hash, a_builder, alignment, children)

    print a_builder.getvalue()


def test(targets, count, smallest_hash, a_builder, alignment, children):
    first = False
    a_builder.write("\n{:<5}\t{:<20}{:12}{:20}{:20}".format(count, smallest_hash, "", "", ""))
    if targets is None:
        a_builder.write(Cls.disambiguate_network(alignment, children))
    else:
        response = Cls.disambiguate_network_2(children, targets, output=False)
        if response:
            temp = ""
            dataset = ""
            # for line in response:
            #     print line

            for i in range(1, len(response)):
                if i == 1:
                    temp = response[i][1]

                elif dataset == response[i][0]:
                    temp = "{} | {}".format(temp, response[i][1])

                else:
                    if first is False:
                        a_builder.write("{}\n".format(temp))
                    else:
                        a_builder.write("{:80}{}\n".format("", temp))
                    first = True
                    temp = response[i][1]

                dataset = response[i][0]
            a_builder.write("{:80}{}\n".format("", temp))


def good_bad_count_stats(file_path, human_bad=False, human_good=False, human_acceptable=False, human_uncertain=False,
                         machine_bad=False, machine_good=False, machine_acceptable=False, machine_uncertain=False,
                         latex=False, activated=False):

    if activated is False:
        print "\nTHE FUNCTION [good_bad_count_stats] IS NOT ACTIVATED"
        return None

    # print "\nEVALUATION SHEET SUMMARY"

    machine_bad_str = "  bad ["
    machine_good_str = "  good ["
    machine_acceptable_str = " acceptable ["
    machine_uncertain_str = " uncertain ["

    human_bad_str = "-bad-"
    human_good_str = "-good-"
    human_acceptable_str = "-acceptable-"
    human_uncertain_str = "-uncertain-"

    count_human_bad = 0
    count_human_good = 0
    count_human_acceptable = 0
    count_human_uncertain = 0

    count_machine_bad = 0
    count_machine_good = 0
    count_machine_acceptable = 0
    count_machine_uncertain = 0

    plot_dic = dict()
    pattern = '\d+_[n, p]\d*'

    # files = [f for f in listdir(nrm(file_path)) if join(nrm(file_path), f).endswith('.txt')]
    # print file_path
    # if len(files) > 0:

    # with open(join(file_path, files[0]), "r") as lines:
    if os.path.isfile(file_path):

        with open(file_path, "r") as lines:

            print "\nEVALUATION SHEET SUMMARY FOR: {}".format(os.path.basename(file_path))
            f_measure = 0
            true_positive = 0
            false_positive = 0
            false_negative = 0
            true_negative = 0

            for line in lines:

                original = line
                line = line.strip().lower()

                # HUMAN
                if human_bad or human_good or human_acceptable or human_uncertain or \
                        machine_bad or machine_good or machine_acceptable or machine_uncertain:

                    if line.__contains__("Count	ID".lower()):
                        print "\t{}".format(line)

                if line.__contains__(human_good_str):
                    count_human_good += 1
                    identifier = re.findall(pattern, original, re.I)
                    if identifier:
                        plot_dic[identifier[0]] = 4

                    if human_good:
                        print "\t{}".format(line)

                if line.__contains__(human_bad_str):
                    count_human_bad += 1
                    identifier = re.findall(pattern, original, re.I)
                    plot_dic[identifier[0]] = 1

                    if human_bad:
                        print "\t{}".format(line)

                if line.__contains__(human_acceptable_str):
                    count_human_acceptable += 1
                    identifier = re.findall(pattern, original, re.I)
                    plot_dic[identifier[0]] = 3

                    if human_acceptable:
                        print "\t{}".format(line)

                if line.__contains__(human_uncertain_str):
                    count_human_uncertain += 1
                    identifier = re.findall(pattern, original, re.I)
                    plot_dic[identifier[0]] = 2

                    if human_uncertain:
                        print "\t{}".format(line)

                # MACHINE
                if line.__contains__(machine_good_str):
                    count_machine_good += 1

                    if line.__contains__(human_good_str):
                        true_positive += 1
                    else:
                        false_positive += 1

                    if machine_good:
                        print "\t{}".format(line)

                if line.__contains__(machine_bad_str):
                    count_machine_bad += 1
                    if machine_bad:
                        print "\t{}".format(line)

                    if line.__contains__(human_good_str):
                        false_negative += 1
                    else:
                        true_negative += 1

                if line.__contains__(machine_acceptable_str):
                    count_machine_acceptable += 1
                    if machine_acceptable:
                        print "\t{}".format(line)

                    if line.__contains__(human_good_str):
                        false_negative += 1
                    else:
                        true_negative += 1

                if line.__contains__(machine_uncertain_str):
                    count_machine_uncertain += 1
                    if machine_uncertain:
                        print "\t{}".format(line)

                    if line.__contains__(human_good_str):
                        false_negative += 1
                    else:
                        true_negative += 1

                # if count_machine_good == 50:
                #     break

        print "\nMACHINE {0:>12}{1:>6}\tHUMAN {0:>12} {2:>6}" \
              "\tTRUE POSITIVE  {3:6}\tFALSE POSITIVE {4:6}".\
            format("GOOD", count_machine_good, count_human_good, true_positive, false_positive)

        if count_human_good > 0 and count_human_good >= true_positive:

            precision = true_positive/float(count_machine_good)
            recall = true_positive/float(count_human_good)
            f_measure = round(2 * (precision * recall)/(precision + recall), 3)
            print "MACHINE {0:>12}{1:>6}\tHUMAN {0:>12} {2:>6}" \
                  "\tPRECISION      {3:6}\tRECALL         {4:6}".\
                format("BAD", count_machine_bad, count_human_bad, round(precision, 3), round(recall, 3))

        else:
            print "MACHINE {0:>12}{1:>6}\tHUMAN {0:>12} {2:>6}" \
                  "\tPRECISION      {3:6}\tRECALL         {4:6}". \
                format("BAD", count_machine_bad, count_human_bad, "     -", "     -")

        print "MACHINE {0:>12}{1:>6}\tHUMAN {0:>12} {2:>6}" \
              "\tFALSE NEGATIVE {3:6}\tTRUE NEGATIVE  {4:6}".\
            format("ACCEPTABLE", count_machine_acceptable, count_human_acceptable, false_negative, true_negative)

        print "MACHINE {0:>12}{1:>6}\tHUMAN {0:>12} {2:>6}\tF MEASURE      {3:6}".\
            format("UNCERTAIN", count_machine_uncertain, count_human_uncertain, f_measure)

        machine_total = count_machine_good + count_machine_bad + count_machine_acceptable + count_machine_uncertain
        print "TOTAL   {0:>18}\tTOTAL  {1:>18}\n".\
            format(machine_total, count_human_good + count_human_bad + count_human_acceptable + count_human_uncertain)

        confusion_matrix(true_p=true_positive, false_p=false_positive, true_n=true_negative, false_n=false_negative,
                         ground_truth_p=count_human_good, observations=machine_total, latex=latex)

        return plot_dic

    else:
        print "\nFILE [{}]  DOES NOT EXIST\n".format(os.path.basename(file_path))
        return plot_dic


# and the mosque project?
def metric(nodes, observed, bridge, diameter):
    bs = round(sigmoid(bridge), 2)
    ds = round(sigmoid(diameter - 1), 2)
    norm_b = bridge/float(nodes - 1)
    norm_d = round((diameter - 1)/float(nodes - 2), 2)
    max_c = float(nodes * (nodes - 1)/2)
    nb = round(max(norm_b, bs), 2)
    nd = round(max(norm_d, ds), 2)
    nc = round(1 - observed/max_c, 2)
    impact = round((nb + nc + nd)/3, 2)
    eq = 1 - impact

    print "BRIDGE \t\t[{}]\t[{}]\nCLOSURE \t[{}]\t[{}]\t[{}]" \
          "\nDIAMETER \t[{}]\t[{}]\nIMPACT\t\t\t\t[{}]\nQuality \t[{}]\t[{}]\n".\
        format(norm_b, bs, max_c, 1 - nc, nc, norm_d, ds, impact, eq, eq)


def network_examples():
    print "1. RING"
    nodes = 6
    observed = 6
    bridge = 0
    diameter = 3
    metric(nodes, observed, bridge, diameter)
    # BRIDGE 		[0.0]	[0.0]
    # CLOSURE 	[0.6]	[15.0]
    # DIAMETER 	[0.5]	[0.56]
    # Quality 	[0.39]	[0.39]

    print "2. MESH WITH A BRIDGE"
    nodes = 6
    observed = 7
    bridge = 1
    diameter = 3
    metric(nodes, observed, bridge, diameter)
    # BRIDGE 		[0.2]	[0.38]
    # CLOSURE 	[0.53]	[15.0]
    # DIAMETER 	[0.5]	[0.56]
    # Quality 	[0.49]	[0.49]

    print "3. STAR"
    nodes = 6
    observed = 5
    bridge = 5
    diameter = 2
    metric(nodes, observed, bridge, diameter)
    # BRIDGE 		[1.0]	[0.76]
    # CLOSURE 	[0.67]	[15.0]
    # DIAMETER 	[0.25]	[0.38]
    # Quality 	[0.68]	[0.68]

    print "4. FULL MESH"
    nodes = 6
    observed = 15
    bridge = 0
    diameter = 1
    metric(nodes, observed, bridge, diameter)
    # BRIDGE 		[0.0]	[0.0]
    # CLOSURE 	[0.0]	[15.0]
    # DIAMETER 	[0.0]	[0.0]
    # Quality 	[0.0]	[0.0]

    print "5 LINE"
    nodes = 6
    observed = 5
    bridge = 5
    diameter = 5
    metric(nodes, observed, bridge, diameter)
    # BRIDGE 		[1.0]	[0.76]
    # CLOSURE 	[0.67]	[15.0]
    # DIAMETER 	[0.75]	[0.65]
    # Quality 	[0.81]	[0.81]

    print "6 TREE"
    nodes = 6
    observed = 5
    bridge = 5
    diameter = 4
    metric(nodes, observed, bridge, diameter)
    # BRIDGE 		[1.0]	[0.76]
    # CLOSURE 	[0.67]	[15.0]
    # DIAMETER 	[0.75]	[0.65]
    # Quality 	[0.81]	[0.81]

    print "7 OTHER"
    nodes = 5
    observed = 4
    bridge = 4
    diameter = 2
    metric(nodes, observed, bridge, diameter)


def confusion_matrix(true_p=0, false_p=0, true_n=0, false_n=0,
                     ground_truth_p=0, observations=0, latex=False, zero_rule=True):

    if zero_rule is True:
        if ground_truth_p > observations - ground_truth_p:
            confusion_matrix(true_p=ground_truth_p, false_p=observations - ground_truth_p, true_n=0, false_n=0,
                             ground_truth_p=ground_truth_p, observations=observations, latex=latex, zero_rule=False)
        else:

            confusion_matrix(true_p=0, false_p=0, true_n=observations - ground_truth_p, false_n=ground_truth_p,
                             ground_truth_p=ground_truth_p, observations=observations, latex=latex, zero_rule=False)

    # confusion_matrix(true_p=231, false_p=58, ground_truth_p=272, false_n=41, true_n=61, observations=391)

    # PREDICT
    confusion = Buffer.StringIO()

    recall = "-"
    precision = "-"
    ground_truth_n = "-"
    fall_out = "-"
    omission = "-"
    f_disc_rate = "-"
    n_pred_value = "-"
    likelihood_ratio = "-"
    f_1 = "-"

    positives = true_p + false_p
    negatives = false_n + true_n

    if positives > 0:
        recall = true_p / float(positives)
        f_disc_rate = round(false_p / float(positives), 3)

    if negatives > 0:
        omission = round(false_n / float(negatives), 3)
        n_pred_value = round(true_n / float(negatives), 3)

    if ground_truth_p > 0:
        precision = true_p / float(ground_truth_p)

    if observations >= ground_truth_p:
        ground_truth_n = observations - ground_truth_p
        if ground_truth_n > 0:
            fall_out = round(false_p / float(ground_truth_n), 3)

    if fall_out != "-" and fall_out > 0:
        likelihood_ratio = round(recall/fall_out, 3)

    if precision != "-" and recall != "-" and recall * precision > 0:
        f_1 = round(2 * (precision * recall)/(recall + precision), 3)

    long_line = "{:->105}\n".format("")
    short_line = "{:19}{:->35}\n".format("", "")
    end_line = "{:19}{:->86}\n".format("", "")
    short_line_base = "{:^19}{:->35}\n".format("*** BASE LINE ***", "")

    base = "\\tiny *** BASE" if zero_rule is False else ""
    base_line = "\\tiny LINE ***" if zero_rule is False else ""

    # LINE 1
    confusion.write(short_line)
    confusion.write("{:>19}|{:^32} |\n".format("", "{} GROUND TRUTHS".format(observations)))

    # LINE 2
    confusion.write(short_line_base) if zero_rule is False else confusion.write(short_line)
    confusion.write("{:19}| {:^14} | {:^14} |\n".format("", "GT Positive", "GT Negative"))
    confusion.write("{:19}| {:^14} | {:^14} |\n".format("", ground_truth_p, ground_truth_n))

    # LINE 3
    confusion.write(long_line)
    confusion.write("{:8}| Positive | {:^14} | {:^14} | {:^19} | {:^25} |\n".format(
        "", "True Positive", "False Positive", "Precision", "False discovery rate (FDR)"))

    if recall != "-":
        confusion.write("{:8}| {:^8} | {:^14} | {:^14} | {:^19} | {:^26} |\n".format(
            "", positives, true_p, false_p, round(recall, 3), f_disc_rate))
    else:
        confusion.write("{:8}| {:^8} | {:^14} | {:^14} | {:^19} | {:^26} |\n".format(
            "", positives, true_p, false_p, "-", f_disc_rate))

    # LINE 4
    confusion.write("{:7} {:->97}\n".format("PREDICT", ""))
    confusion.write("{:8}| Negative | {:^14} | {:^14} | {:^19} | {:^25} |\n".format(
        "", "False Negative", "True Negative", "False omission rate", "Negative predictive value "))
    confusion.write("{:8}| {:^8} | {:^14} | {:^14} | {:^19} | {:^26} |\n".format(
        "", negatives, false_n, true_n, omission, n_pred_value))

    # LINE 5
    confusion.write(long_line)
    confusion.write("{:8}           | {:^14} | {:^14} |{:^20} | {:^13}{:^13} |\n".format(
        "", "Recall", "Fall-out", " P. Likelihood Ratio", "F1 score", "Accuracy"))

    accuracy = round((true_p + true_n) / float(observations), 3)

    if precision != "-":
        confusion.write("{:8}           | {:^14} | {:^14} |{:^20} | {:^13}{:^13} |\n".format(
            "", round(precision, 3), fall_out, likelihood_ratio, f_1, accuracy))
    else:
        confusion.write("{:8}           | {:^14} | {:^14} |{:^20} | {:^13} {:^13}|\n".format(
            "", precision, fall_out, likelihood_ratio, f_1, accuracy))

    # LINE 6
    confusion.write(end_line)

    if zero_rule is True:
        confusion.write("Precision                  PPV   = Positive Predicted Value  = TP / (TP + FP)\n")
        confusion.write("Recall                     TPR   = True Positive Rate        = TP / GT\n")
        confusion.write("False discovery rate       FDR   = Σ False positive / Σ Predicted condition positive\n")
        confusion.write("Negative predictive value  NPV   = Σ True negative / Σ Predicted condition negative\n")
        confusion.write("False omission rate        FOR   = Σ False negative / Σ Predicted condition negative\n")
        confusion.write("Positive likelihood ratio  LR+   = TPR / FPR\n")
        confusion.write("False positive rate        FPR   = Σ False positive / Σ Condition negative\n")
        confusion.write("FPR a.k.a Fall-out, probability of false alarm")

    latex_cmd = """
\\newcolumntype{{s}}{{>{{\columncolor[HTML]{{AAACED}}}} p{{3cm}}}}
\\renewcommand{{\\arraystretch}}{{1.2}}
\\begin{{table}}[h!]
    \\vspace{{-0.5cm}}
    \centering
    {{\scriptsize
    \\begin{{tabular}}{{
    >{{\centering\\arraybackslash}}p{{0.5cm}}
    >{{\centering\\arraybackslash}}p{{1.5cm}} |
    >{{\centering\\arraybackslash}}p{{1.6cm}} |
    >{{\centering\\arraybackslash}}p{{1.6cm}} |
    >{{\centering\\arraybackslash}}p{{2.2cm}}
    >{{\centering\\arraybackslash}}p{{2.3cm}} }} \cline{{3-4}}
     % RAW 1 ************************************
     \cline{{3-4}}
    &
    & \multicolumn{{2}}{{ c| }}{{\cellcolor{{gray!10}} \\tiny {0} GROUND TRUTHS}}
    &
    & \\\\
    % RAW 2 ************************************
    \cline{{3-4}} \cline{{3-4}}
    \cline{{3-4}}
    & {18}
    & GT. Pos.
    & GT. neg.
    &
    & \\\\
    % RAW 3 ************************************
    & {19}
    & {1}
    & {2}
    &
    & \\\\
    % RAW 4 ************************************
    \cline{{1-6}}
     \multicolumn{{1}}{{ |c| }}{{\cellcolor{{gray!10}}}}
    &  \\tiny POSITIVE
    & True Pos.
    & False Pos.
    & {{\cellcolor{{green!10}} Precision}}
    & \multicolumn{{1}}{{ |c| }}{{False Discovery Rate}} \\\\
    % RAW 5 ************************************
    \multicolumn{{1}}{{ |c| }}{{\cellcolor{{gray!10}}}}
    & {15}
    & {3}
    & {4}
    & {{\cellcolor{{green!10}} {5}}}
    & \multicolumn{{1}}{{ |c| }}{{{6}}} \\\\
    % RAW 6 ************************************
     \cline{{2-6}}\multicolumn{{1}}{{ |c| }}{{\cellcolor{{gray!10}}}}
    & \\tiny NEGATIVE
    & False Neg.
    & True Neg.
    & F. Omission Rate
    & \multicolumn{{1}}{{ |c| }}{{Neg. Predictive Value}} \\\\
     % RAW 7 ************************************
    \multicolumn{{1}}{{ |c| }}{{\multirow{{-4}}{{*}}{{\\rotatebox[origin=c]{{90}}
    {{\cellcolor{{gray!10}} \\tiny  \\textbf{{PREDICT}}}}}}}}
    & {16}
    & {7}
    & {8}
    & {9}
    & \multicolumn{{1}}{{ |c| }}{{{10}}} \\\\
    % RAW 8 ************************************
    \cline{{1-6}}\multicolumn{{1}}{{  c  }}{{       }}
    &
    & {{ \cellcolor{{green!10}} Recall}}
    & Fall-out
    & Positive L. Ratio
    & \multicolumn{{1}}{{ |c| }}{{\cellcolor{{green!10}} F1 score | Accuracy}} \\\\
    % RAW 9 ************************************
    \multicolumn{{1}}{{  c  }}{{       }}
    &
    & {{ \cellcolor{{green!10}} {11}  }}
    & {12}
    & {13}
    & \multicolumn{{1}}{{ |c| }}{{\cellcolor{{green!10}} {14} | {17}}}  \\\\
    \cline{{3-6}}
    \end{{tabular}}
    \\vspace{{5pt}}
    \caption{{Confusion matrix for link-networks of size 8.}}
    \label{{table_confusion_matrix}}
    }}
    \\vspace{{-1cm}}
\end{{table}}
    """.format(observations, ground_truth_p, ground_truth_n, true_p, false_p,
               round(recall, 3) if recall != "-" else "-", f_disc_rate,
               false_n, true_n, omission, n_pred_value, round(precision, 3),
               fall_out, likelihood_ratio, f_1, positives, negatives, accuracy, base, base_line)

    print confusion.getvalue()

    if latex is True:
        print latex_cmd


def generate_bat_for_RQ(directory):

    files = ""
    # folder = "C:\Users\Al\Dropbox\@VU\Ve\TestRQ"
    if path.isdir(directory):
        files = [f for f in listdir(nrm(directory)) if isfile(join(nrm(directory), f))]
        for i in range(0, len(files)):

            if files[i].endswith(".trig") or files[i].endswith(".sparql"):
                print """echo Loading data {:6}: {}""".format(i, files[i])

            if files[i].endswith(".trig"):
                print """\tcall stardog data add risis "{}" """.format(join(nrm(directory), files[i]))

            if files[i].endswith(".sparql"):
                print """\tcall stardog query risis "{}" """.format(join(nrm(directory), files[i]))

#
# pattern = """BIND\( IRI\("(<.*>)"\) AS (\?LINK_[\d]+)"""
# """>[^<>]*\/.*<"""
# import Alignments.Utility as Ut
#
# def convert(bind_text, insert_text):
#
#     regex_result = re.findall("""BIND\( IRI\("(<.*>)"\) AS (\?LINK_[\d]+)""", bind_text)
#
#     url_2_new_id = dict()
#     id_2_uri = dict()
#     for url, id in regex_result:
#         # print url, id
#         id_2_uri[id] = url
#         if url not in url_2_new_id:
#             url_2_new_id[url] = id
#         else:
#             url_2_new_id[url] += " {}".format(id)
#
#     # BIND WITH NEW ID
#     new_bind = Buffer.StringIO()
#     for url, id in url_2_new_id.items():
#         new_bind.write("BIND( IRI(\"{}\") AS ?LINK_{} )\n".format(url, Ut.hash_it(id)))
#
#     print new_bind.getvalue(), "\n\n"
#
#     temp = insert_text
#     for id, url in id_2_uri.items():
#         new_id = url_2_new_id[url]
#         new_id = "?LINK_{}".format(Ut.hash_it(new_id))
#         temp = temp.replace(id, new_id)
#         # print id, url, "?LINK_{}".format(Ut.hash_it(new_id))
#
#     print temp
#
#
# # convert(input, test)

# generate bat

# generate_bat_for_RQ("C:\Users\Al\Dropbox\@VU\Ve\Geo-RQ\idea_1e6448")
# generate_bat_for_RQ("C:\Users\Al\Dropbox\@VU\Ve\TestRQ")
# generate_bat_for_RQ("C:\Users\Al\Dropbox\@VU\Ve\RQ4D2SServer")
# generate_bat_for_RQ("C:\Users\Al\Dropbox\@VU\Ve\TestRQ3")
# generate_bat_for_RQ("C:\Users\Al\Documents\Tobias\\nano")


# confusion_matrix(true_p=29, false_p=0, true_n=0, false_n=0, ground_truth_p=27, observations=29)

# -UNION REF 2000M AFTER-
#                  -REF2000MAfter-
# codecs.open(ipath, "wb", "utf-8")
# -REF500MdeduplicateAfter-


# -DEDUPLICATE2000MBefore-

# -DEDUPLICATE2000MAfter-


def get_cluster_id(file_path):

    if file_path is not None and isfile(file_path) is True:
        new_file = open(file_path, "rb")
        read = new_file.read()
        new_file.close()
        return re.findall(" (\d_.\d+)", read)
    return []


def extract_cluster_stats(ids_file, file_path_to_extract, save_in="", temporal="before"):

    # EXTRACT STATS BASED ON CLUSTER IDS
    print "\n{:17} : {}".format("IDs FILE", ids_file)
    print "{:17} : {}".format("EXTRACTION FILE", file_path_to_extract)
    # read = ""
    pattern = "\d_.\d+"
    ids = get_cluster_id(ids_file)
    # print ids
    print "{:17} : {}".format("cluster IDs found", len(ids))
    builder = Buffer.StringIO()
    if isfile(file_path_to_extract) is True:
        with open(file_path_to_extract, "rb") as new_file:
            builder.write("{}".format(new_file.readline()))
            for line in new_file:
                find = re.findall(pattern, line)
                if len(find) == 1 and find[0] in ids:
                    builder.write("{}\n".format(line.strip('\n')))
                    for lines in new_file:
                        builder.write("{}\n".format(lines.strip('\n')))
                        if len(lines.strip()) == 0:
                            break
        new_file.close()
    else:
        print "THE FILE DOES NOT EXISTS: {}".format(file_path_to_extract)

    # print builder.getvalue()
    basename = path.basename(file_path_to_extract).replace(
        "ClusterSheet", "ClusterSheet_netherlands_{}".format(temporal))
    file_path = "{}\\{}".format(save_in, basename)

    if isdir(save_in) is False:
        os.makedirs(save_in)

    with open(file_path, "wb") as new_file:
        new_file.write(builder.getvalue())

