# -*- coding: utf-8 -*-
# coding=utf-8

import re
import os
import sys
import time
import rdflib
import codecs
import datetime
import platform
import cStringIO
import xmltodict
import requests
import subprocess

import zipfile as Zip
from os import listdir
import os.path as path
import cStringIO as Buffer
import Alignments.NameSpace as Ns
import Alignments.Query as Qry
import Alignments.Settings as St
import Alignments.Server_Settings as Svr
from os.path import isfile, join
from unidecode import unidecode
from kitchen.text.converters import to_bytes, to_unicode
# write_to_path = "C:\Users\Al\Dropbox\Linksets\ExactName"


OPE_SYS = platform.system().lower()
mac_weird_name = "darwin"


#################################################################
"""
    GENERIC FUNCTIONS
"""
#################################################################



def zip_dir(path, zip_name):

    zip_f = Zip.ZipFile(zip_name, 'w', Zip.ZIP_DEFLATED)
    for root, dirs, files in os.walk(path):
        for file in files:
            zip_f.write(os.path.join(root, file))


def hash_it(text):

    code = hash(str(text))
    hashed = str(code).replace("-", "N") if str(code).__contains__("-") else "P{}".format(code)
    # print hashed
    return hashed


def from_alignment2singleton(alignment):

    if str(alignment).__contains__(Ns.linkset):
        return str(alignment).replace(Ns.linkset, Ns.singletons)
    elif str(alignment).__contains__(Ns.lens):
        return str(alignment).replace(Ns.lens, Ns.singletons)
    else:
        return alignment


def is_nt_format(resource):
    try:
        temp = str(to_bytes(resource)).strip()
        return temp.startswith("<") and temp.endswith(">")

    except Exception as err:
        print "Exception:", err
        return False


def to_nt_format(resource):

    try:
        if is_nt_format(resource) is True:
            return resource
        else:
            return "<{}>".format(resource)

    except Exception as err:
        print "Exception:", err
        return resource


def is_property_path(resource):

    temp = str(to_bytes(resource)).strip()
    check = re.findall("> */ *<", temp)
    return len(check) != 0


def get_uri_local_name(uri, sep="_"):

    # print "URI: {}".format(uri)
    # print type(uri)

    if uri is None:
        return None

    if len(uri) == 0:
        return None

    # if type(uri) is not str:
    #     return None

    check = re.findall("<([^<>]*)>/*", uri)

    if is_property_path(uri) or is_nt_format(uri) or len(check) > 0:

        name = ""
        # pro_list = re.findall("<([^<>]*)>/*", uri)
        pro_list = check

        for i in range(len(pro_list)):
            local = get_uri_local_name(pro_list[i])
            if i == 0:
                name = local
            else:
                name = "{}{}{}".format(name, sep, local)
                # print ">>>> name: ", name
        return name

    else:
        non_alphanumeric_str = re.sub('[ \w\.-]', '', uri)
        if non_alphanumeric_str == "":
            return uri
        else:
            last_char = non_alphanumeric_str[-1]
            index = uri.rindex(last_char)
            name = uri[index + 1:]
            return name


def get_uri_local_name_plus(uri, sep="_"):

    # print "URI: {}".format(uri)
    # print type(uri)

    if uri is None:
        return None

    if len(uri) == 0:
        return None

    # if type(uri) is not str:
    #     return None

    check = re.findall("<([^<>]*)>/*", uri)

    if is_property_path(uri) or is_nt_format(uri) or len(check) > 0:

        name = ""
        pro_list = check

        for i in range(len(pro_list)):
            local = get_uri_local_name_plus(pro_list[i])
            if i == 0:
                name = local
            else:
                name = "{}{}{}".format(name, sep, local)
                # print ">>>> name: ", name
        return name

    else:
        local = re.findall(".*[\/\#](.*)$", uri)
        if len(local) > 0 and len(local[0]) > 0 :
            return local[0]
        else:
            return uri


def split_property_path(property_path):

    # example = """(" <http://www.grid.ac/ontology/hasAddress>  / <http://www.grid.ac/ontology/countryCode>")"""
    if property_path is None:
        return []
    return re.findall("<([^<>]*)>/*", property_path)


def pipe_split(text, sep="_"):

    # print pipe_split("[rembrandt van rijn] aligns with [rembrandt van rijn]")

    altered = ""
    split = str(to_bytes(text)).split("|")

    for i in range(len(split)):
        item = split[i].strip()
        item = get_uri_local_name(item, sep)
        if i == 0:
            altered = item
        else:
            altered += " | {}".format(item)

    if altered is None or len(altered) == 0:
        return text

    return altered


def pipe_split_plus(text, sep="_"):

    # print pipe_split("[rembrandt van rijn] aligns with [rembrandt van rijn]")

    altered = ""
    split = str(to_bytes(text)).split("|")

    for i in range(len(split)):
        item = split[i].strip()
        item = get_uri_local_name_plus(item, sep)
        if i == 0:
            altered = item
        else:
            altered += " | {}".format(item)

    if altered is None or len(altered) == 0:
        return text

    return altered


def get_uri_ns_local_name(uri):

    if (uri is None) or (uri == ""):
        return None

    if is_property_path(uri) or is_nt_format(uri):

        name = ""
        pro_list = re.findall("<([^<>]*)>/*", uri)

        for i in range(len(pro_list)):
            local = get_uri_local_name(pro_list[i])
            if i == 0:
                name = local
            else:
                name = "{}_{}".format(name, local)
                # print ">>>> name: ", name
        return [None, name]

    else:
        non_alphanumeric_str = re.sub('[ \w]', '', uri)
        if non_alphanumeric_str == "":
            return uri
        else:
            last_char = non_alphanumeric_str[-1]
            index = uri.rindex(last_char)
            name = uri[index + 1:]
            ns = uri[:index+1]
            return [ns, name]


