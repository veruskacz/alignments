from Alignments.Manage.AdminGraphs import drop_linkset

""" EXECUTE LINKSET SPECIFICATIONS """
# to_delete = "http://risis.eu/linkset/grid_20170522_orgref10_exactStrSim_label_P1517853875"
to_delete = "http://risis.eu/linkset/refined_en_nl_exactStrSim_label_P916744941_intermediate_author_name"
drop_linkset(to_delete, display=False, activated=True)
