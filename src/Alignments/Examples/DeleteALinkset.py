from Alignments.Manage.AdminGraphs import drop_linkset

""" EXECUTE LINKSET SPECIFICATIONS """
to_delete = "http://risis.eu/linkset/grid_20170522_orgref10_exactStrSim_label_P1517853875"
drop_linkset(to_delete, display=False, activated=True)
