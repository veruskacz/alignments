from Alignments.Manage.AdminGraphs import drop_linkset

""" EXECUTE LINKSET SPECIFICATIONS """
# to_delete = "http://risis.eu/linkset/grid_20170522_orgref10_exactStrSim_label_P1517853875"
# to_delete = "http://risis.eu/linkset/refined_en_nl_exactStrSim_label_P916744941_intermediate_author_name"
# to_delete = "http://risis.eu/linkset/en_nl_intermediate_author_name_N36817389"
to_delete = "http://risis.eu/linkset/en_nl_exactStrSim_name_N467336337"
drop_linkset(to_delete, display=False, activated=True)

"""
PREFIX linkset:     <http://risis.eu/linkset/>
PREFIX activity:    <http://risis.eu/activity/>
delete data
{
    GRAPH activity:idea_2e6b7c
    {
        activity:idea_algmt_222eea
            alivocab:created        linkset:en_nl_intermediate_author_label_P1605654795 .
    }
}
"""

