# -*- coding: utf-8 -*-
# coding=utf-8
import rdflib
import logging
import os
import cStringIO
from os import listdir
from os.path import isfile, isdir, join
import datetime

logging.basicConfig()
_format = "%a %b %d %H:%M:%S %Y"


def check_rdf_file(file_path):

    try:

        if not os.path.exists(file_path):
            print "\n\t[Error] The path [{}] does not exist.".format(file_path)
            return

        rdf_file = os.path.basename(file_path)
        extension = os.path.splitext(rdf_file)[1]
        extension = extension.replace(".", "")
        print ""

        graph_format = extension
        if graph_format == 'ttl':
            graph_format = "turtle"
        """
            Check the currently closed RDF file
        """
        print "=======================================================" \
              "======================================================="
        print "    Syntactic check of: ", rdf_file
        print "=======================================================" \
              "======================================================="

        g = rdflib.Dataset()
        print '    Loading ', rdf_file
        # print "    It's a .{} file".format(extension)
        g.load(source=file_path, format=graph_format)
        print "    It's a valid.{} file with a RDF graph of length: {}".format(extension, str(len(g)))

    except Exception as err:
        print "\t[check_rdf_file in checkRDFFile]", err


def check_rdf_in_dir(dir_path):

    builder = cStringIO.StringIO()
    files = [f for f in listdir(dir_path) if isfile(join(dir_path, f))]

    print "{:>104}\n".format(datetime.datetime.today().strftime(_format))
    builder.write("\n--------------------------------------------------------"
                  "----------------------------------------------------------\n")
    builder.write("    Syntactic check of RDF files in:\n\t\t{}\n".format(dir_path))
    builder.write("    \tThe folder contains [ {} ] files.\n".format(len(files)))
    builder.write("--------------------------------------------------------"
                  "----------------------------------------------------------\n")

    count = 1
    for f in listdir(dir_path):
        path = join(dir_path, f)

        if isfile(path):
            # check_rdf_file(path)
            # Extension
            rdf_file = os.path.basename(path)
            extension = os.path.splitext(rdf_file)[1]
            extension = extension.replace(".", "")

            # change ttl extension format
            graph_format = extension
            if graph_format == 'ttl':
                graph_format = "turtle"
            # print "2"
            # Load the file
            try:
                g = rdflib.Dataset()
                g.load(source=path, format=graph_format)
                report = "    [{:*>5}]\t{} is a valid .{} file with a RDF graph of length: {}".\
                    format(count, rdf_file, extension, str(len(g)))
                builder.write("{}\n".format(report))
                print report
            except Exception as err:
                builder.write("    {} is not a valid .{} file \n".format(rdf_file, extension))
        count += 1
    return builder.getvalue()


def check_converted_folder(converted_folder):

    stats_path = "{}\\RDF-FileCheckedReport.txt".format(converted_folder)
    stats_path = stats_path.replace("\\", "/")

    print stats_path
    writer = open(stats_path, "wb")
    print "\n\t The report on RDF file check can be found at:\n\t\t{}".format(stats_path)
    for path in listdir(converted_folder):
        full = join(converted_folder, path)
        if isdir(full) is True:
            report = check_rdf_in_dir(full)
            writer.write(report)
    writer.close()

# check_converted_folder("D:\datasets\EUPRO\converted\eupro 2016-10-28")

# check_rdf_in_dir("D:\datasets\EUPRO\converted\eupro 2016-10-28\Country")

# date = "2016-10-22"
# dataset = "LeidenRanking"
# for i in range(1, 8):
#     main = "D:\datasets\Linksets\GeneratedIn_{}\{}\{}.JRC.ambiguous.ls.{}.{}.trig".\
#         format(date, dataset, dataset, i, date)
#     check_rdf_file(main)
#
# for i in range(1, 8):
#     main = "D:\datasets\Linksets\GeneratedIn_{}\{}\{}.JRC.disambiguated.ls.{}.{}.trig".\
#         format(date, dataset, dataset, i, date)
#     check_rdf_file(main)


# check_rdf_file("C:\Users\Al\PycharmProjects\AlignmentUI\src\Alignments\Data\Linkset\Exact\en_nl_intermediate_author_label_P1605654795(Metadata)-20170702.trig")
