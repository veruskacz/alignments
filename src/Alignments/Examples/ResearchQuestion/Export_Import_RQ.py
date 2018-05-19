import Alignments.UserActivities.Import_Data as Imp


rq1 = "http://risis.eu/activity/idea_3944ec"
rq_folder = "C:\Productivity\ZipTest\Zip"
# download_research_question_link_Stats("http://risis.eu/activity/idea_3944ec", "C:\Productivity\RQT2", activated=True)
# download_research_question("http://risis.eu/activity/idea_3944ec", "C:\Productivity\RQT")
# download_research_question("http://risis.eu/activity/idea_da1b1e", "C:\Users\Al\Documents\Tobias\\nano")
# "http://risis.eu/activity/idea_a5791d"


""" OUTPUT EXAMPLE
2. GET ALL LINKSETS CREATED FROM AN ALIGNMENT MAPPING
PREFIX ls:<http://risis.eu/linkset/>
There are 21 linksets
    LINKSET      1/21      497 triples in ls:h2020_leidenRanking_2015_approxStrSim_Organization_name_N247890402
    LINKSET      2/21      186 triples in ls:h2020_h2020_approxStrSim_Organization_name_N529851809
    LINKSET      3/21      718 triples in ls:h2020_eter_2014_approxStrSim_Organization_name_P1029719164
    LINKSET      4/21       61 triples in ls:eter_2014_eter_2014_approxStrSim_University_Institution_Name_P98241885
    ...
    LINKSET     20/21     2358 triples in ls:grid_20170712_h2020_approxStrSim_Organization_label_N1087999532

3. GET ALL LENSES CREATED FROM AN ALIGNMENT MAPPING
PREFIX lens:<http://risis.eu/linkset/>
 There are 1 lenses
    LENS         1/1    68145 triples : lens:union_E..._P1768695787
"""
# description = Imp.get_research_question_link_stats(rq1, rq_folder, activated=False)

"""EXPORT THE RESEARCH QUESTION TO rq_folder"""
# Imp.export_research_question(rq1, rq_folder, activated=True)

"""LOAD THE RESEARCH QUESTION TO THE STARDOG TRIPLE STORE"""
path_to_zip_file = "C:\Productivity\ZipTest\idea_3944ec.zip"
# Imp.import_research_question(path_to_zip_file, load=False, activated=True)

"""ANOTHER WAY TO CONTROL THE LOAD"""
# Imp.load_rq_from_batch("", "C:\Productivity\ZipTest\idea_3944ec.zip")

# print Imp.generate_win_bat_for_rq("C:\Productivity\idea_3944ec\idea_3944ec")
# import zipfile
# zip_ref = zipfile.ZipFile(path_to_zip_file, 'r')
# zip_ref.extractall("C:\Productivity\Zip")
# zip_ref.close()
