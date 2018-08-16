import Alignments.Utility as Ut
import Alignments.Query as Qry
from Alignments.Utility import get_uri_local_name_plus as local_name

# CLUSTER ID
# CLUSTER SIZE
# MACHINE EVAL
# HUMAN EVAL
# RESOURCES


def test(data, resources):

    # DATASET AND THE PROPERTIES OF INTEREST. EACH PROPERTY CAN BE PROVIDED WITH AN ALTERNATIVE NAME
    # data = {
    #     'dataset-1': {
    #         'mandatory': [('property-1', 'name'), ('property-10', ""), ('property-15', '')],
    #         'optional': [('property-00', 'country'), ]
    #     },
    #     'dataset-2': {
    #         'mandatory': [('property-2', 'name'), ('property-23', ""), ('property-30', "")],
    #         'optional': []
    #     },
    #     'dataset-3': {
    #         'mandatory': [('property-3', 'name'), ('property-36', ""), ('property-33', "")],
    #         'optional': []
    #     }
    # }

    # THE LIST OF RESOURCES TO INVESTIGATE
    # resource = ['resource-1', 'resource-2', 'resource-3']

    # QUERY TEMPLE EXAMPLE
    """
    SELECT *
    {
        # LIST OR RESOURCES TO INVESTIGATE
        VALUES ?resource { resource-1 resource-2 resource-3 }

        {
            GRAPH <dataset-2>
            {
				BIND( <dataset-2> as ?dataset)
				?resource <property-2> ?name .
				?resource <property-23> ?dataset-2_property-23 .
				?resource <property-30> ?dataset-2_property-30 .
            }
        }	UNION

        {
            GRAPH <dataset-3>
            {
				BIND( <dataset-3> as ?dataset)
				?resource <property-3> ?name .
				?resource <property-36> ?dataset-3_property-36 .
				?resource <property-33> ?dataset-3_property-33 .
            }
        }	UNION

        {
            GRAPH <dataset-1>
            {
				BIND( <dataset-1> as ?dataset)
				?resource <property-1> ?name .
				?resource <property-10> ?dataset-1_property-10 .
				?resource <property-15> ?dataset-1_property-15 .
				OPTIONAL { ?resource <property-00> ?country . }
            }
        }
    }
    """

    count_union = 0
    sub_query = ""

    template_1 =     """\t{}
        {{
            GRAPH {}
            {{ \n\t\t\t\t{}\n{}{}
            }}
        }}"""

    template_2 = """
    SELECT *
    {{
        # LIST OR RESOURCES TO INVESTIGATE
        VALUES ?resource {{ {} }}
        {}
    }}

    """

    # CONVERTING THE LIST INTO A SPACE SEPARATED LIST
    resource_enumeration = " ".join( Ut.to_nt_format(item) for item in resources)

    for dataset, dictionary in data.items():

        mandatory = dictionary['mandatory']
        optional = dictionary['optional']

        # GENERATE THE SUB-QUERY FOR MANDATORY PROPERTIES
        sub_mandatory = "\n".join(
            "\t\t\t\t?resource {0} ?{1} .".format(
                Ut.to_nt_format(uri), alternative if len(alternative) > 0 else
                "{}_{}".format(local_name(dataset), local_name(uri)) ) for uri, alternative in mandatory)

        # GENERATE THE SUB-QUERY FOR OPTIONAL PROPERTIES
        if len(optional) > 0:
            sub_optional = "\n".join(
                "\n\t\t\t\tOPTIONAL {{ ?resource {0} ?{1} . }}".format(
                    Ut.to_nt_format(uri), alternative if len(alternative) > 0 else
                    "{}_{}".format(local_name(dataset), local_name(uri))) for uri, alternative in optional)
        else:
            sub_optional = ""

        # BIND THE DATASET TO HAVE IT IN THE SELECT
        bind = "BIND( {} as ?dataset)".format(Ut.to_nt_format(dataset))

        # ACCUMULATE THE SUB-QUERIES
        sub_query += template_1.format(
            "UNION\n" if count_union > 0 else "", Ut.to_nt_format(dataset), bind, sub_mandatory, sub_optional)
        count_union += 1

    query = template_2.format(resource_enumeration, sub_query)

    Qry.display_result(query, is_activated=True)

    return query


# TESTING
info = {
        'dataset-1': {
            'mandatory':[('property-1', 'name'), ('property-10', ""), ('property-15', '')],
            'optional': [('property-00', 'country'),]
        },
        'dataset-2': {
            'mandatory':[('property-2', 'name'), ('property-23', ""), ('property-30', "")],
            'optional': []
        },
        'dataset-3': {
            'mandatory':[('property-3', 'name'), ('property-36', ""), ('property-33', "")],
            'optional': []
        }
    }

info_2 = {
        'http://risis.eu/dataset/grid_20180625': {
            'mandatory':[
                ('http://www.w3.org/2004/02/skos/core#altLabel', ''),
                ('http://www.w3.org/2000/01/rdf-schema#label', "name"),
                ('<http://www.grid.ac/ontology/hasAddress>/<http://www.grid.ac/ontology/countryCode>', '')],
            'optional': []
        },
        'http://risis.eu/dataset/orgref_20180301': {
            'mandatory':[
                ('http://risis.eu/orgref_20180301/ontology/predicate/Name', 'name'),
                ('http://risis.eu/orgref_20180301/ontology/predicate/Country', "")],
            'optional': []
        },
        # 'dataset-3': {
        #     'mandatory':[('property-3', 'name'), ('property-36', ""), ('property-33', "")],
        #     'optional': []
        # }
    }

rscs= ['http://risis.eu/orgref_20180301/resource/10039929',
       'http://risis.eu/orgref_20180301/resource/13967334',
       'http://www.grid.ac/institutes/grid.1001.0', 'http://www.grid.ac/institutes/grid.413314.0']
test(info_2, rscs)
