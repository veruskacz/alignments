import Alignments.Examples.LinkValidation.Data as Data
import Alignments.UserActivities.Plots as Plt
import Alignments.Examples.LinkValidation.Functions as Functions
from os.path import join
import cStringIO as Buffer
import Alignments.UserActivities.Import_Data as Im


open_aire_dir = "C:\Productivity\LinkAnalysis\D2SOpenAire\{}"
greater_equal = False



"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# IMPORT RESEARCH QUESTION METADATA AND ALIGNMENTS                                      #
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

Im.download_research_question_link_Stats("http://risis.eu/activity/idea_3944ec", "C:\Productivity\RQT", activated=False)
Im.download_research_question_link_Stats("http://risis.eu/activity/idea_a5791d", "C:\Productivity\RQT", activated=False)


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# PLOT FOR OPENAIRE DATATHON EMBEDDED LINKS
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
net_size = 3
net_max_size = 11
embedded_dir = open_aire_dir.format("Embedded_True")
embedded_linkset = "subset_openAire_20180219_openAire_20180219_embededAlignment_OrganizationEntity_sameAs_N2115119541"
embedded_linkset = "http://risis.eu/linkset/{}".format(embedded_linkset)
Plt.cluster_d_test(embedded_linkset, network_size=net_size,  network_size_max=net_max_size,
                   targets=Data.targets_openaire, constraint_targets=None, constraint_text=None,
                   directory=embedded_dir, greater_equal=greater_equal, limit=None, only_good=True, activated=True)


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# PLOT FOR OPENAIRE DATATHON
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
open_aire_dir = "C:\Productivity\LinkAnalysis\D2SOpenAire\Cluster"
open_aire_cluster = "clustered_exactStrSim_N1245386587321660737"
cluster = "http://risis.eu/linkset/{}".format(open_aire_cluster)

open_aire_lens_dir = "C:\Productivity\LinkAnalysis\D2SOpenAire\Lens"
open_aire_lens = "union_Grid_20170712_H2020_Orgref_20170703_OpenAire_20180219_N2036353171593472993"
lens = "http://risis.eu/lens/{}".format(open_aire_lens)
for i in range(3, 0):
    print "\nITERATION {}".format(i)
    Plt.cluster_d_test(cluster, network_size=i,  targets=Data.targets_openaire,
                       directory=open_aire_dir, greater_equal=greater_equal, limit=None, activated=False)


print "STATS"
sheet_builder = Buffer.StringIO()
for i in range(3, 0):
    print "\nITERATION {}".format(i)
    text = Plt.cluster_d_test_stats(embedded_linkset, network_size=i,  targets=Data.targets,
                                    directory=None, greater_equal=greater_equal, limit=None, activated=True)
    sheet_builder.write("{}\n".format(text))