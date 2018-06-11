# -*- coding: utf-8 -*-
# coding=utf-8

import sys

from Alignments.ToRDF.RDF import *
from Alignments.Utility import win_bat as bat
from kitchen.text.converters import to_bytes, to_unicode

__name__ = """CSV"""
entity_type_prefix = u"entity"


class CSV(RDF):

    def no_id(self, database, is_trig, file_to_convert, separator, entity_type, rdftype, activated=False):

        if activated is False:
            print "The function [CSV: no_id] has not been activated."
            return

        database = database.replace(" ", "_")

        """
            param database: name of the dataset
            param is_trig: A boolean value indicating the format of the RDF file that will be generated.
            param file_to_convert: Represents the oath of the CSV file that that is to be converted.
            param separator: A character specifying the character used for value separation.
            param entity_type: The name of the entity type starting by a capital character.

            Note: This conversion uses the number of the row as subject identifier. This is used when it
            is hard to isolate an entity withing the csv file or no column qualifies as identifier.
        """

        bom = ''
        _file = ""
        print
        self.errorCount = 0
        self.rdftype = rdftype
        self.inputPath = file_to_convert  # -> string   The out file path
        self.pvFormat = u""  # -> string   Representing RDF triple format to use for formatting Predicate_Value
        self.risisOntNeutral = "riClass:Neutral"  # Prefix for Neutrality
        self.lastColumn = 0  # -> int      The last attribute index
        self.longestHeader = 0  # -> int      The number of characters in the longest attribute
        self.data_prefix = entity_type.strip().lower().replace(' ', '_')
        '''Replace unwanted characters -> #;:.-(–)—[']`=’/”{“}^@*+!~\,%'''
        self.pattern = '[?&#;:%!~+`=’*.(\-)–\\—@\['',\\]`{^}“/”]'

        try:
            # Open the file to convert
            # _file = codecs.open(self.inputPath, 'rb', encoding="utf-8")
            _file = open(self.inputPath, 'rb')

        except Exception as exception:
            print "\n", exception
            exit(1)

        """ About BYTE ORDER MARK (BOM) """
        self.first_line = to_bytes(_file.readline())
        if self.first_line.startswith(to_bytes(codecs.BOM_UTF8)):
            for i in range(len(to_bytes(codecs.BOM_UTF8))):
                bom += self.first_line[i]
            self.first_line = self.first_line.replace(bom, '')
            print u"[" + os.path.basename(self.inputPath) + u"]", u"contains BOM."

        # get the first line
        self.first_line = self.first_line.strip(u'\r\n')
        print "\n\tThis is the header: ", self.first_line

        # Get the attribute headers
        # -> Array  about the list of attributes in the csv file
        self.csvHeader = self.extractor(self.first_line, separator)
        self.csvHeaderLabel = self.extractor(self.first_line, separator)
        print "\tThis is the header: ", self.csvHeader
        print "THE HEADER IS OF SIZE:", len(self.csvHeader)

        """ 2. Get the last column ID. This allows to stop the loop before the end
                whenever the identification column happens to be the last column"""
        self.lastColumn = len(self.csvHeader) - 1
        # This is no longer the case because we now keep the column used as reference
        # if self.subjectID == self.lastColumn:
        #     self.lastColumn -= 1

        """ 3. Get the attribute headers and make them URI ready"""
        for i in range(0, len(self.csvHeader)):

            # '''Replace unwanted characters -> #;:.-(–)—[']`=’/”{“}^@*+!~\,%'''
            # pattern = '[?&#;:%!~+`=’*.(\-)–\\—@\['',\\]`{^}“/”]'
            self.csvHeader[i] = self.csvHeader[i].replace(' ', '_')
            self.csvHeader[i] = re.sub(self.pattern, u"", self.csvHeader[i].replace('&', "_and_"))

            '''For every attribute composed of more than 1 word and separated by space,
            start the first word with lower case followed by the underscore character'''

            # print self.csvHeader
            new_header = ""
            header_split = self.csvHeader[i].split()
            if header_split is not None and len(header_split) > 0:
                new_header = header_split[0].lower()

            for j in range(1, len(header_split)):
                new_header += u"_" + header_split[j]
                self.csvHeader[i] = new_header
            # print header_split

            '''Get the size (number of characters) of the longest attribute'''
            if self.longestHeader < len(self.csvHeader[i]):
                self.longestHeader = len(self.csvHeader[i])

        """ 4. Set the RDF triple formatter """
        sub_position = 6
        # vocab: takes 6 slots
        pre_position = sub_position + self.longestHeader
        self.pvFormat = u"{0:>" + u"{0}".format(
            str(sub_position)) + u"} {1:" + u"{0}".format(str(pre_position)) + u"} {2}"

        schema = self.get_schema(entity_type=entity_type, field_metadata=self.fieldMetadata)
        # print schema
        RDF.__init__(self, input_path=self.inputPath, database=database, entity_type=entity_type,
                     is_trig=is_trig, namespace=self.get_namespace(database), schema=schema)

        n = 0
        """ Opening the named-graph """
        self.open_trig(dataset_prefix)

        """ Writing the rdf instances of the dataset """
        while True:

            n += 1
            line = to_unicode(_file.readline(), "utf-8")

            if not line:

                """ Closing the named-graph by closing the turtle writer """
                if self.isClosed is not True:
                    self.close_writer()

                print '\nNo more line... Process ended at line > ' + str(n)
                print 'Done with converting [' + file_to_convert + '] to RDF!!!'
                _file.close()

                # WRITE THE BAT FILE
                print "\n", self.dirName
                self.bat_file = bat(self.dirName, self.database)
                break

            # if n <= 5:
            #     # print line
            #     pass
            # if n == 6:
            #     self.turtleWriter.close()
            #     break

            # """ Proceed with the conversion """
            # self.write_triples_2(to_unicode(line), separator, row_number=n, field_metadata=self.fieldMetadata)

            buffered = ""
            while True:

                print >> sys.stderr, '\r', "\tCURRENT LINE: {}".format(n),

                record = line
                if not record:
                    break

                if buffered != "":
                    div = CSV.extractor(record, separator, content_delimiter='"')
                    if len(div) != len(self.csvHeader):
                        record = "{}{}".format(buffered, record)

                div = CSV.extractor(record, separator, content_delimiter='"')

                if len(div) < len(self.csvHeader):
                    buffered = "{}".format(record)
                    print ">>> Buffered: {}".format(buffered)

                elif len(div) == len(self.csvHeader):
                    # print "\nLINE: {}".format(record.rstrip())
                    # print "SIZE: {}".format(len(div))
                    buffered = ""
                    # for item in div:
                    #     print "{}".format(item)

                    """ Proceed with the conversion """
                    self.write_triples_2(div, row_number=n, field_metadata=self.fieldMetadata)
                    break

                elif len(div) > len(self.csvHeader):
                    print "\nERROR!!!!"
                    # REPORT ERROR IN THE CHARACTER SEPARATED VALUE FORMAT
                    if len(div) != len(self.csvHeader):
                        self.errorCount += 1
                        print "{:5} Record encoding error. Header: {} columns while Record: {} columns".format(
                            self.errorCount, len(self.csvHeader), len(div))
                        print "\t\t{:8}".format(div)
                        # print line
                        # PRINTING ITEMS
                        for i in range(0, len(div)):
                            print b"\t\t{} - {}".format(i + 1, to_bytes(div[i]))
                    break

                line = to_unicode(_file.readline())

    def __init__(self, database, is_trig, file_to_convert, separator, entity_type,
                 rdftype=None, subject_id=None, embedded_uri=None, field_metadata=None, activated=False):

        entity_type = entity_type.strip().replace(" ", "_")
        database = database.strip().replace(" ", "_")

        if activated is False:
            print "The function [CSV init] has not been activated."
            return

        # embedded_uri is an array of dictionaries.
        # For each dictionary, We have:
        #   ID:Integer <- of the column that needs to became a uri
        #   reverse:Boolean <- to determine whether the URI needs to connect to the subject
        #   namespace:string e.g. http://risis.eu/ <- the namespace to assign to the new URI
        #   predicate:string It could be just the property (e.g. CityOf) or the URI (http://risis.eu/resource/CityOf)

        print "RDF TYPE LIST : {}".format(rdftype)
        print "SUBJECT ID    : {}".format(subject_id)
        """
            param database: name of the dataset
            param is_trig: A boolean value indicating the format of the RDF file that will be generated.
            param file_to_convert: Represents the oath of the CSV file that that is to be converted.
            param separator: A character specifying the character used for value separation.
            param subject_id: The index of the column identified to be used as the subject in the RDF file.
            param entity_type: The name of the entity type starting by a capital character.
        """
        self.embedded_uri = embedded_uri
        self.fieldMetadata = field_metadata
        if subject_id is None:
            self.no_id(database, is_trig, file_to_convert, separator, entity_type, rdftype, activated=activated)
            return

        bom = ''
        _file = ""

        self.errorCount = 0
        self.rdftype = rdftype
        self.subjectID = subject_id         # -> int      The index of the attribute to use as identification
        self.inputPath = file_to_convert    # -> string   The out file path
        self.pvFormat = u""  # -> string   Representing RDF triple format to use for formatting Predicate_Value
        self.risisOntNeutral = "riClass:Neutral"  # Prefix for Neutrality
        self.lastColumn = 0  # -> int      The last attribute index
        self.longestHeader = 0  # -> int      The number of characters in the longest attribute
        # self.data_prefix = entity_type.lower().replace(' ', '_')
        self.data_prefix = "resource" if entity_type is None else entity_type.strip().lower().replace(' ', '_')

        '''Replace unwanted characters -> #;:.-(–)—[']`=’/”{“}^@*+!~\,%'''
        self.pattern = '[?&#;:%!~+`=’*.(\-)–\\—@\['',\\]`{^}“/”]'

        try:
            # Open the file to convert
            # _file = codecs.open(self.inputPath, 'rb', encoding="utf-8")
            _file = open(self.inputPath, 'rb')

        except Exception as exception:
            print "\n", exception
            exit(1)

        """ About BYTE ORDER MARK (BOM) """
        self.first_line = _file.readline().strip()
        if self.first_line.startswith(to_bytes(codecs.BOM_UTF8)):
            for i in range(len(to_bytes(codecs.BOM_UTF8))):
                bom += self.first_line[i]
            self.first_line = self.first_line.replace(bom, '')
            print u"[" + os.path.basename(self.inputPath) + u"]", u"contains BOM."

        # get the first line
        # self.first_line = self.first_line.strip(u'\r\n')
        print "\n\tTHIS IS THE HEADER STRING  : ", self.first_line

        # Get the attribute headers
        # -> Array  about the list of attributes in the csv file
        self.csvHeader = self.extractor(self.first_line, separator)
        self.csvHeaderLabel = self.extractor(self.first_line, separator)
        print "\tTHIS IS THE HEADER LIST    : ", self.csvHeader
        print "\tTHE HEADER LIST IS OF SIZE : ", len(self.csvHeader)

        """ 2. Get the last column ID. This allows to stop the loop before the end
                whenever the identification column happens to be the last column"""
        self.lastColumn = len(self.csvHeader) - 1
        # This is no longer the case because we now keep the column used as reference
        # if self.subjectID == self.lastColumn:
        #     self.lastColumn -= 1

        """ 3. Get the attribute headers and make them URI ready"""
        for i in range(0, len(self.csvHeader)):

            self.csvHeader[i] = self.csvHeader[i].replace(' ', '_')
            self.csvHeader[i] = re.sub(self.pattern, u"", self.csvHeader[i].replace('&', "_and_"))

            '''For every attribute composed of more than 1 word and separated by space,
            stat the first word with lower case followed by the underscore character'''

            # print self.csvHeader
            new_header = ""
            header_split = self.csvHeader[i].split()
            if header_split is not None and len(header_split) > 0:
                new_header = header_split[0].lower()
            for j in range(1, len(header_split)):
                new_header += u"_" + header_split[j]
                self.csvHeader[i] = new_header
            # print header_split

            '''Get the size (number of characters) of the longest attribute'''
            if self.longestHeader < len(self.csvHeader[i]):
                self.longestHeader = len(self.csvHeader[i])

        """ 4. Set the RDF triple formatter """
        sub_position = 6
        # vocab: takes 6 slots
        pre_position = sub_position + self.longestHeader
        self.pvFormat = u"{0:>" + u"{0}".format(
            str(sub_position)) + u"} {1:" + u"{0}".format(str(pre_position)) + u"} {2}"

        schema = self.get_schema(entity_type=entity_type, field_metadata=self.fieldMetadata)
        # print schema
        RDF.__init__(self, input_path=self.inputPath, database=database, entity_type=entity_type,
                     is_trig=is_trig, namespace=self.get_namespace(database), schema=schema)

        n = 0
        """ Opening the named-graph
        """
        self.open_trig(dataset_prefix)

        """ Writing the rdf instances of the dataset
        """
        while True:

            n += 1
            line = to_unicode(_file.readline())

            if not line:

                # WRITE THE BAT FILE
                print "\n\nFILE LOCATION: {}", self.dirName
                self.bat_file = bat(self.dirName, self.database)

                """ Closing the named-graph by closing the turtle writer.
                    CAN POSSIBLY THROUGH AND EXCEPTION BY RDFLIB AFTER CHECKING THE FILE
                """
                if self.isClosed is not True:
                    self.close_writer()

                print '\nNo more line... Process ended at line > ' + str(n)
                print 'Done with converting [' + file_to_convert + '] to RDF!!!'
                _file.close()

                break

            # if n <= 5:
            #     print line
            #     pass
            # if n <= 72:
            # """ Proceed with the conversion """
            # self.write_triples(to_unicode(line), separator, embedded_uri, self.fieldMetadata)

            buffered = ""
            while True:

                print >>  sys.stderr, '\r', "\tCURRENT LINE: {}".format(n),

                record = line
                if not record:
                    break

                if buffered != "":
                    div = CSV.extractor(record, separator, content_delimiter='"')
                    if len(div) != len(self.csvHeader):
                        record = u"{}{}".format(buffered, record)

                div = CSV.extractor(record, separator, content_delimiter='"')

                if len(div) < len(self.csvHeader):
                    buffered = u"{}".format(record)
                    print u">>> Buffered: {}".format(buffered)

                elif len(div) == len(self.csvHeader):
                    # print "\nLINE: {}".format(record.rstrip())
                    # print "SIZE: {}".format(len(div))
                    buffered = ""
                    # for item in div:
                    #     print "{}".format(item)

                    """ Proceed with the conversion """
                    self.write_triples(div, embedded_uri, self.fieldMetadata)
                    break

                elif len(div) > len(self.csvHeader):
                    print "\nERROR!!!!"
                    # REPORT ERROR IN THE CHARACTER SEPARATED VALUE FORMAT
                    if len(div) != len(self.csvHeader):
                        self.errorCount += 1
                        print "{:5} Record encoding error. Header: {} columns while Record: {} columns".format(
                            self.errorCount, len(self.csvHeader), len(div))
                        print "\t\t{:8}".format(div)
                        # print line
                        # PRINTING ITEMS
                        for i in range(0, len(div)):
                            print b"\t\t{} - {}".format(i + 1, to_bytes(div[i]))

                    break

                line = to_unicode(_file.readline())

        print "\n"

    @staticmethod
    def extractor(record, separator, content_delimiter='"', check=None):
        td = content_delimiter
        attributes = []
        temp = ""

        # print record
        i = 0
        while i < len(record):

            if record[i] == td:
                complete = False
                j = i + 1
                while j < len(record):
                    if record[j] != td:
                        temp += record[j]
                    # THE CURRENT CHARACTER IS A DELIMITER
                    elif j + 1 < len(record) and record[j + 1] != separator:
                        if record[j] != td:
                            temp += record[j]
                    elif j + 1 < len(record) and record[j + 1] == separator:

                        # "column ""weird stuff"", something else",
                        if j > 0 and record[j - 1] != td:
                            j += 2
                            complete = True
                            break

                        # "column ""weird stuff""",
                        elif j > 1 and (record[j - 1] != td or record[j - 2] == td):
                            j += 2
                            complete = True
                            break
                        else:
                            temp += record[j]
                    j += 1

                # completed or at the end
                if complete == True or j == len(record):
                    value = temp.strip()
                    if value.startswith(td) and value.endswith(td):
                        value = value[1:-1]
                    # print value, j
                    if value != td:
                        attributes.append(value)
                # print temp, j, len(record)
                temp = ""
                i = j

            else:
                while i < len(record):

                    # Enqueue if you encounter the separator
                    if record[i] == separator:
                        value = temp.strip()
                        if value.startswith(td) and value.endswith(td):
                            value = value[1:-1]
                        attributes.append(value)
                        # print "> separator " + temp
                        temp = ""

                    # Append if the current character is not a separator
                    if record[i] != separator:
                        temp += record[i]
                        # print "> temp " + temp

                    # Not an interesting case. Just get oit :-)
                    else:
                        i += 1
                        break

                    # Increment the iterator
                    i += 1

        # Append the last attribute
        if temp != "":
            value = temp.strip()
            if value.startswith(td) and value.endswith(td):
                value = value[1:-1]
            # print 2, value
            if value != td:
                attributes.append(value)

        # print "EXTRACTOR RETURNED: {}".format(attributes)
        return attributes

    @staticmethod
    def get_namespace(database):
        """ This function outputs the static hardcoded namespace required for the OrgRef dataset """
        name_space = cStringIO.StringIO()
        name_space.write("\t### Name Space #########################################################################\n")
        name_space.write("\t@base <http://risis.eu/> .\n")
        name_space.write("\t@prefix dataset: <dataset/> .\n")
        name_space.write("\t@prefix schema: <ontology/> .\n")
        name_space.write("\t@prefix entity: <{0}/ontology/class/> .\n".format(database))
        name_space.write("\t@prefix vocab: <{0}/ontology/predicate/> .\n".format(database))
        name_space.write("\t@prefix data: <{0}/resource/> .\n".format(database))

        name_space.write("\t@prefix riClass: <risis/ontology/class/> .\n")

        name_space.write("\t@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n")
        name_space.write("\t@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n")
        name_space.write("\t@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n")
        name_space.write("\t@prefix owl: <http://www.w3.org/2002/07/owl#> .\n")
        name_space.write("\t########################################################################################\n")
        content = name_space.getvalue()
        name_space.close()
        return content

    @staticmethod
    def view_file(file_path, size=10):
        bom = ''
        # _file = ""
        # first_line = ""
        # text = ""
        bldr = cStringIO.StringIO()
        try:
            # Open the file to convert
            # _file = codecs.open(self.inputPath, 'rb', encoding="utf-8")
            _file = open(file_path, 'rb')

        except Exception as exception:
            # print "\n", exception
            message = "NO DATASET FILE UPLOADED\n\n\n\n\n\n\t\t" + str(exception)
            return {"header": "NO DATASET FILE UPLOADED",  "sample": message}

        """ About BYTE ORDER MARK (BOM) """
        first_line = to_bytes(_file.readline())

        if first_line.startswith(to_bytes(codecs.BOM_UTF8)):
            for i in range(len(to_bytes(codecs.BOM_UTF8))):
                bom += first_line[i]
            first_line = first_line.replace(bom, '')
            print u"[" + os.path.basename(file_path) + u"]", u"contains BOM."

        # get the first line
        first_line = first_line.strip(u'\r\n')
        bldr.write(first_line + "\n")

        for i in range(0, size):
            bldr.write(_file.readline())
        text = bldr.getvalue()
        bldr.close()
        _file.close()

        # print text
        return {"header": first_line, "sample": text}

    @staticmethod
    def view_data(file_path, limit=1000):
        # file = ""
        # sample = ""
        builder = cStringIO.StringIO()
        _file = open(file_path, 'rb')
        for i in range(0, limit):
            builder.write(_file.readline())
        builder.write("\n...")
        sample = builder.getvalue()
        _file.close()
        builder.close()
        return sample

    def view_converted_data(self, limit=1000):
        # file = ""
        # sample = ""
        builder = cStringIO.StringIO()
        _file = open(self.outputPath, 'rb')
        for i in range(0, limit):
            builder.write(_file.readline())
        builder.write("\n...")
        sample = builder.getvalue()
        _file.close()
        builder.close()
        return sample

    def view_converted_schema(self, limit=1000):
        # file = ""
        # sample = ""
        builder = cStringIO.StringIO()
        _file = open(self.outputMetaPath, 'rb')
        for i in range(0, limit):
            builder.write(_file.readline())
        builder.write("\n...")
        sample = builder.getvalue()
        _file.close()
        builder.close()
        return sample

    def get_schema(self, entity_type, field_metadata=None):
        """ This function gets the set of attribute header as the NEUTRAL implicit Orgref RDF schema """
        schema = cStringIO.StringIO()
        schema.write('\n')

        schema.write("\t### Classes #####################################################\n")
        schema.write("\t#################################################################\n\n")

        if entity_type is not None and entity_type != "":
            schema.write("\t### [  ]\n")
            schema.write(u"\t{0}:{1}\n".format(entity_type_prefix, entity_type))
            schema.write(self.pvFormat.format("", 'rdf:type', "rdfs:Class, owl:Class ;\n"))
            schema.write(self.pvFormat.format(b"", b"rdfs:label", self.triple_value(entity_type) + u" .\n"))

        schema.write("\n\n\t### Properties ##################################################\n")
        schema.write("\t#################################################################\n\n")

        # """Create the named graph"""
        # if is_trig is True:
        #     schema.write("### [ About the schema of " + str(database) + " ]\n")
        #     schema.write(schema_prefix + database.strip().replace(" ", "_") + "\n")
        #     schema.write(u"{\n")

        description = None
        if field_metadata is not None:
            description = field_metadata["description"]

        curr_description = None
        for i in range(0, len(self.csvHeader)):
            if description is not None:
                curr_description = description[i]

            schema.write(b"\t### [ " +
                         str(i + 1) + b" ] About the attribute: \"" + to_bytes(self.csvHeader[i]) + b"\" \n")
            schema.write(b"\t" +
                         to_bytes(vocabulary_prefix) + to_bytes(self.csvHeader[i]).strip().replace(b" ", b"_") + b"\n")
            schema.write(self.pvFormat.format(b"", b"rdf:type", self.risisOntNeutral + u" ,\n"))
            schema.write(self.pvFormat.format(b"", b"", b"rdf:Property" + u" ;\n"))

            # WRITING GIVEN COMMENT
            if curr_description is not None and len(curr_description) > 0:
                schema.write(
                    self.pvFormat.format(b"", b"rdfs:comment", self.triple_value(curr_description) + u" ;\n"))

            # WRITING GIVEN COMMENT
            if self.rdftype is not None and i in self.rdftype:
                schema.write(
                    self.pvFormat.format(b"", b"rdfs:comment", self.triple_value(
                        "This property was not used to describe the data as it has "
                        "been redefined as an RDF property ") + u" ;\n"))

            schema.write(self.pvFormat.format(
                b"", b"rdfs:label", self.triple_value(self.csvHeaderLabel[i]) + b" .\n"))
            if i != len(self.csvHeader) - 1:
                schema.write(b"\n")

        # """Close the named graph"""
        # if is_trig is True:
        #     schema.write("}\n")

        return schema.getvalue()

    # TODO OLD FUNCTION, CAN BE REMOVED
    def write_triples_old(self, line, separator, embedded_uri=None, field_metadata=None):

        # print line

        # Replace unwanted characters -> \r\n
        # line = line.rstrip(u'\r\n')
        record = self.extractor(line, separator)

        # REPORT ERROR IN THE CHARACTER SEPARATED VALUE FORMAT
        if len(record) != len(self.csvHeader):
            self.errorCount += 1
            print "{:5} Record encoding error. Header: {} columns while Record: {} columns".format(
                self.errorCount, len(self.csvHeader), len(record))
            print "\t\t{:8}".format(record)
            # print line
            for i in range(0, len(record)):
                print b"\t\t{} - {}".format(i+1, to_bytes(record[i]))
            return ""

        size = len(record) - 1
        record[size] = record[size].rstrip(u'\r\n')
        # print str(record[size]).__contains__(u'\r\n')
        # print record
        subject_resource = record[self.subjectID]

        if subject_resource is not None:
            subject_resource = subject_resource.strip()

        if len(subject_resource) > 0:

            if subject_resource != "":
                self.refreshCount += 1
            if self.refreshCount > self.fileSplitSize:
                self.refreshCount = 0
                self.refresh()

            # Write the subject
            self.instanceCount += 1
            self.write_line("\t### [ " + str(self.instanceCount) + " ]")
            # self.write_line(u"\t{0}:".format(self.data_prefix) + subject_resource.replace(" ", "_"))
            resource_uri = u"\t{0}:".format(self.data_prefix) + self.check_for_uri(subject_resource)

            # WRITE ABOUT THE INVERSE RESOURCE THAT POINTS HTO THE SUBJECT
            if embedded_uri is not None:
                for specs in embedded_uri:
                    if specs['reverse'] is True:
                        if specs['namespace'] is not None and len(specs['namespace']) > 0:
                            namespace = specs['namespace'].strip()
                            subject = u"\t<{0}>".format(namespace + self.check_for_uri(record[specs['id']]))
                        else:
                            subject = u"\t{0}:".format(self.data_prefix) + self.check_for_uri(record[specs['id']])

                        if specs['predicate'] is not None and len(specs['predicate']) > 0:
                            if specs['predicate'].__contains__("http"):
                                predicate = "<{}>".format(specs['predicate'].strip())
                            else:
                                predicate = vocabulary_prefix + self.check_for_uri(specs['predicate'])
                        else:
                            predicate = vocabulary_prefix + self.csvHeader[specs['id']]
                        self.write_line(subject)
                        self.write_line( self.pvFormat.format("", predicate, resource_uri) + " .")
                        self.write_line("")



            # WRITE ABOUT THE RESOURCE
            self.write_line(resource_uri)

            if self.entityType is not None and self.entityType != "":
                self.write_line(self.pvFormat.format("", 'rdf:type', u"{0}:{1} ;".format(
                    entity_type_prefix, self.entityType)))

            # Write the values
            self.write_record_values(record, embedded_uri, field_metadata)
            # print record

    def write_triples(self, colon_list, embedded_uri=None, field_metadata=None):

        record = colon_list

        size = len(record) - 1
        record[size] = record[size].rstrip(u'\r\n')

        # print record
        subject_resource = record[self.subjectID]

        if subject_resource is not None:
            subject_resource = subject_resource.strip()

        if len(subject_resource) > 0:

            if subject_resource != "":
                self.refreshCount += 1
            if self.refreshCount > self.fileSplitSize:
                self.refreshCount = 0
                self.refresh()

            # Write the subject
            self.instanceCount += 1
            self.write_line("\t### [ " + str(self.instanceCount) + " ]")
            # self.write_line(u"\t{0}:".format(self.data_prefix) + subject_resource.replace(" ", "_"))
            resource_uri = u"\t{0}:".format(self.data_prefix) + self.check_for_uri(subject_resource)

            # WRITE ABOUT THE INVERSE RESOURCE THAT POINTS HTO THE SUBJECT
            if embedded_uri is not None:
                for specs in embedded_uri:
                    if specs['reverse'] is True:
                        if specs['namespace'] is not None and len(specs['namespace']) > 0:
                            namespace = specs['namespace'].strip()
                            subject = u"\t<{0}>".format(namespace + self.check_for_uri(record[specs['id']]))
                        else:
                            subject = u"\t{0}:".format(self.data_prefix) + self.check_for_uri(record[specs['id']])

                        if specs['predicate'] is not None and len(specs['predicate']) > 0:
                            if specs['predicate'].__contains__("http"):
                                predicate = "<{}>".format(specs['predicate'].strip())
                            else:
                                predicate = vocabulary_prefix + self.check_for_uri(specs['predicate'])
                        else:
                            predicate = vocabulary_prefix + self.csvHeader[specs['id']]
                        self.write_line(subject)
                        self.write_line( self.pvFormat.format("", predicate, resource_uri) + " .")
                        self.write_line("")



            # WRITE ABOUT THE RESOURCE
            self.write_line(resource_uri)

            if self.entityType is not None and self.entityType != "":
                self.write_line(self.pvFormat.format("", 'rdf:type', u"{0}:{1} ;".format(
                    entity_type_prefix, self.entityType)))

            # Write the values
            self.write_record_values(record, embedded_uri, field_metadata)
            # print record

    def write_record_values(self, record, embedded_uri=None, field_metadata=None):
        """ This function takes as an argument a csv record as
        an array witch represents a csv line in the dataset """

        array_sep = None
        if field_metadata is not None:
            array_sep = field_metadata["array_sep"]

        if len(record) != len(self.csvHeader):
            return ""

        # ITERATE THROUGH THE HEADER
        for i in range(0, len(self.csvHeader)):

            # GETTING PROPERTY VALUES
            cur_value = record[i].strip()
            # print str(i) + " " + self.csvHeader[i] + "\t" + cur_value

            # GETTING THE SEPARATOR FOR THAT HEADER
            curr_sep = None
            if array_sep is not None:
                curr_sep = array_sep[i]

            # SPLITTING THE RECORD USING curr_sep
            # IN CASE THE VALUE HAS A SPECIFIC FORMAT
            if curr_sep is not None and len(curr_sep) > 0:
                values = cur_value.split(curr_sep)

                for value in values:
                    if self.rdftype is None or i not in self.rdftype:
                        # print "NOT WORKING IN MORE"
                        self.write_predicate_value(i, value, embedded_uri)
                    elif i in self.rdftype:
                        # print "WORKING IN MORE"
                        self.write_rdftype_value(i, value)

            else:
                if self.rdftype is None or i not in self.rdftype:
                    # print "NOT WORKING " + str(self.rdftype)
                    self.write_predicate_value(i, cur_value, embedded_uri)
                elif i in self.rdftype:
                    # print "WORKING"
                    self.write_rdftype_value(i, cur_value)

    # TODO OLD FUNCTION, CAN BE REMOVED
    def write_triples_2_old(self, line, separator, row_number, field_metadata=None):

        # print line
        # line = line.strip(b'\r\n')

        record = self.extractor(line, separator)
        size = len(record) - 1
        record[size] = record[size].rstrip(u'\r\n')
        # print str(record[size]).__contains__(u'\r\n')
        # print record
        subject_resource = "R{0}".format(row_number)

        if subject_resource is not None:
            subject_resource = subject_resource.strip()

        if subject_resource != "":
            self.refreshCount += 1
        if self.refreshCount > self.fileSplitSize:
            self.refreshCount = 0
            self.refresh()

        # Write the subject
        self.instanceCount += 1
        self.write_line("\t### [ " + str(self.instanceCount) + " ]")

        # self.write_line(u"\t{0}:".format(self.data_prefix) + subject_resource.strip().replace(" ", "_"))
        self.write_line(u"\t{0}:".format(self.data_prefix) + self.check_for_uri(subject_resource))

        if self.entityType is not None and self.entityType != "":
            self.write_line(self.pvFormat.format("", 'rdf:type', u"{0}:{1} ;".format(
                entity_type_prefix, self.entityType)))

        # Write the values
        self.write_record_values(record, field_metadata)
        # print record

    def write_triples_2(self, colon_list, row_number, field_metadata=None):

        # print line
        # line = line.strip(b'\r\n')

        record = colon_list
        size = len(record) - 1
        record[size] = record[size].rstrip(u'\r\n')

        # print record
        subject_resource = "R{0}".format(row_number)

        if subject_resource is not None:
            subject_resource = subject_resource.strip()

        if subject_resource != "":
            self.refreshCount += 1
        if self.refreshCount > self.fileSplitSize:
            self.refreshCount = 0
            self.refresh()

        # Write the subject
        self.instanceCount += 1
        self.write_line("\t### [ " + str(self.instanceCount) + " ]")

        # self.write_line(u"\t{0}:".format(self.data_prefix) + subject_resource.strip().replace(" ", "_"))
        self.write_line(u"\t{0}:".format(self.data_prefix) + self.check_for_uri(subject_resource))

        if self.entityType is not None and self.entityType != "":
            self.write_line(self.pvFormat.format("", 'rdf:type', u"{0}:{1} ;".format(
                entity_type_prefix, self.entityType)))

        # Write the values
        self.write_record_values(record, field_metadata)
        # print record

    def write_predicate_value(self, index, value, embedded_uri=None):
        is_embedded = False
        val = value.strip()

        if embedded_uri is not None:
            for spec in embedded_uri:
                # print spec
                if index == spec['id']:
                    is_embedded = True
                    break
        # print is_embedded, "-->", index

        # The last column has a value so, end the triple with a dot
        if index == self.lastColumn and val != "":

            # A URI VALUE
            if is_embedded:
                self.write_line(
                    self.pvFormat.format(
                        u"", vocabulary_prefix + self.csvHeader[index], u"{}:{}".format(
                            self.data_prefix, self.check_for_uri(val))) + u" .")

            self.write_line(
                self.pvFormat.format(
                    "", vocabulary_prefix + self.csvHeader[index], self.triple_value(val)) + " .")
            self.write_line("")

        # The last column does not have a value => No triple but end of the subject.
        elif index == self.lastColumn and val == "":
            self.write_line("{0:>6}".format("."))
            self.write_line("")

        # Normal RDF business
        elif val != b"":
            # print("\n" + "[" + str(i) + "]" + self.csvHeader[i] + ": " + cur_value)

            # A URI VALUE
            if is_embedded:
                self.write_line(
                    self.pvFormat.format(
                        u"", vocabulary_prefix + self.csvHeader[index] + u"_uri", u"{}:{}".format(
                            self.data_prefix, self.check_for_uri(val))) + u" ;")

            self.write_line(self.pvFormat.format(u"", u"{0}{1}".format(
                vocabulary_prefix, self.csvHeader[index]), self.triple_value(val)) + u" ;")

    def write_rdftype_value(self, index, value):

        val = value.strip()
        # val = str(value.replace(' ', '_')).strip()
        # val = re.sub(self.pattern, u"", val.replace('&', "_and_"))
        # print self.triple_value(val)

        # The last column has a value so, end the triple with a dot
        if index == self.lastColumn and val != "":

            self.write_line(self.pvFormat.format(u"", u"rdf:type", u"{}:{}".format(
                self.data_prefix, self.check_for_uri(val))) + u" ;")

            self.write_line(self.pvFormat.format(
                u"", vocabulary_prefix + self.csvHeader[index], self.triple_value(val)) + u" .")
            self.write_line("")

        # The last column does not have a value => No triple but end of the subject.
        elif index == self.lastColumn and val == "":
            self.write_line("{0:>6}".format("."))
            self.write_line("")

        # Normal RDF business
        elif val != b"":
            # print("\n" + "[" + str(i) + "]" + self.csvHeader[i] + ": " + cur_value)
            self.write_line(
                self.pvFormat.format(u"", u"rdf:type", u"{}:{}".format(
                    self.data_prefix, to_unicode(self.check_for_uri(val)))) + u" ;")
            self.write_line(
                self.pvFormat.format(u"", vocabulary_prefix + self.csvHeader[index], self.triple_value(val)) + u" ;")

