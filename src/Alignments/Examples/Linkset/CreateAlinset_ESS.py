import Alignments.Settings as St
from Alignments.Linksets.SPA_Linkset import specs_2_linkset
from Alignments.Manage.AdminGraphs import drop_linkset
###############################################################################################################
""" DEFINE LINKSET SPECIFICATIONS """
###############################################################################################################
mechanism_1 = "exactStrSim"
mechanism_2 = "identity"

# THE RESEARCH QUESTION TO WHICH THE VIEW BELONGS TO
research_uri = "http://risis.eu/activity/idea_77f81f"

###############################################################################################################
""" EXAMPLE 1: EXACT STRING SIMILARITY """
###############################################################################################################

""" PROVIDE SPECS FOR DATASETS of INTEREST """
grid = {
    St.rdf_predicate: "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
    St.graph: "http://risis.eu/dataset/grid",
    St.entity_datatype: "http://risis.eu/grid/ontology/class/Institution",
    St.aligns: "http://risis.eu/grid/ontology/predicate/name"}

eter_english = {
   St.graph: "http://risis.eu/dataset/eter",
   St.entity_datatype: "http://risis.eu/eter/ontology/class/University",
   St.aligns: "http://risis.eu/eter/ontology/predicate/english_Institution_Name"}


""" DEFINE LINKSET SPECIFICATIONS """
ls_specs_1 = {
    St.researchQ_URI: research_uri,
    St.source: eter_english,
    St.target: grid,
    St.mechanism: mechanism_1
}
""" EXECUTE LINKSET SPECIFICATIONS """
linkset_2 = specs_2_linkset(ls_specs_1, display=False, activated=True)


drop_linkset("http://risis.eu/linkset/eter_grid_exactStrSim_english_Institution_Name_N1410131292",
             display=False, activated=False)