def update_specification(specs):

    # print "Specs update"
    # print specs

    if St.link_old in specs:

        if specs[St.link_old]:
            if is_property_path(specs[St.link_old]) or is_nt_format(specs[St.link_old]):
                pro_list = re.findall("<([^<>]*)>/*", specs[St.link_old])
                name = ""
                for i in range(len(pro_list)):
                    local = get_uri_local_name(pro_list[i])
                    if i == 0:
                        name = local
                    else:
                        name = "{}_{}".format(name, local)
                    # print ">>>> name: ", name
                specs[St.link_old_name] = name
                if len(pro_list) == 1 and St.aligns in specs:
                    specs[St.link_old_ns] = str(specs[St.aligns]).replace(specs[St.link_old_name], '')
                else:
                    specs[St.link_old_ns] = None
            else:
                specs[St.link_old_name] = get_uri_local_name(specs[St.link_old])
                specs[St.link_old_ns] = get_uri_ns_local_name(specs[St.link_old])[0]

    if St.graph in specs:
        if specs[St.graph]:
            specs[St.graph_name] = get_uri_local_name(specs[St.graph])
            specs[St.graph_ns] = get_uri_ns_local_name(specs[St.graph])[0]
            # print specs[St.graph_name]

    if St.entity_datatype in specs:
        specs[St.entity_name] = get_uri_local_name(specs[St.entity_datatype])
        specs[St.entity_ns] = str(specs[St.entity_datatype]).replace(specs[St.entity_name], '')
        # print specs[St.entity_name]

    if St.aligns in specs:

        if specs[St.aligns]:

            if is_property_path(specs[St.aligns]) or is_nt_format(specs[St.aligns]):
                pro_list = re.findall("<([^<>]*)>/*", specs[St.aligns])
                name = ""
                for i in range(len(pro_list)):
                    local = get_uri_local_name(pro_list[i])
                    if i == 0:
                        name = local
                    else:
                        name = "{}_{}".format(name, local)
                    # print ">>>> name: ", name
                specs[St.aligns_name] = name
                if len(pro_list) == 1:
                    specs[St.aligns_ns] = str(specs[St.aligns]).replace(specs[St.aligns_name], '')
                else:
                    specs[St.aligns_ns] = None

            else:
                specs[St.aligns_name] = get_uri_local_name(specs[St.aligns])
                specs[St.aligns_ns] = str(specs[St.aligns]).replace(specs[St.aligns_name], '')
            # print specs[St.aligns_name]

    if St.longitude in specs:

        if specs[St.longitude]:

            if is_property_path(specs[St.longitude]) or is_nt_format(specs[St.longitude]):
                pro_list = re.findall("<([^<>]*)>/*", specs[St.longitude])
                name = ""
                for i in range(len(pro_list)):
                    local = get_uri_local_name(pro_list[i])
                    if i == 0:
                        name = local
                    else:
                        name = "{}_{}".format(name, local)
                        # print ">>>> name: ", name
                specs[St.longitude_name] = name
                if len(pro_list) == 1:
                    specs[St.longitude_ns] = str(specs[St.longitude]).replace(specs[St.longitude_name], '')
                else:
                    specs[St.longitude_ns] = None

            else:
                specs[St.longitude_name] = get_uri_local_name(specs[St.longitude])
                specs[St.longitude_ns] = str(specs[St.longitude]).replace(specs[St.longitude_name], '')
                # print specs[St.aligns_name]

    if St.latitude in specs:

        if specs[St.latitude]:

            if is_property_path(specs[St.latitude]) or is_nt_format(specs[St.latitude]):
                pro_list = re.findall("<([^<>]*)>/*", specs[St.latitude])
                name = ""
                for i in range(len(pro_list)):
                    local = get_uri_local_name(pro_list[i])
                    if i == 0:
                        name = local
                    else:
                        name = "{}_{}".format(name, local)
                        # print ">>>> name: ", name
                specs[St.latitude_name] = name
                if len(pro_list) == 1:
                    specs[St.latitude_ns] = str(specs[St.latitude]).replace(specs[St.latitude_name], '')
                else:
                    specs[St.latitude_ns] = None

            else:
                specs[St.latitude_name] = get_uri_local_name(specs[St.latitude])
                specs[St.latitude_ns] = str(specs[St.latitude]).replace(specs[St.latitude_name], '')
                # print specs[St.aligns_name]

    if St.lens in specs:
        specs[St.lens_name] = get_uri_local_name(specs[St.lens])
        specs[St.lens_ns] = str(specs[St.lens]).replace(specs[St.lens_name], '')

    if St.linkset in specs:
        specs[St.linkset_name] = get_uri_local_name(specs[St.linkset])
        specs[St.linkset_ns] = str(specs[St.linkset]).replace(specs[St.linkset_name], '')

    if St.refined in specs:
        specs[St.refined_name] = get_uri_local_name(specs[St.refined])
        specs[St.refined_ns] = str(specs[St.refined]).replace(specs[St.refined_name], '')

    # print "DONE WITH SPECS UPDATE"


def intersect(a, b):

    if (a is not None) and (b is not None):
        return list(set(a) & set(b))

    return None


