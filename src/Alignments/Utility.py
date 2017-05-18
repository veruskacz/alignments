import re
import os
import time
import rdflib
import codecs
import datetime
import cStringIO
import xmltodict
import Query as Qry
import Settings as St
from os import listdir
from os.path import isfile, join
from kitchen.text.converters import to_bytes, to_unicode
write_to_path = "C:\Users\Al\Dropbox\Linksets\ExactName"


#################################################################
"""
    GENERIC FUNCTIONS
"""
#################################################################


def get_uri_local_name(uri):
    # print "URI: {}".format(uri)
    # print type(uri)

    if uri is None:
        return None

    if len(uri) == 0:
        return None

    # if type(uri) is not str:
    #     return None

    else:
        non_alphanumeric_str = re.sub('[ \w]', '', uri)
        if non_alphanumeric_str == "":
            return uri
        else:
            last_char = non_alphanumeric_str[-1]
            index = uri.rindex(last_char)
            name = uri[index + 1:]
            return name


def get_uri_ns_local_name(uri):
    if (uri is None) or (uri == ""):
        return None
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
            specs[St.aligns_name] = get_uri_local_name(specs[St.aligns])
            specs[St.aligns_ns] = str(specs[St.aligns]).replace(specs[St.aligns_name], '')
            # print specs[St.aligns_name]

    if St.lens in specs:
        specs[St.lens_name] = get_uri_local_name(specs[St.lens])
        specs[St.lens_ns] = str(specs[St.lens]).replace(specs[St.lens_name], '')

    if St.linkset in specs:
        specs[St.linkset_name] = get_uri_local_name(specs[St.linkset])
        specs[St.linkset_ns] = str(specs[St.linkset]).replace(specs[St.linkset_name], '')


def intersect(a, b):

    if (a is not None) and (b is not None):
        return list(set(a) & set(b))

    return None


def win_bat(file_directory, file_name):

    # NORMALISE THE NAME TO AVOID below C:\Users\Al\Dropbox\Linksets\test
    np = normalise_path(file_directory)
    # print np

    # GET THE DIRECTORY
    directory = os.path.dirname(np) if os.path.isdir(np) is not True else np
    # print dir

    # LOAD ALL FILES
    # file_list = [f for f in os.listdir(dir) if os.path.isfile(join(dir, f))]

    load_bldr = cStringIO.StringIO()
    load_bldr.write("""\n\techo "Loading data\"""")
    load_bldr.write("\n\tstardog data add risis")

    # LOAD ONLY .TRIG OR .TTL FILES
    print "\nTHESE FILES WILL BE USED FOR GENERATING A BAT FILE:"
    for f in os.listdir(directory):

        full_path = join(directory, f)

        if os.path.isfile(full_path):

            if f.endswith('.trig') or f.endswith('.ttl'):
                # abs =  os.path.abspath(f).replace("\\", "/")

                load_bldr.write(" \"{}\"".format(full_path))
                print "  - {}".format(full_path)

    print load_bldr.getvalue()

    # GENERATE THE BAT FILE
    bat_path = "{}\\{}.bat".format(directory, file_name)
    writer = codecs.open(bat_path, "wb", "utf-8")
    writer.write(to_unicode(load_bldr.getvalue()))
    writer.close()
    load_bldr.close()

    # RETURN THE BAT FILE
    print "\nTHE BAT FILE IS LOCATED AT:\n  - {}".format(bat_path)
    return bat_path


def batch_load(batch_path):

    if isfile(batch_path) and batch_path.endswith('.bat'):
        os.system(batch_path)
        return "YOUR FILE(S) HAVE BEEN LOADED"
    return "CHECK THE FILE PATH."


def dir_files(directory, extension_list):

    print "\nTHESE FILES WILL BE USED FOR GENERATING A BAT FILE:"
    list = []
    for f in os.listdir(directory):

        full_path = join(directory, f)

        if os.path.isfile(full_path):
            ext = os.path.splitext(f)[1].strip().lower()
            if ext in extension_list:
                list.append(full_path)
    print list
    return list


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
    for graph in ds.graphs():
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
"""
#################################################################


def write_to_file(graph_name, metadata=None, correspondences=None, singletons=None):

    # print graph_name

    """
        2. FILE NAME SETTINGS
    """
    try:
        date = datetime.date.isoformat(datetime.date.today()).replace('-', '')
        dir_name = write_to_path  # os.path.dirname(f_path)
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


def get_writers(graph_name):

    # print graph_name

    """
        2. FILE NAME SETTINGS
    """
    date = datetime.date.isoformat(datetime.date.today()).replace('-', '')
    dir_name = write_to_path  # os.path.dirname(f_path)
    batch_file = "{}_batch)_{}.bat".format(graph_name, date)
    linkset_file = "{}(Linksets)-{}.trig".format(graph_name, date)
    metadata_file = "{}(Metadata)-{}.trig".format(graph_name, date)
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