# print CSV.extractor("""\"Name","Country","State?","Level",
# "Wikipedia","Wikidata","VIAF","ISNI","GRID","Website","ID\"""", ",")
#
# CSV.view_file("C:\Users\Al\PycharmProjects\Linkset\Data_uploaded\orgref.csv")
#
# data = "Column_1,Column_2,Column_3,\"Column_4\",Column_5\n,Column_6,Column_7,Column_8"
# _file = open("C:\Users\Al\Downloads\CSV_Test.csv")
# buffered = ""
# while True:
#
#     record = _file.readline()
#     if not record:
#         break
#
#     if buffered != "":
#         div = CSV.extractor(record, ",", content_delimiter='"')
#         if len(div) != 8:
#             record = "{}{}".format(buffered, record)
#
#     div = CSV.extractor(record, ",", content_delimiter='"')
#
#     if len(div) < 8:
#         buffered = "{}".format(record)
#         print ">>> Buffered: {}".format(buffered)
#
#     elif len(div) == 8:
#         print "\nLINE: {}".format(record)
#         buffered = ""
#         print "SIZE: {}".format(len(div))
#         for item in div:
#             print "{}".format(item)
#         # break
#
#     elif len(div) > 8:
#         # buffered = ""
#         print div
#         print "\nERROR!!!!"
#         # break


# test_path = "C:\Users\Al\Downloads\Atest\orgreg_hei_export5October2017_.csv"
# test_file = open(test_path)
# header = test_file.readline()
# separated = CSV.extractor(header, ";" )
# print "SIZE:", len(header)
# print "THE HEADER:", header
# for i in range(0, len(separated)):
#
#     print >> sys.stderr, i, '\r',

    # print "{:<6}{}".format(i+1, separated[i])

# row = test_file.readline()
# print "ROW:", row
# separated_row = CSV.extractor(row, ";" )
# print "SIZE OF THE ROW:", len(separated_row)
# for item in separated_row:
#     print item

# print CSV.extractor('"Name", "Country","State","Level","Wikipedia","Wikidata","VIAF","ISNI","GRID","Website","ID"', ',')
# print CSV.extractor(' "title" , "n" , "sd" , "ed" , "pa" , "an" , "mn" , "co" , "tc" , "cou" ,', ',')

# eureca = "C:\Productivity\queryResults.csv"
# convert_13 = CSV(
#     database="Eureca_20180601", is_trig=True, subject_id=0,
#     file_to_convert=eureca,
#     separator=",", entity_type="EurecaProjects", rdftype=[], embedded_uri=None, activated=True)