def win_bat(file_directory, file_name):

    # NORMALISE THE NAME TO AVOID below
    np = normalise_path(file_directory)
    # print np

    # GET THE DIRECTORY
    directory = os.path.dirname(np) if os.path.isdir(np) is not True else np
    # print dir

    # LOAD ALL FILES
    # file_list = [f for f in os.listdir(dir) if os.path.isfile(join(dir, f))]

    load_builder = cStringIO.StringIO()
    load_builder.write("""\n\techo "Loading data\"""")

    if OPE_SYS == 'windows':
        load_builder.write("\n\tstardog data add {} ".format(Svr.settings[St.stardog_uri]))

    # if OPE_SYS.__contains__(mac_weird_name):
    else:
        stardog_path = Svr.settings[St.stardog_path]
        load_builder.write("\n\t{}stardog data add {} ".format(stardog_path, Svr.settings[St.stardog_uri]))

    # LOAD ONLY .TRIG OR .TTL FILES
    print "\nTHESE FILES WILL BE USED FOR GENERATING A BAT FILE:"
    for f in os.listdir(directory):

        full_path = join(directory, f)

        if os.path.isfile(full_path):

            if f.endswith('.trig') or f.endswith('.ttl'):
                # abs =  os.path.abspath(f).replace("\\", "/")

                load_builder.write(" \"{}\"".format(full_path))
                print "  - {}".format(full_path)

    print load_builder.getvalue()

    # GENERATE THE BAT FILE
    bat_path = "{0}{1}{1}{2}{3}".format(directory, os.path.sep, file_name, batch_extension())
    writer = codecs.open(bat_path, "wb", "utf-8")
    writer.write(to_unicode(load_builder.getvalue()))
    writer.close()

    # print OPE_SYS
    # if OPE_SYS.__contains__(mac_weird_name):
    if OPE_SYS != 'windows':
        os.chmod(bat_path, 0o777)
        print "MAC"

    load_builder.close()

    # RETURN THE BAT FILE
    print "\nTHE BAT FILE IS LOCATED AT:\n  - {}".format(bat_path)
    return bat_path


def batch_extension():

    # print ">>> OPERATING SYSTEM:", OPE_SYS.upper()
    # bat_ext = ""

    if OPE_SYS == "windows":
        bat_ext = ".bat"

    # elif OPE_SYS.__contains__(mac_weird_name):
    else:
        bat_ext = ".sh"

    return bat_ext


def batch_load(batch_load_file):

    if OPE_SYS == "windows":
        return bat_load(batch_load_file)

    # elif OPE_SYS.__contains__(mac_weird_name):
    else:
        return sh_load(batch_load_file)


def bat_load(bat_path):

    try:

        if isfile(bat_path) and bat_path.endswith(batch_extension()):

            # os.system returns 0 if it all went OK and 1 otherwise.
            # BUT IT DOES NOT TELL HOW MANY TRIPLES WHERE ADDED
            # output = os.system("{}".format(bat_path, c_path))

            # SUBPOCESS PRINT THE ENTIRE OUTPUT:
            #   THE FILES THAT WERE ADDED
            #   HOW MANY TRIPLES WHERE ADDED
            output = subprocess.check_output(bat_path, shell=True)
            output = re.sub('\(Conversion\).*\n', '', output)

            # THE OUTPUT CONTAINS FULL PATH THAT IS NOT ADVISABLE TO DISPLAY
            # FIND STRINGS THAT EXHIBIT A FILE PATTERN
            file_path = re.findall(" .:.*\\.*\..*", output)
            for f in file_path:

                if f.__contains__("\\"):
                    # print "FILE FOUND: {}".format(f)
                    test = f.split("\\")
                    # EXTRACT THE END OF THAT PATTERN
                    new = test[len(test) - 1]
                    # REPLACE THE PATTERN WITH THAT END FOUNb ABOVE
                    output = output.replace(f, " " + new)

                elif f.__contains__("/"):
                    # print "FILE FOUND: {}".format(f)
                    test = f.split("/")
                    # EXTRACT THE END OF THAT PATTERN
                    new = test[len(test) - 1]
                    # REPLACE THE PATTERN WITH THAT END FOUNb ABOVE
                    output = output.replace(f, " " + new)

            print "PROCESS OUTPUT: {}".format(output)
            return {"message": "OK", "result": output}

    except Exception as err:
        return {"message": "CHECK THE FILE PATH.\n{}".format(err.message), "result": None}


def sh_load(bat_path):

    try:

        if isfile(bat_path) and bat_path.endswith(batch_extension()):
            print "Executing the batch file from non-windows machine"
            # os.system returns 0 if it all went OK and 1 otherwise.
            # BUT IT DOES NOT TELL HOW MANY TRIPLES WHERE ADDED
            # output = os.system("{}".format(bat_path))

            output = subprocess.check_output(bat_path, shell=True)

            print "PROCESS OUTPUT: {}".format(output)
            return {"message": "OK", "result": output}

    except Exception as err:
        return "CHECK THE FILE PATH.\n{}".format(err.message)


def dir_files(directory, extension_list):

    print directory

    # print "\nTHESE FILES WILL BE USED FOR GENERATING A BAT FILE:"
    lst = []
    for f in os.listdir(directory):

        full_path = join(directory, f)

        if os.path.isfile(full_path):
            ext = os.path.splitext(f)[1].strip().lower()
            if ext in extension_list:
                lst.append(full_path)

    # print list
    return lst


#################################################################
"""
    ABOUT INSERTING NAMED GRAPHS FILES
"""
#################################################################


