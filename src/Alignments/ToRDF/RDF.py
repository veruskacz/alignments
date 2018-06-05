# -*- coding: utf-8 -*-
# coding=utf-8
import re
import os
import codecs
import datetime
import rdflib
import logging
import cStringIO
from rfc3987 import match
from kitchen.text.converters import to_bytes, to_unicode

logging.basicConfig()

""" prefix used for vocabulary """
__name__ = """RDF"""
# data_prefix = u"data"
schema_prefix = u"schema:"
dataset_prefix = u"dataset:"
vocabulary_prefix = u"vocab:"
entity_type_prefix = u"entity"
_dataset = "dataset"

base_default_url = u"<http://risis.eu/>"
dataset_default_url = u"<dataset/>"
schema_default_url = u"<grid/ontology/>"
vocabulary_default_url = u"<grid/ontology/property/>"
entity_default_url = u"<grid/ontology/class/>"
data_default_url = u"<grid/resource/>"

# schema_prefix = u"schema"
# dataset_prefix = u"dataset"
schema_class = u"OntSchema"
ri_class_prefix = u"riClass"
ri_predicate_prefix = u"riPredicate"

date = datetime.date.isoformat(datetime.date.today())

predicate_space = 40

# http://www.regexr.com/


class RDF(object):

    """ Format for writing inline triple:     predicate[vocab:name] value["Al koudous"] end[.] """
    # inlineF = u"            {0:40} {1} {2}\n"
    inlineF = u"            {0:" + u"{0}".format(predicate_space) + u"} {1} {2}\n"

    """ This variable is used to format <predicate> <object> <closing punctuation>
        By default the space between the predicate and the object is set to 40
        Compared to the next format, this format does pre-include the predicate prefix.
    """
    # exPredicateFormat = u"      {0:40}       {1} {2}\n"
    exPredicateFormat = u"      {0:" + u"{0}".format(predicate_space) + u"}       {1} {2}\n"

    """ Inline format using the global predicate_prefix <vocab:> the formatting is as follow:
        vocab:<subject> <predicate> <value> <',' or ';' or '.'>]
    """
    # inlineFormat = u"      " + u"{0}".format(vocabulary_prefix) + u"{0:40} {1} {2}\n"
    inlineFormat = \
        u"      " + u"{0}".format(vocabulary_prefix) + u"{0:" + u"{0}".format(predicate_space) + u"} {1} {2}\n"

    """ Inline format using the global predicate_prefix <vocab:> the formatting is as follow:
        vocab:<subject> <predicate> <value> <',' or ';' or '.'>]
        The difference between this format and the previous one is that this one does not end the line with \n
    """
    # inlineChainFormat = u"      " + u"{0}".format(vocabulary_prefix) + u"{0:40} {1} {2}"
    inlineChainFormat = \
        u"      " + u"{0}".format(vocabulary_prefix) + u"{0:" + u"{0}".format(predicate_space) + u"} {1} {2}"

    """ Format used for triple line: <subject> <predicate> <value> <',' or ';' or '.'>] """
    lineFormat = "{0:>4}{1:30}{2:14}{3:15}\n"

    """ Regular Expressions that might be needed for checking predicate values """

    # Integer Regular expression
    # 01 is not considered as an integer
    rgxInteger = re.compile("^[-+]?[0-9]$|^[-+]?[1-9]\d+$", re.IGNORECASE)

    # Decimal Regular expression
    # Stardog does not support decimal with comma
    rgxDecimal = re.compile("^[-+]?\d*[.]\d+$", re.IGNORECASE)

    # Float Regular expression
    rgxDouble = re.compile("^[-+]?\d*[.,]?\d+[eE][-+]?[0-9]+$", re.IGNORECASE)

    # Date Regular expression
    rgxDate = re.compile(
        "^\d{4}[-/.](0[1-9]|1[012])" +
        "[- /.](0[1-9]|[12][0-9]|3[01])([zZ]?|[-+](0[1-9]|1[0-9]|2[0-4]):00)$", re.IGNORECASE)

    # Time Regular expression
    rgxTime = re.compile(
        "^(0[1-9]|1[0-9]|2[0-3]):[0-5][0-9]" +
        "(:[0-5][0-9](.[0-9]?[0-9]?[0-9]?)?)([zZ]|[-+](0[1-9]|1[0-9]|2[0-4]):00)?$", re.IGNORECASE)

    # Date and Time Regular expression
    rgxDateTime = re.compile(
        "^\\d{4}[-/.](0[1-9]|1[012])[- /.](0[1-9]|[12][0-9]|3[01])([zZ]?|[-+](0[1-9]" +
        "|1[0-9]|2[0-4]):00)T(0[1-9]|1[0-9]|2[0-3]):[0-5][0-9](:[0-5][0-9]" +
        "(\\.[0-9]?[0-9]?[0-9]?)?)([zZ]|[-+](0[1-9]|1[0-9]|2[0-4]):00)?$", re.IGNORECASE)

    def __init__(self, input_path, database, entity_type, is_trig, namespace, schema, schema_metadata=None):

        """ tab predicate value end """
        database = database.replace(" ", "_")
        self.schemaGraphMetadata = schema_metadata
        self.turtleWriter = None
        self.dirName = u"{0}\converted\{1}.{2}\{3}".format(
            os.path.dirname(input_path), database, date, entity_type)
        self.database = database       # -> The name of the database to convert
        self.isTrig = is_trig           # -> boolean Checks the RDF format of the output file
        self.entityType = entity_type

        # self.namespace = namespace.replace(" data: ", u" {0}: ".format(entity_type.lower()))
        self.namespace = namespace.replace(" data: ", u" {0}: ".format(
            "resource" if entity_type is None else entity_type.strip().lower().replace(' ', '_'))
                                           )
        self.schema = schema
        self.refreshCount = 0
        self.instanceCount = 0
        self.fileUpdate = 1
        self.isClosed = False
        self.inputPath = input_path
        self.fileSplitSize = 70000
        self.outputExtension = "trig" if is_trig is True else "ttl"

        '''
            1. Set the output file path
            os.path.splitext(inputPath)[0] separate C:\kitty.jpg.zip as [C:\kitty.jpg] and [.zip]
        '''
        self.fileName = os.path.basename(os.path.splitext(self.inputPath)[0])

        self.dirName = self.dirName.replace("\\", "/")

        self.fileNameWithExtension = "{0}_{1}_{2}_{3}".format(
            self.fileName, str(self.fileUpdate), str(date), self.outputExtension)

        self.outputPath = "{0}/{1}_{2}_{3}.{4}".format(
            self.dirName, self.fileName, str(self.fileUpdate), str(date), self.outputExtension)

        self.outputMetaPath = "{0}/{1}_{2}_(Meta)_{3}.{4}".format(
            self.dirName, self.fileName, str(self.fileUpdate), str(date), self.outputExtension)

        # print "\tOutput file\t\t: ", self.outputPath

        try:
            if not os.path.exists(self.dirName):
                os.makedirs(self.dirName)
        except OSError as err:
            print "\n\t[__init__ in RDF]", err
            return

        """
            2. Create the turtle writer
        """
        self.turtleWriter = codecs.open(self.outputPath, "wb", "utf-8")  # The turtle writer object for the output file
        self.turtleMetaWriter = codecs.open(self.outputMetaPath, "wb", "utf-8")

        """
            3. Write the namespace
        """
        self.turtleWriter.write(self.namespace)
        self.turtleMetaWriter.write(self.namespace)

        """
            4. Write the schema
        """
        if self.schemaGraphMetadata is not None:
            self.turtleMetaWriter.write(self.schemaGraphMetadata)

        if self.schema is not None:
            if self.isTrig is True:
                self.open_meta_trig(schema_prefix)
                self.turtleMetaWriter.write(to_unicode(self.schema))
                self.close_meta_trig()
                self.turtleMetaWriter.close()
            else:
                self.turtleMetaWriter.write(to_unicode(self.schema))
                self.turtleMetaWriter.close()

    @staticmethod
    def triple_value(value):

        """ This function takes as input the predicate's value and returns it in the write format, be it a
            integer, decimal, double, boolean, date, time or dateTime datatype or whether it is a URI """

        # Check whether the value is null or empty
        if value is None:
            return ""
        else:
            value = value.strip()

        # Return an empty string if the value is an empty string
        if value == "":
            return ""

        if value == "\\":
            value += "\\"

        # Replace double quote with a single quote
        value = to_unicode(value)
        value = value.replace('"', "'")

        # URI values
        if ("http://" in value or "https://" in value) and " " not in value:
            if match(value) is not None:
                return to_unicode(u"<{0}>".format(value))
            elif re.search("[“”’`\r\n'\"]+", value, re.IGNORECASE):
                return to_unicode(u"\"\"\"{0}\"\"\"".format(value))
            else:
                return to_unicode(u"\"{0}\"".format(value))  # ^^xsd:string

        # NUMBERS: can be written like other literals with lexical form and datatype
        elif RDF.rgxInteger.match(value):
            return u"\"{0}\"^^xsd:integer".format(value)

        elif RDF.rgxDecimal.match(value):
            return u"\"{0}\"^^xsd:decimal".format(value)

        elif RDF.rgxDouble.match(value):
            return u"\"{0}\"^^xsd:double".format(value)

        # BOOLEAN: values may be written as either 'true' or 'false' (case-sensitive)
        # and represent RDF literals with the datatype xsd:boolean. """
        elif value == "true" or value == "false":
            return u"\"{0}\"^^xsd:boolean".format(value)

        # DATE: specified in the following form "YYYY-MM-DD"
        # Note: All components are required!
        elif RDF.rgxDate.match(value):
            return u"\"{0}\"^^xsd:date".format(value)

        # TIME:
        elif RDF.rgxTime.match(value):
            return u"\"{0}\"^^xsd:time".format(value)

        # DATE - TIME:
        elif RDF.rgxDateTime.match(value):
            return u"\"{0}\"^^xsd:dateTime".format(value)

        # TEXT \u005c
        # ^^xsd:string
        elif re.search("[“”’`\r\n'\"]+", value, re.IGNORECASE):
            return to_unicode(u"\"\"\"{0}\"\"\"".format(value).replace(u"\\", u"\\\\"))

        else:
            # ^^xsd:string
            return to_unicode(u"\"{0}\"".format(value)).replace(u"\\", u"\\\\")

    @staticmethod
    def triple_value_2(value, datatype):
        """ This function takes as input the predicate's value and returns it in the write format, be it a
                    integer, decimal, double, boolean, date, time or dateTime datatype or whether it is a URI """

        # Check whether the value is null or empty
        if value is None:
            return ""
        else:
            value = value.strip()

        # Return an empty string if the value is an empty string
        if value == "":
            return ""

        if value == "\\":
            value += "\\"

        # Replace double quote with a single quote
        value = to_bytes(value)
        value = value.replace('"', "'")

        # TEXT \u005c
        if re.search("[“”’`\r\n'\"]+", value, re.IGNORECASE):
            return b"\"\"\"{0}\"\"\"".format(value).replace("\\", "\\\\")

        else:
            return to_bytes(b"\"{0}\"^^xsd:{1}".format(value, datatype)).replace("\\", "\\\\")

    @staticmethod
    def triple_value_tag(value, tag):
        """ This function takes as input the predicate's value and returns it with a tag or as a URI """

        if type(value) is list and len(value) > 1:
            transformed = cStringIO.StringIO()

            for i in range(len(value)):

                value_to_use = value[i]

                if i == len(value) - 1:
                    # print value
                    # Check whether the value is null or empty
                    if value_to_use is None:
                        pass
                    else:
                        value_to_use = value_to_use.strip()
                        # print "> " + value + " < " + tag + " >"
                        # Return an empty string if the value is an empty string
                        if value_to_use == "":
                            pass

                        if value_to_use == u"\\":
                            value_to_use += u"\\"

                    # Replace double quote with a single quote
                    value_to_use = to_unicode(value_to_use.replace("\"", "'"))

                    # URI values
                    if RDF.rgxDecimal.match(value_to_use):
                        transformed.write(u"\"{0}\"^^xsd:decimal".format(value_to_use))

                    # TEXT \u005c
                    elif re.search("[“”’`\r\n'\"]+", value_to_use, re.IGNORECASE):
                        transformed.write(to_unicode(u"\"\"\"{0}\"\"\"".format(value_to_use)))

                    else:
                        transformed.write(u"\"{0}\"@{1}".format(value_to_use, tag))

                else:

                    # print value
                    # Check whether the value is null or empty
                    if value_to_use is None:
                        pass
                    else:
                        value_to_use = value_to_use.strip()
                        # print "> " + value + " < " + tag + " >"
                        # Return an empty string if the value is an empty string
                        if value_to_use == "":
                            pass

                        if value_to_use == u"\\":
                            value_to_use += u"\\"

                    # Replace double quote with a single quote
                    value_to_use = to_unicode(value_to_use.replace("\"", "'"))

                    # URI values
                    if RDF.rgxDecimal.match(value_to_use):
                        transformed.write(u"\"{0}\"^^xsd:decimal, ".format(value_to_use))

                    # TEXT \u005c
                    elif re.search("[“”’`\r\n'\"]+", value_to_use, re.IGNORECASE):
                        transformed.write(to_unicode(u"\"\"\"{0}\"\"\", ".format(value_to_use)))

                    else:
                        transformed.write(u"\"{0}\"@{1}, ".format(value_to_use, tag))

            return transformed.getvalue()

        else:
            # print value
            # Check whether the value is null or empty
            if value is None:
                return u""
            else:
                value = value.strip()
                # print "> " + value + " < " + tag + " >"
                # Return an empty string if the value is an empty string
                if value == "":
                    return u""

                if value == u"\\":
                    value += u"\\"

            # Replace double quote with a single quote
            value = to_unicode(value.replace("\"", "'"))

            # URI values
            if RDF.rgxDecimal.match(value):
                return u"\"{0}\"^^xsd:decimal".format(value)

            # TEXT \u005c
            elif re.search("[“”’`\r\n'\"]+", value, re.IGNORECASE):
                return to_unicode(u"\"\"\"{0}\"\"\"".format(value))

            else:
                return u"\"{0}\"@{1}".format(value, tag)

    @staticmethod
    def triple_value_prefix(prefix, value):
        """ This function takes as input the predicate's prefix and value and returns it as a URI with a prefix """

        # Check whether the value is null or empty
        if value is None:
            return u""
        else:
            value = value.strip()

        # Return an empty string if the value is an empty string
        if value == "":
            return u""

        if value == u"\\":
            value += u"\\"

        # value = value.split(',')

        if type(value) is list and len(value) > 1:
            transformed = cStringIO.StringIO()
            for i in range(len(value)):
                value_to_use = RDF.check_for_uri(value[i])
                if i == len(value) - 1:
                    transformed.write(u"{0}:{1}".format(prefix, value_to_use))
                else:
                    transformed.write(u"{0}:{1}, ".format(prefix, value_to_use))
            return transformed.getvalue()

        else:
            value = RDF.check_for_uri(value)
            return u"{0}:{1}".format(prefix, value)

    def write_subject(self, count, subject):

        # Make sure subject is okay for URI
        subject = self.check_for_uri(subject)

        self.turtleWriter.write(u"\t### [ {0} ] About the {1}: {2}.\n".format(count, self.entityType.lower(), subject))
        self.turtleWriter.write(u"{0}{1}\n".format('\t', subject))
        self.turtleWriter.write(self.exPredicateFormat.format(
            'rdf:type', self.triple_value_prefix(entity_type_prefix, self.entityType), ' ;'))

    def write_subject_pre(self, count, subject, prefix):

        # Make sure subject is okay for URI
        subject = self.check_for_uri(subject)

        if self.turtleWriter is not None:
            self.turtleWriter.write(u"\t### [ {0} ] About the {1}: {2}.\n".
                                    format(count, self.entityType.lower(), subject))

            self.turtleWriter.write(u"{0}{1}:{2}\n".format('\t', prefix, subject))

            self.turtleWriter.write(self.exPredicateFormat.format(
                'rdf:type', self.triple_value_prefix(entity_type_prefix, self.entityType), ' ;'))

    def write_string(self, attribute, value, last):
        # Make sure attribute is okay for URI
        attribute = self.check_for_uri(attribute)

        if self.turtleWriter is not None:
            value = to_unicode(value)
            """ Write a [predicate Value] line """
            last = '.' if last is True else ";"
            if value is not None:
                value = (u"{0}".format(value)).strip()
                if value != "":
                    to_write = to_unicode(self.inlineFormat.format(attribute, self.triple_value(value), last))
                    self.turtleWriter.write(to_write)
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False

    def write_string_chain(self, attribute, value, has_predicate, comma, prefix, end):
        """
            Write a [predicate Value] line
        """
        # Make sure attribute is okay for URI
        attribute = self.check_for_uri(attribute)

        last = u',' if comma is True else u";"
        if end is True and last == u";":
            last = u'.'
        if value is not None:
            value = str(value).strip()
            if value != "":
                if has_predicate is True:
                    if prefix != "":
                        self.turtleWriter.write(
                            self.inlineFormat.format(attribute, self.triple_value_prefix(prefix, value), last))
                    else:
                        self.turtleWriter.write(self.inlineFormat.format(attribute, self.triple_value(value), last))
                else:
                    if prefix != "":
                        self.turtleWriter.write(
                            self.inlineF.format(attribute, self.triple_value_prefix(prefix, value), last))
                    else:
                        self.turtleWriter.write(self.inlineF.format(attribute, self.triple_value(value), last))
                return True
            return False
        else:
            return False

    def write_string_chain_2(self, attribute, value, has_predicate, comma, prefix, end, datatype):

        """
            Write a [predicate Value] line
        """
        # Make sure attribute is okay for URI
        attribute = self.check_for_uri(attribute)

        last = u',' if comma is True else u";"
        if end is True and last == u";":
            last = u'.'
        if value is not None:
            value = str(value).strip()
            if value != "":
                if has_predicate is True:
                    if prefix != "":
                        self.turtleWriter.write(
                            self.inlineFormat.format(attribute, self.triple_value_prefix(prefix, value), last))
                    else:
                        self.turtleWriter.write(
                            self.inlineFormat.format(attribute, self.triple_value_2(value, datatype), last))
                else:
                    if prefix != "":
                        self.turtleWriter.write(
                            self.inlineF.format(attribute, self.triple_value_prefix(prefix, value), last))
                    else:
                        self.turtleWriter.write(
                            self.inlineF.format(attribute, self.triple_value_2(value, datatype), last))
                return True
            return False
        else:
            return False

    def write_string_prefix(self, attribute, prefix, value, last):
        """ Write a [predicate prefix:Value] line """
        # Make sure attribute is okay for URI
        attribute = self.check_for_uri(attribute)

        ans = False
        last = u'.' if last is True else u";"
        if value is not None:
            value = str(value).strip()
            if value != "":
                ans = True
                self.turtleWriter.write(
                    self.inlineFormat.format(attribute, self.triple_value_prefix(prefix, value), last))
        return ans

    def write_string_tag(self, attribute, value, tag, last):
        """ Write a [predicate Value@tag] line """
        # Make sure attribute is okay for URI
        attribute = self.check_for_uri(attribute)

        last = u'.' if last is True else u";"
        if value is not None:
            value = value.strip()
            # print attribute + " " + value + " " + tag
            value = to_unicode(value)
            if value != "":
                to_write = to_unicode(self.inlineFormat.format(attribute, self.triple_value_tag(value, tag), last))
                self.turtleWriter.write(to_write)

    def write_array(self, attribute, array, last):
        """
            Write an array of [predicate Value] lines
        """
        # Make sure attribute is okay for URI
        attribute = self.check_for_uri(attribute)

        last = u'.' if last is True else u";"

        if array is not None:

            # Array of one element
            if len(array) == 1:
                self.turtleWriter.write(self.inlineFormat.format(attribute, self.triple_value(array[0]), last))

            # array of more than one element
            elif len(array) >= 1:
                self.turtleWriter.write(
                    self.inlineFormat.format(attribute, self.triple_value(array[0]), u" ,"))

                for i in range(1, len(array) - 1):
                    self.turtleWriter.write(self.inlineF.format(u"", self.triple_value(array[i]), u" ,"))

                self.turtleWriter.write(
                    self.inlineF.format(u"", self.triple_value(array[len(array) - 1]), last))

    def write_array_prefix(self, attribute, prefix, array, last):
        """ Write an array of [predicate prefix:Value] lines """
        # Make sure attribute is okay for URI
        attribute = self.check_for_uri(attribute)

        last = u'.' if last is True else u";"
        if array is not None:

            # Array of one element
            if len(array) == 1:
                self.turtleWriter.write(
                    self.inlineFormat.format(attribute, self.triple_value_prefix(prefix, array[0]), last))

            # array of more than one element
            elif len(array) >= 1:
                self.turtleWriter.write(
                    self.inlineFormat.format(attribute, self.triple_value_prefix(prefix, array[0]), u" ,"))

                for i in range(1, len(array) - 1):
                    self.turtleWriter.write(
                        self.inlineF.format(u"", self.triple_value_prefix(prefix, array[i]), u" ,"))

                self.turtleWriter.write(
                    self.inlineF.format(u"", self.triple_value_prefix(prefix, array[len(array) - 1]), last))

    def write_dict(self, dictionary):
        dict_size = len(dictionary)
        count = 1
        for key2, value2 in dictionary.items():
            end = True if count == dict_size else False
            ans = self.write_string(key2, value2, end)

            # if the last attribute has no value
            if end is True and ans is False:
                self.turtleWriter.write("\t  .\n")
            count += 1

    def write_pro_vale(self, pro_val_obj, object_property_prefix_dic):

        if self.turtleWriter is not None:

            dict_size = len(pro_val_obj)
            count = 1

            for pair in pro_val_obj:

                _property = pair["property"]
                # print "property: ", property

                end = True if count == dict_size else False

                # Properties with entity type
                if _property in object_property_prefix_dic:

                    # This is an option to document the resource with its string representation.
                    # But it was removed because we assumed that if the resource exists, this information
                    # will always reside as properties of the entity itself.
                    # ans = self.write_string_chain_2(_property, pair["value"], True, True,
                    #                                 object_property_prefix_dic[_property], end, datatype="string")
                    # ans = self.write_string_chain_2("", pair["value"], False, False, "", end, datatype="string")

                    ans = self.write_string_prefix(_property, object_property_prefix_dic[_property], pair["value"], end)

                else:
                    ans = self.write_string(_property, to_bytes(pair["value"]), end)

                # if the last attribute has no value
                if end is True and ans is False:
                    self.turtleWriter.write("\t  .\n")

                count += 1

    def write_line(self, string):
        """ This function allows writing new line to a file without
        continuously adding the newline escape character """

        # Writer no set
        if self.turtleWriter is None:
            return
        else:
            self.turtleWriter.write(to_unicode(string) + b'\n')

    def write_meta_line(self, string):
        """ This function allows writing new line to a file without
        continuously adding the newline escape character """

        # Writer no set
        if self.turtleMetaWriter is None:
            return
        else:
            self.turtleMetaWriter.write(to_unicode(string) + b'\n')

    def open_trig(self, prefix):
        """ This function sets the name of the named-graph and opens the curly bracket"""
        self.write_line(u"")

        # The Named-graph
        self.write_line(u"### [ About {0}'s {1} ]".format(self.database, _dataset))
        if self.isTrig is True:
            self.write_line(u"{0}{1}".format(prefix, self.database))
            self.write_line(u"{")

    def open_meta_trig(self, prefix):
        """ This function sets the name of the named-graph and opens the curly bracket"""
        self.write_meta_line(u"")

        # The Named-graph
        self.write_meta_line(u"### [ About {0}'s {1} ]".format(self.database, _dataset))
        if self.isTrig is True:
            self.write_meta_line(u"{0}{1}".format(prefix, self.database))
            self.write_meta_line(u"{")

    def close_trig(self):
        """ This function closes the named-graph """
        if self.turtleWriter is not None:
            self.turtleWriter.write(u"}\n")

    def close_meta_trig(self):
        """ This function closes the named-graph """
        if self.turtleMetaWriter is not None:
            self.turtleMetaWriter.write(u"}\n")

    def close_writer(self):
        """ This function closes the dataset named-graph and the writer  """
        if self.isTrig is True:
            self.close_trig()

        self.turtleWriter.close()
        self.isClosed = True

        try:
            self.check_rdf_file(self.outputPath)
        except Exception as exception:
            print "\n", exception
        try:
            self.check_rdf_file(self.outputMetaPath)
        except Exception as exception:
            print "\n", exception

    def refresh(self):
        """ This function makes sure that a new file is created whenever self.fileSplitSize is reached """
        self.close_writer()
        self.isClosed = True

        """ File Update
        """
        self.fileUpdate += 1
        # print "replace: ", self.fileNameWithExtension
        # print "File name: ", self.fileName
        self.outputPath = "{0}\{1}.{2}.{3}.{4}".format(
            self.dirName, self.fileName, str(self.fileUpdate), str(date), self.outputExtension)
        self.turtleWriter = codecs.open(self.outputPath, "wb", "utf-8")
        # print self.outputPath
        """ Namespace update
        """
        self.write_line(self.namespace)

        """ Schema Update
        """
        if self.schema is not None:
            if self.isTrig is True:
                self.open_trig(schema_prefix)
                self.turtleWriter.write(self.schema)
                self.close_trig()
            else:
                self.turtleWriter.write(self.schema)

        """ Named-graph update
        """
        if self.isTrig is True:
            self.open_trig(dataset_prefix)

        """ File close status update
        """
        self.isClosed = False

    def check_rdf_file(self, file_path):

        rdf_file = os.path.basename(file_path)
        graph_format = self.outputExtension
        if graph_format == 'ttl':
            graph_format = "turtle"
        """
            Check the currently closed RDF file
        """
        print "\nRefresh: ", self.fileUpdate
        print "--------------------------------------------------------------------------------------------------------"
        print "Output file > " + file_path
        print "-------------------------------------------------------------------------------------------------------#"
        print "    Syntactic check of: ", rdf_file
        g = rdflib.Dataset()
        print '    Loading ', rdf_file
        g.load(source=file_path, format=graph_format)
        print '    The file is a valid RDF with length:', str(len(g))

    @staticmethod
    def check_for_uri(attribute):
        attribute = attribute.strip()
        for c in [' ', '/', ',', "\"", '\t']:
            attribute = attribute.replace(c, "_")
        attribute = attribute.replace('&', "_and_")
        return attribute

    # def write_schema(self, schema_dict):
    #     """Takes in a dictionary {key:attribute value:description} and generates an RDF schema."""
    #     schema = cStringIO.StringIO()
    #     count = 0
    #     for key, value in schema_dict.items():
    #         count += 1
    #         subject = key
    #
    #         if value != "":
    #             schema.write(u"\t### [ {0} ] About: {1}\n".format(count, subject))
    #             schema.write(u"{0}{1}:{2}\n".format(u'\t', vocabulary_prefix, subject))
    #             schema.write(u"      {0:47}{1} ;\n".format("rdf:type", "rdf:Property"))
    #             schema.write(u"      {0:47}{1} .\n\n".format("rdfs:comment", self.triple_value(value)))
    #         else:
    #             schema.write(u"\t### [ {0} ] About: {1}\n".format(count, subject))
    #             schema.write(u"{0}{1}:{2}\n".format(u'\t', vocabulary_prefix, subject))
    #             schema.write(u"      {0:47}{1} .\n".format("rdf:type", "rdf:Property"))
    #
    #     return schema.getvalue()

    # """More than one attribute"""
    #
    # def write_array_objects(self, array, attributes, prefix):
    #
    #     """One attribute"""
    #     if len(attributes) > 0:
    #
    #         if len(array) == 1:
    #             for obj in array:
    #                 self.write_string(attributes[0], obj[attributes[0]], last=False)
    #
    #         elif len(array) > 1:
    #             self.write_string_chain(
    #                 attributes[0], array[0][attributes[0]], comma=True, has_predicate=True, prefix=prefix)
    #
    #             for i in range(1, len(array) - 1):
    #                 self.write_string_chain(
    #                     "", array[i][attributes[0]], comma=True, has_predicate=False, prefix=prefix)
    #
    #             self.write_string_chain(
    #                 "", " {0}".format(
    #                     array[len(array) - 1][attributes[0]]), comma=False, has_predicate=False, prefix=prefix)
    #
    #     """More than one attribute"""

    # def set_general_format(self, sub_position, pre_position):
    #     # TODO work on this code
    #     """ 4. Set the RDF triple formatter """
    #     sub_position = 6
    #     # vocab: takes 6 slots
    #     pre_position = sub_position + self.longestHeader
    #     self.pvFormat = u"{0:>" + u"{0}".format(
    #         str(sub_position)) + u"} {1:" + u"{0}".format(str(pre_position)) + u"} {2}"
