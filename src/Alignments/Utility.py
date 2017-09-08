import re
import os
import time
import rdflib
import codecs
import datetime
import platform
import cStringIO
import xmltodict
import subprocess
from os import listdir
import Alignments.NameSpace as Ns
import Alignments.Query as Qry
import Alignments.Settings as St
import Alignments.Server_Settings as Svr
from os.path import isfile, join
from kitchen.text.converters import to_bytes, to_unicode
# write_to_path = "C:\Users\Al\Dropbox\Linksets\ExactName"
OPE_SYS = platform.system().lower()
mac_weird_name = "darwin"


#################################################################
"""
    GENERIC FUNCTIONS
"""
#################################################################


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

    if is_property_path(uri) or is_nt_format(uri):

        name = ""
        pro_list = re.findall("<([^<>]*)>/*", uri)

        for i in range(len(pro_list)):
            local = get_uri_local_name(pro_list[i])
            if i == 0:
                name = local
            else:
                name = "{}{}{}".format(name, sep, local)
                # print ">>>> name: ", name
        return name

    else:
        non_alphanumeric_str = re.sub('[ \w]', '', uri)
        if non_alphanumeric_str == "":
            return uri
        else:
            last_char = non_alphanumeric_str[-1]
            index = uri.rindex(last_char)
            name = uri[index + 1:]
            return name


def pipe_split(text, sep="_"):

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


# print pipe_split("[rembrandt van rijn] aligns with [rembrandt van rijn]")


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
                if len(pro_list) == 1:
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

    if St.lens in specs:
        specs[St.lens_name] = get_uri_local_name(specs[St.lens])
        specs[St.lens_ns] = str(specs[St.lens]).replace(specs[St.lens_name], '')

    if St.linkset in specs:
        specs[St.linkset_name] = get_uri_local_name(specs[St.linkset])
        specs[St.linkset_ns] = str(specs[St.linkset]).replace(specs[St.linkset_name], '')

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
        load_builder.write("\n\tstardog data add risis")

    # if OPE_SYS.__contains__(mac_weird_name):
    else:
        stardog_path = Svr.settings[St.stardog_path]
        load_builder.write("\n\t{}stardog data add risis".format(stardog_path))

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

    print ">>> OPERATING SYSTEM:", OPE_SYS.upper()
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
            # return output

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
        path = join(dir_path, f)
        extension = os.path.splitext(path)[1]

        if isfile(path) & (extension.lower() == ".trig"):
            # print path
            insertgraph(dataset_name, path, file_count)
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
        linkset_file = "{}(Linksets)-{}.trig".format(graph_name, date)
        metadata_file = "{}(Metadata)-{}.trig".format(graph_name, date)
        singleton_metadata_file = "{}(SingletonMetadata)-{}.trig".format(graph_name, date)
        dir_name = dir_name.replace("\\", "/")

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

        if metadata is not None:
            document = None
            try:
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
                document = codecs.open(singleton_metadata_output, "wb", "utf-8")
                document.write(to_unicode(singletons))
                document.close()
            except Exception as err:
                print err
                if document:
                    document.close()

    except Exception as err:
        print err


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
        b_writer.write("\n\tstardog data add risis {}".format(insert_output))
    else:
        stardog_path = Svr.settings[St.stardog_path]
        b_writer.write("\n\t{}stardog data add risis {}".format(stardog_path, insert_output))
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


def listening(directory):

    # run indefinitely
    while True:
        # get the directory listing
        lock_file = [name for name in os.listdir(directory)
                     if name.endswith('.lock')]

        # print the most recent listing
        for lock in lock_file:
            print(lock)

        if len(lock_file) > 0:
            return "THE SERVER IS ON."

        # wait a little bit before getting the next listing
        # if you want near instantaneous updates, make the sleep value small.
        time.sleep(1)


def stardog_on(bat_path, waiting_time=10):

    print "\nSTARTING THE STARDOG SERVER"
    lock_file = [name for name in os.listdir(Svr.settings[St.stardog_data_path]) if name.endswith('.lock')]
    if len(lock_file) > 0:
        print "THE SERVER WAS ALREADY ON."
    else:
        # subprocess.call(bat_path, shell=True)
        if batch_extension() == ".bat":
            os.system(bat_path)
        else:
            os.system("OPEN -a Terminal.app {}".format(bat_path))
        time.sleep(waiting_time)
        print "\tTHE SERVER IS ON."


def stardog_off(bat_path):

    print "\nSTOPPING THE STARDOG SERVER"
    lock_file = [name for name in os.listdir(Svr.settings[St.stardog_data_path]) if name.endswith('.lock')]
    if len(lock_file) > 0:
        off = batch_load(bat_path)
        print "\tRESPONSE: {}".format(off)
        if off.lower().__contains__("successfully"):
            lock_file = [name for name in os.listdir(Svr.settings[St.stardog_data_path]) if name.endswith('.lock')]
            if len(lock_file) > 0:
                os.remove(lock_file[0])

    else:
        print "THE SERVER WAS NOT ON."