def insertgraph(dataset_name, f_path, file_count, save=True):

    limit = 70000
    date = datetime.date.isoformat(datetime.date.today()).replace('-', '')
    f_path = f_path.replace("\\", "/")
    ds = rdflib.Dataset()
    name = os.path.basename(f_path)

    new_dir = "{}/Inserted_{}_On_{}".format(os.path.dirname(f_path), name, date)

    try:
        if not os.path.exists(new_dir):
            os.makedirs(new_dir)
    except OSError as err:
        print "\n\t[__init__ in RDF]", err
        return

    print "loading : [{}]".format(file_count)
    print "\n\tFile: {}".format(name)
    start_time = time.time()
    ds.parse(source=f_path, format="trig", encoding='utf-8')
    print "\tLoading completed in{:>8} {} seconds".format(":", str(time.time() - start_time))
    print "\tSize                {:>8} {} triples".format(":", len(ds))

    count = 1
    # count_chunk = 0
    for graph in ds.graph():
        count_lines = 0

        # rdflib.graph.Graph
        if len(graph) > 0:
            name = re.findall("<.*>", str(graph))[0]
            if name.__contains__("file:") is not True:
                print "\t>>> Named-graph [{}]{:>15} {}".format(count, ":", name)
                count_chunk = 0
                qrybldr = cStringIO.StringIO()
                qrybldr.write("INSERT DATA\n{{\n\tGRAPH {}\n".format(name))
                qrybldr.write("\t{\n")

                for subj, pred, obj in graph:
                    count_lines += 1

                    #  If literal
                    if type(obj) == rdflib.term.Literal:
                        if len(obj) == 1:
                            # obj = to_bytes(obj)
                            obj = obj.replace("\\", "\\\\")
                        obj = "\"\"\"{}\"\"\"".format(to_bytes(obj))
                        # print obj

                    #  if URI
                    elif type(obj) == rdflib.term.URIRef:
                        obj = "<{}>".format(to_bytes(obj))

                    # triple
                    qrybldr.write("\t\t<{}> <{}> {} .\n".format(to_bytes(subj), to_bytes(pred), obj))

                    if count_lines == limit:
                        count_chunk += 1
                        qrybldr.write("\t}\n}\n")
                        query_time = time.time()
                        if save is True:
                            wr = codecs.open("{}/Insert-{}_chunk{}_{}.txt".format(
                                new_dir, dataset_name, count_chunk, date), "wb")
                            wr.write(qrybldr.getvalue())
                            wr.close()
                        qres = Qry.endpoint(qrybldr.getvalue())

                        if qres is not None:
                            doc = xmltodict.parse(qres)
                            print "\t>>> Response of chunk {:<12}: {}".format(count_chunk, doc['sparql']['boolean'])
                            print "\t>>> Inserted in {:>19} {} seconds".format(":", str((time.time() - query_time)))

                        # Reset
                        qrybldr.close()
                        qrybldr = cStringIO.StringIO()
                        qrybldr.write("INSERT DATA\n{{\n\tGRAPH {}\n".format(name))
                        qrybldr.write("\t{\n")
                        count_lines = 0
                        # qres = ""

                qrybldr.write("\t}\n}\n")
                query_time = time.time()
                final = qrybldr.getvalue()
                qrybldr.close()
                if len(final) > 0:
                    count_chunk += 1
                    if save is True:
                        wr = codecs.open("{}/Insert-{}_chunk{}_{}.txt".format(
                            new_dir, dataset_name, count_chunk, date), "wb")
                        wr.write(final)
                        wr.close()
                    qres = Qry.endpoint(final)
                    if qres is not None:
                        doc = xmltodict.parse(qres)
                        print "\t>>> Response of chunk {:<12}: {}".format(count_chunk, doc['sparql']['boolean'])
                        print "\t>>> Inserted in {:>19} {} seconds".format(":", str(time.time() - query_time))
                count += 1

    print "\tProcess completed in {} {} seconds\n".format(":", str(time.time() - start_time))


def insertgraphs(dataset_name, dir_path):

    _format = "%a %b %d %H:%M:%S %Y"
    builder = cStringIO.StringIO()
    files = [f for f in listdir(dir_path) if isfile(join(dir_path, f))]

    print "\n\n{:>114}".format(datetime.datetime.today().strftime(_format))
    builder.write("\n--------------------------------------------------------"
                  "----------------------------------------------------------\n")
    builder.write("    Inserting graphs contained in :\n\t\t{}\n".format(dir_path))
    builder.write("    \tThe folder contains [ {} ] files.\n".format(len(files)))
    builder.write("--------------------------------------------------------"
                  "----------------------------------------------------------\n")

    print builder.getvalue()

    file_count = 1
    for f in listdir(dir_path):
        f_path = join(dir_path, f)
        extension = os.path.splitext(f_path)[1]

        if isfile(f_path) & (extension.lower() == ".trig"):
            # print path
            insertgraph(dataset_name, f_path, file_count)
            file_count += 1


#################################################################
"""
    ABOUT WRITING TO FILE

    REMINDER 1:
    FOR MAC/LINUX REMEMBER TO CHANGE THE FILE PERMISSIONS FOR EXECUTING THE BATCH FILE
        SET: chmod -R 777 Data/
        CHECK: ls -l

    REMINDER 2:
    THE ENVIRONMENT VARIABLES HAVE TO BE SETTLED
        MAKE SURE THE TERMINAL IS RESTARTED AFTER SETTING THE VARIABLES
            in mac
                open ~/.bash_profile
                add to file
                    export STARDOG_HOME=/Users/YOURUSERNAME/Documents/stardog-4.1.3/data
                    export PATH=$PATH:/Users/YOURUSERNAME/Documents/stardog-4.1.3/bin

        TEST THE COMMAND 'STARDOG DATA ADD ...' TO BE SURE
"""
#################################################################


def write_to_file(graph_name, directory, metadata=None, correspondences=None, singletons=None):

    # print graph_name

    """
        2. FILE NAME SETTINGS
    """
    try:
        date = datetime.date.isoformat(datetime.date.today()).replace('-', '')
        dir_name = directory  # write_to_path os.path.dirname(f_path)
        linkset_file = "{}-Linksets-{}.trig".format(graph_name, date)
        metadata_file = "{}-Metadata-{}.trig".format(graph_name, date)
        singleton_metadata_file = "{}-SingletonMetadata-{}.trig".format(graph_name, date)
        dir_name = dir_name.replace("\\", "/")

        linkset_output = "{}/{}".format(dir_name, linkset_file).replace("//", "/")
        metadata_output = "{}/{}".format(dir_name, metadata_file).replace("//", "/")
        singleton_metadata_output = "{}/{}".format(dir_name, singleton_metadata_file).replace("\\", "/")
        try:
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)
        except OSError as err:
            print "\n\t[__init__ in RDF]", err
            return
        # print "output file is :\n\t{}".format(output_path)

        """
            3. WRITE LINKSET TO FILE
        """
        print "\tDIRECTORY NAME:", path.dirname(metadata_output)
        if metadata is not None:
            document = None
            try:
                print "\t\tMETADATA FILE:", path.basename(metadata_output)
                document = codecs.open(metadata_output, "wb", "utf-8")
                document.write(to_unicode(metadata))
                document.close()
            except Exception as err:
                print err
                if document:
                    document.close()

        if correspondences is not None:
            document = None
            try:
                print "\t\tLINKSET FILE:", path.basename(linkset_output)
                document = codecs.open(linkset_output, "wb", "utf-8")
                document.write(to_unicode(correspondences))
                document.close()
            except Exception as err:
                print err
                if document:
                    document.close()

        if singletons is not None:
            document = None
            try:
                print "\t\tSINGLETON METADATA FILE:", path.basename(singleton_metadata_output)
                document = codecs.open(singleton_metadata_output, "wb", "utf-8")
                document.write(to_unicode(singletons))
                document.close()
            except Exception as err:
                print err
                if document:
                    document.close()

    except Exception as err:
        print err


