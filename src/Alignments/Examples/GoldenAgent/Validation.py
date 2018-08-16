import Alignments.Utility as Ut

# CLUSTER ID
# CLUSTER SIZE
# MACHINE EVAL
# HUMAN EVAL
# RESOURCES


def test(data, resources):

    # data = {
    #     'dataset-1': ['property-1', 'property-10', 'property-15'],
    #     'dataset-2': ['property-2', 'property-23', 'property-30'],
    #     'dataset-3': ['property-3', 'property-36', 'property-33']
    # }

    # resource = ['resource-1', 'resource-2', 'resource-3']

    # QUERY TEMPLE EXAMPLE
    """
        SELECT *
    {
        # LIST OR RESOURCES TO INVESTIGATE
        VALUES ?resource { resource-1 resource-2 resource-3 }

        GRAPH <dataset-2>
        {
			BIND( <dataset-2> as ?dataset-2)
			?resource <property-2> ?dataset-2_property-2 .
			?resource <property-23> ?dataset-2_property-23 .
			?resource <property-30> ?dataset-2_property-30 .
        } 	UNION

        GRAPH <dataset-3>
        {
			BIND( <dataset-3> as ?dataset-3)
			?resource <property-3> ?dataset-3_property-3 .
			?resource <property-36> ?dataset-3_property-36 .
			?resource <property-33> ?dataset-3_property-33 .
        } 	UNION

        GRAPH <dataset-1>
        {
			BIND( <dataset-1> as ?dataset-1)
			?resource <property-1> ?dataset-1_property-1 .
			?resource <property-10> ?dataset-1_property-10 .
			?resource <property-15> ?dataset-1_property-15 .
        }
    }
    """

    sub_query = ""

    template_1 =     """\t{}
        GRAPH {}
        {{ \n\t\t\t{}\n{}
        }} """

    template_2 = """
    SELECT *
    {{
        # LIST OR RESOURCES TO INVESTIGATE
        VALUES ?resource {{ {} }}
        {}
    }}

    """

    resource_enumeration = " ".join(resources)

    count_union = 0
    for dataset, properties in data.items():

        sub = "\n".join(
            "\t\t\t?resource {0} ?{1}_{2} .".format(Ut.to_nt_format(item), dataset, item) for item in properties)
        bind = "BIND( {} as ?{})".format(Ut.to_nt_format(dataset), Ut.get_uri_local_name_plus(dataset))
        sub_query += template_1.format("UNION\n" if count_union > 0 else "", Ut.to_nt_format(dataset), bind, sub)
        count_union += 1

    print template_2.format(resource_enumeration, sub_query)


# TESTING
info = {
        'dataset-1': ['property-1', 'property-10', 'property-15'],
        'dataset-2': ['property-2', 'property-23', 'property-30'],
        'dataset-3': ['property-3', 'property-36', 'property-33']
    }
rscs= ['resource-1', 'resource-2', 'resource-3']
test(info, rscs)