def write_2_disc(file_directory, file_name, data, extension="txt"):
    date = datetime.date.isoformat(datetime.date.today()).replace('-', '')
    file_path = join(file_directory, file_name)
    file_path = "{}_{}.{}".format(file_path, date, extension)
    if file_name is not None and data:
        document = None
        try:
            if not os.path.exists(file_directory):
                os.makedirs(file_directory)
            document = codecs.open(file_path, "wb", "utf-8")
            document.write(to_unicode(data))
            document.close()
        except Exception as err:
            print err
            if document:
                document.close()


def get_writers(graph_name, directory):

    #  print graph_name
    """ 2. FILE NAME SETTINGS """
    date = datetime.date.isoformat(datetime.date.today()).replace('-', '')
    dir_name = directory  # write_to_path  # os.path.dirname(f_path)
    batch_file = "{}_batch_{}{}".format(graph_name, date, batch_extension())
    linkset_file = "{}(Linksets)-{}.trig".format(graph_name, date)
    metadata_file = "{}(Metadata)-{}.sparql".format(graph_name, date)
    singleton_metadata_file = "{}(SingletonMetadata)-{}.trig".format(graph_name, date)
    dir_name = dir_name.replace("\\", "/")
    dir_name = dir_name.replace("//", "/")

    batch_output = "{}/{}".format(dir_name, batch_file)
    linkset_output = "{}/{}".format(dir_name, linkset_file)
    metadata_output = "{}/{}".format(dir_name, metadata_file)
    singleton_metadata_output = "{}/{}".format(dir_name, singleton_metadata_file)

    try:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
    except OSError as err:
        print "\n\t[__init__ in RDF]", err
        return
    # print "output file is :\n\t{}".format(output_path)

    """
        3. WRITE LINKSET TO FILE
    """
    writers = dict()
    writers[St.meta_writer] = codecs.open(metadata_output, "wb", "utf-8")
    writers[St.crpdce_writer] = codecs.open(linkset_output, "wb", "utf-8")
    writers[St.singletons_writer] = codecs.open(singleton_metadata_output, "wb", "utf-8")
    writers[St.batch_writer] = codecs.open(batch_output, "wb", "utf-8")

    writers[St.meta_writer_path] = metadata_output
    writers[St.crpdce_writer_path] = linkset_output
    writers[St.singletons_writer_path] = singleton_metadata_output
    writers[St.batch_output_path] = batch_output

    return writers


def normalise_path(file_path):

    file_path = re.sub('[\']', "\\\\", file_path)
    file_path = re.sub('[\"]', "\\\\", file_path)
    file_path = re.sub('[\1]', "\\\\1", file_path)
    file_path = re.sub('[\2]', "\\\\2", file_path)
    file_path = re.sub('[\3]', "\\\\3", file_path)
    file_path = re.sub('[\4]', "\\\\4", file_path)
    file_path = re.sub('[\5]', "\\\\5", file_path)
    file_path = re.sub('[\6]', "\\\\6", file_path)
    file_path = re.sub('[\7]', "\\\\7", file_path)
    file_path = re.sub('[\0]', "\\\\0", file_path)
    file_path = re.sub('[\a]', "\\\\a", file_path)
    file_path = re.sub('[\b]', "\\\\b", file_path)
    file_path = re.sub('[\f]', "\\\\f", file_path)
    file_path = re.sub('[\n]', "\\\\n", file_path)
    file_path = re.sub('[\r]', "\\\\r", file_path)
    file_path = re.sub('[\t]', "\\\\t", file_path)
    file_path = re.sub('[\v]', "\\\\v", file_path)
    return file_path


def load_triple_store(graph_uri, directory, data):

    #  print graph_name
    """ 2. FILE NAME SETTINGS """
    graph_name = get_uri_local_name(graph_uri)
    date = datetime.date.isoformat(datetime.date.today()).replace('-', '')
    dir_name = directory
    np = normalise_path(dir_name)
    dir_name = os.path.dirname(np) if os.path.isdir(np) is not True else np
    dir_name = dir_name.replace("\\", "/")

    # FILE NAME
    batch_file = "{}_batch_{}{}".format(graph_name, date, batch_extension())
    insert_file = "{}-{}.trig".format(graph_name, date)

    # FILE PATH
    batch_output = "{}/{}".format(dir_name, batch_file)
    insert_output = "{}/{}".format(dir_name, insert_file)

    # MAKE SURE THE FOLDER EXISTS
    try:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
    except OSError as err:
        print "\n\t[utility_LOAD_TRIPLE_STORE:]", err
        return

    # WRITERS
    b_writer = codecs.open(insert_output, "wb", "utf-8")
    i_writer = codecs.open(batch_output, "wb", "utf-8")

    # WRITE DATA TO FILE
    i_writer.write(data.getvalue)
    i_writer.close()

    # GENERATE THE BATCH FILE
    if OPE_SYS == 'windows':
        b_writer.write("\n\tstardog data add {} {}".format(Svr.settings[St.stardog_uri], insert_output))
    else:
        stardog_path = Svr.settings[St.stardog_path]
        b_writer.write("\n\t{}stardog data add {} {}".format(stardog_path, Svr.settings[St.stardog_uri], insert_output))
    b_writer.close()

    # SET ACCESS RIGHT
    if OPE_SYS != 'windows':
        print "MAC BATCH: {}".format(batch_output)
        os.chmod(batch_output, 0o777)

    # RUN THE BATCH FILE
    batch_load(batch_output)
    if os.path.exists(batch_output) is True:
        os.remove(batch_output)

    triples = Qry.get_namedgraph_size(graph_uri)
    print triples

    return {"result": triples, "message": "{} inserted".format(triples)}


def listening(directory, sleep_time=10):

    # run indefinitely
    print directory
    while True:
        # get the directory listing
        lock_file = [name for name in os.listdir(directory)
                     if name.endswith('.lock')]

        # print the most recent listing
        for lock in lock_file:
            print"\t>>> {} is active".format(lock)

        try:
            response = requests.get("http://{}".format(Svr.settings[St.stardog_host_name]))
        except Exception as err:
            response = str(err)

        if str(response).__contains__("10061"):
            print "\t>>> The connection has not been established yet with the stardog server..."

        if len(lock_file) > 0 and str(response).__contains__("401"):
            print "\t>>> THE STARDOG SERVER IS ON AND REQUIRES PASSWORD."
            return "THE STARDOG SERVER IS ON AND REQUIRES PASSWORD."

        if len(lock_file) > 0 and \
                (str(response).__contains__("200") or str(response).__contains__("No connection") is False):
            print "\t>>> >>> THE SERVER IS ON."
            return "THE SERVER IS ON."

        print "\nListening for \"system.lock\" file and checking whether a connection to the server is established..."
        # wait a little bit before getting the next listing
        # if you want near instantaneous updates, make the sleep value small.
        time.sleep(sleep_time)


def stardog_on(bat_path):

    print "\nSTARTING THE STARDOG SERVER"
    directory = Svr.settings[St.stardog_data_path]

    lock_file = [name for name in os.listdir(directory) if name.endswith('.lock')]
    try:
        response = requests.get("http://{}".format(Svr.settings[St.stardog_host_name]))
    except Exception as err:
        response = str(err)

    print response

    # NO NEED FOR TURNING IT ON AS IT IS ALREADY ON
    if len(lock_file) > 0 and (str(response).__contains__("200") or str(response).__contains__("401")):
        print "THE SERVER WAS ALREADY ON."

    else:

        # REMOVE THE LOCK FILE IF IT EXISTS
        if len(lock_file) > 0 and path.exists(join(directory, lock_file[0])):
            os.remove(join(directory, lock_file[0]))

        # CREATE THE BATCH FILE FOR STARTING THE STARDOG SERVER
        if path.exists(bat_path) is False:
            # START stardog-admin.bat server start --disable-security
            if batch_extension() == ".bat":

                cmd = """
    @echo
    @echo -------------------------------------------------------------------------------------------------
    @echo STARTING STARDOG FROM {}...
    @echo -------------------------------------------------------------------------------------------------
    cls
    cd "{}"
    START stardog-admin.bat server start
                """.format(bat_path, Svr.settings[St.stardog_path])

            else:
                cmd = """
                echo STARTING STARDOG...
                "{0}"stardog-admin server start
                """.format(Svr.settings[St.stardog_path])

            writer = open(bat_path, "wb")
            writer.write(cmd)
            writer.close()
            os.chmod(bat_path, 0o777)

        # subprocess.call(bat_path, shell=True)
        if batch_extension() == ".bat":
            os.system(bat_path)
        else:
            os.system("OPEN -a Terminal.app {}".format(bat_path))
        # time.sleep(waiting_time)

        while True:
            try:
                try:
                    response = requests.get("http://{}".format(Svr.settings[St.stardog_host_name]))
                except Exception as err:
                    response = str(err)

                if str(response).__contains__("200"):
                    print ">>> THE SERVER IS ON."
                return "THE SERVER IS ON"

            except Exception as err:
                "ERROR: {}".format(str(err))
                "THE SERVER IS STILL STARTING UP..."
                pass

        # listening(Svr.settings[St.stardog_data_path]) TEST_SERVER


def stardog_off(bat_path):

    print "\nSTOPPING THE STARDOG SERVER"

    directory = Svr.settings[St.stardog_data_path]

    if path.exists(bat_path) is False:

        if batch_extension() == ".bat":

            cmd = """
    @echo -------------------------------------------------------------------------------------------------
    @echo STOPPING STARDOG FROM{}...
    @echo -------------------------------------------------------------------------------------------------
    cls
    cd "{}"
    call stardog-admin server stop
            """.format(bat_path, Svr.settings[St.stardog_path])

        else:

            cmd = """
            echo STOPPING STARDOG...
            "{}"stardog-admin server stop
            """.format(Svr.settings[St.stardog_path])

        writer = open(bat_path, "wb")
        writer.write(cmd)
        writer.close()
        os.chmod(bat_path, 0o777)

    lock_file = [name for name in os.listdir(directory) if name.endswith('.lock')]

    if len(lock_file) > 0:

        off = batch_load(bat_path)

        if off is not None and type(off) is dict:
            # print "IS DICTIONARY"
            print ">>> RESPONSE: {}".format(off['result'])
            # lock_file = [name for name in os.listdir(Svr.settings[St.stardog_data_path]) if name.endswith('.lock')]
            if off['result'].lower().__contains__("successfully") and len(lock_file) > 0:
                # MAKE SURE AS SOMETIMES IT TAKES TIME FOR THE LOCK FILE TO BE REMOVED BY STARDOG
                if path.exists(join(directory, lock_file[0])):
                    os.remove(join(directory, lock_file[0]))
        else:
            print ">>> RESPONSE: {}".format(off)
            lock_file = [name for name in os.listdir(directory) if name.endswith('.lock')]
            if off.lower().__contains__("successfully") and len(lock_file) > 0:
                if path.exists(join(directory, lock_file[0])):
                    os.remove(join(directory, lock_file[0]))

    else:
        print ">>> THE SERVER WAS NOT ON."


def create_database(stardog_bin_path, db_bat_path, db_name):

    # CREATING THE DATABASE IN STARDOG
    create_db = """
    \"{0}\"stardog-admin db create -o spatial.enabled=true search.enabled=true strict.parsing=false -n {1}
    """.format(stardog_bin_path, db_name)

    writer = open(db_bat_path, "wb")
    writer.write(create_db)
    writer.close()
    os.chmod(db_bat_path, 0o777)

    # subprocess.call(bat_path, shell=True)
    print "   >>> CREATING THE {} DATABASE".format(db_name)
    if platform.system().lower() == "windows":
        os.system(db_bat_path)
    else:
        os.system("OPEN -a Terminal.app {}".format(db_bat_path))

def extract_ref(text):

    # example = """(" <http://www.grid.ac/ontology/yfshvbsuov_code>")"""
    if text is None:
        return []
    result = re.findall(".*/([^_]*)_.*", text)
    if len(result) == 0:
        local = get_uri_local_name(text)
        return local
    return result[0]


def diacritic_character_mapping(input_text):
    temp = unicode(input_text, "utf-8")
    # print temp
    builder = cStringIO.StringIO()
    "http://www.fileformat.info/info/unicode/char/0189/index.htm"
    "http://www.jarte.com/help_new/accent_marks_diacriticals_and_special_characters.html"
    # Diacritical Character to ASCII Character Mapping
    "https://docs.oracle.com/cd/E29584_01/webhelp/mdex_basicDev/src/rbdv_chars_mapping.html"
    convert = {

        u"a": u"a", u"á": u"a", u"ä": u"a", u"ã": u"a", u"â": u"a", u"à": u"a", u"å": u"a", u"æ": u"ae", u"ā": u"a",
        u"ă": u"a", u"ą": u"a",
        u"À": u"A", u"Á": u"A", u"Â": u"A", u"Ã": u"A", u"Ä": u"A", u"Å": u"A", u"Æ": u"AE",  u"Ā": u"A", u"Ą": u"A",

        u"b": u"b", u"ƀ": u"b", u"ɓ": u"b", u"ƃ": u"b",
        u"Ƀ": u"B", u"Ɓ": u"B", u"Ƃ": u"B", u"Ƅ": u"B",

        u"c": u"c", u"ç": u"c", u"č": u"c", u"ć": u"c", u"¢": u"c", u"ĉ": u"c",
        u"Ç": u"C", u"Ć": u"C", u"Ĉ": u"C", u"Ċ": u"C", u"Č": u"C", u"ċ": u"C",
        u"ƈ": u"C",
        u"Ƈ": u"C",

        u"d": u"d", u"ď": u"d",  u"đ": u"d", u"ð": u"d", u"ɖ": u"ɖ",
        u"Ď": u"D", u"Đ": u"D", u"Ɖ": u"d",
        u"e": u"e", u"é": u"e", u"ë": u"e", u"ê": u"e", u"è": u"e", u"ē": u"e", u"ĕ": u"e", u"ė": u"e", u"ę": u"e",
        u"ě": u"e",
        u"È": u"E", u"É": u"E", u"Ê": u"E", u"Ë": u"E", u"Ē": u"E", u"Ĕ": u"E", u"Ė": u"E", u"Ę": u"E", u"Ě": u"E",

        u"f": u"f",
        u"g": u"g", u"ġ": u"g", u"ĝ": u"g", u"ģ": u"g",
        u"Ĝ": u"G", u"Ğ": u"G", u"Ġ": u"G", u"Ģ": u"G",

        u"h": u"h", u"ħ": u"h",  u"ĥ": u"h",
        u"Ħ": u"H", u"Ĥ": u"H",

        u"i": u"i", u"í": u"i", u"ï": u"i", u"ì": u"i", u"î": u"i", u"ĭ": u"i", u"ĩ": u"i", u"ī": u"i", u"Į": u"I",
        u"ı": u"i",
        u"Ì": u"I", u"Í": u"I", u"Î": u"I", u"Ï": u"I", u"Ĩ": u"I", u"Ī": u"I", u"Ĭ": u"I", u"į": u"i", u"I": u"I",

        u"Ĳ": u"IJ",
        u"ĳ": u"ij",

        u"ß": u"ss",

        u"j": u"j", u"ĵ": u"j",
        u"Ĵ": u"J",

        u"k": u"k", u"Ķ": u"K", u"ķ": u"k", u"ĸ": u"K",

        u"l": u"l", u"ļ": u"l", u"ľ": u"l", u"ĺ": u"l", u"ŀ": u"l", u"ł": u"l",
        u"Ĺ": u"L", u"Ļ": u"L", u"Ľ": u"L", u"Ŀ": u"L", u"Ł": u"L",

        u"m": u"m", u"µ": u"m",

        u"n": u"n", u"ñ": u"n", u"ń": u"n", u"ņ": u"n", u"ň": u"n", u"ŋ": u"n",
        u"Ñ": u"N", u"Ń": u"N", u"Ņ": u"N", u"Ň": u"N", u"ʼN": u"n", u"Ŋ": u"N",

        u"o": u"o", u"ó": u"o", u"ö": u"o", u"ô": u"o", u"ø": u"o", u"õ": u"o", u"œ": u"oe", u"ò": u"o", u"ɔ": u"o",
        u"Ò": u"O", u"Ó": u"O", u"Ô": u"O", u"Õ": u"O", u"Ö": u"O",  u"Ø": u"O", u"Ɔ": u"O",

        u"Ō": u"O", u"Ŏ": u"O", u"Ő": u"o",
        u"ō": u"o", u"ŏ": u"o", u"ő": u"o",

        u"Œ": u"oe",
        u"p": u"p",
        u"q": u"q",

        u"r": u"r", u"ŕ": u"r", u"ŗ": u"t", u"ř": u"r",
        u"Ŕ": u"R", u"Ŗ": u"R", u"Ř": u"R",

        u"s": u"s", u"ş": u"s", u"š": u"s", u"ś": u"s", u"ŝ": u"s", u"S": u"S", u"ſ": u"s",
        u"Ś": u"S", u"Ŝ": u"S", u"Ş": u"S", u"Š": u"S",

        u"t": u"t", u"ţ": u"t", u"ť": u"t", u"ŧ": u"t", u"Ţ": u"T", u"Ť": u"T",
        u"Ŧ": u"T",

        u"u": u"u", u"ü": u"u", u"û": u"u", u"ù": u"u", u"ú": u"u", u"ũ": u"u", u"ū": u"u", u"ŭ": u"u", u"ů": u"u",
        u"ű": u"u", u"ų": u"u",
        u"Ù": u"U", u"Ú": u"U", u"Ü": u"U", u"Û": u"U", u"Ũ": u"U", u"Ū": u"U", u"Ŭ": u"U", u"Ů": u"U", u"Ű": u"U",
        u"Ų": u"U",

        u"v": u"v",
        u"w": u"w",
        u"ŵ": u"w", u"Ŵ": u"W",
        u"x": u"x",

        u"y": u"y", u"ÿ": u"y", u"ý": u"y", u"ŷ": u"y",
        u"Ÿ": u"Y", u"¥": u"Y", u"Ý": u"Y", u"Ŷ": u"Y",

        u"z": u"z", u"ź": u"z", u"ž": u"z", u"ż": u"z",
        u"Ź": u"Z", u"Ż": u"Z", u"Ž": u"Z",
    }

    # for x, y in convert.items():
    #     print x, y

    for x in temp:
        # print x
        if x in convert:
            # print "yes", x
            builder.write(convert[x])
        else:
            # print "no", x
            if type(x) == unicode:
                builder.write(to_bytes(x))
            else:
                builder.write(unicode(x, "utf-8"))
    return builder.getvalue()


def character_mapping(input_text):

    if type(input_text) is unicode:
        return unidecode(input_text)
    return unidecode(unicode(input_text, encoding="utf-8"))


def to_alphanumeric(input_text, spacing="_"):

    if type(input_text) is not unicode:
        input_text = (unicode(input_text, "utf-8"))
    return re.sub('[\W]', spacing, input_text)


def prep_4_uri(input_text):

    # map diacritic characters
    mapping = character_mapping(input_text)

    # Only alpha numeric
    return to_alphanumeric(mapping)


def zip_folder(input_folder_path, output_file_path=None):

    """
    Zip the contents of an entire folder (with that folder included
    in the archive). Empty sub-folders will be included in the archive
    as well.
    """

    if path.isfile(output_file_path) is not True :
        output_path = os.path.join(os.path.abspath(os.path.join(input_folder_path, os.pardir)), "export.zip")

    parent_dir = os.path.abspath(os.path.join(input_folder_path, os.pardir))

    file_name = os.path.basename(output_file_path)
    (short_name, extension) = os.path.splitext(file_name)

    # Retrieve the paths of the folder contents.
    contents = os.walk(input_folder_path)
    zip_file = None

    try:

        zip_file = Zip.ZipFile(output_file_path, 'w', Zip.ZIP_DEFLATED)

        for root, folders, files in contents:

            # Include all sub-folders, including empty ones.
            for folder_name in folders:
                absolute_path = os.path.join(root, folder_name)
                # print "Adding '%s' to archive." % absolute_path
                zip_file.write(absolute_path, "{0}{0}{1}{0}{0}{2}".format(os.path.sep, short_name, file_name))

            for file_name in files:
                absolute_path = os.path.join(root, file_name)
                # print "Adding '%s' to archive." % absolute_path
                zip_file.write(absolute_path, "{0}{0}{1}{0}{0}{2}".format(os.path.sep, short_name, file_name))

        print "\n\t'%s' created successfully." % output_file_path
        return output_file_path

    except IOError, message:
        print message
        sys.exit(1)
    except OSError, message:
        print message
        sys.exit(1)
    except Zip.BadZipfile, message:
        print message
        sys.exit(1)
    finally:
        if zip_file is not None:
            zip_file.close()


def get_resource_value(resources, targets):

    rsc_builder = Buffer.StringIO()
    if type(resources) is str:
        rsc_builder.write("\t\t{}\n".format(to_nt_format(resources)))
    else:
        for resource in resources:
            rsc_builder.write("\t{}\n".format(to_nt_format(resource)))

    i_format = """
        {{
            GRAPH <{0}>
            {{
                BIND("{2}" AS ?property)
                BIND(<{0}> AS ?dataset)
                ?resource a <{1}> .
                ?resource {2} ?value
            }}
        }}
    """
    query = Buffer.StringIO()
    empty = True
    for dictionary in targets:
        graph = dictionary[St.graph]
        data = dictionary[St.data]
        for types in data:
            data_type = types[St.entity_datatype]
            properties = types[St.properties]
            for i_property in properties:
                p_formatted = to_nt_format(i_property)
                if empty is True:
                    query.write("\t\tVALUES ?resource \n\t\t{{\n\t\t {} \t\t}}".format(rsc_builder.getvalue()))
                    query.write(i_format.format(graph, data_type, p_formatted))
                    empty = False
                else:
                    query.write("\tUNION" + i_format.format(graph, data_type, p_formatted))

    return query.getvalue()
#
# # THIS NEED TO BE A STRING OTHERWISE IT DOES NOT WORK IN STARDOG
#                 BIND("{2}" AS ?property)
#                 # WE BIND THE DATASET TO EXTRACT IT IN THE SELECT
#                 BIND(<{0}> AS ?dataset)
#                 ?resource a <{1}> .
#                 ?resource {2} ?value