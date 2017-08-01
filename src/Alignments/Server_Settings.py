import os
import Alignments.Settings as St

# UPLOAD_FOLDER = os.getcwd()
SEP = os.path.sep
DIR = "{0}{1}{1}Alignments{1}{1}Data".format(os.getcwd(), SEP)
UPLOAD_FOLDER = "{0}{1}{1}UploadedFiles".format(os.getcwd(), SEP)
UPLOAD_ARCHIVE = "{0}{1}{1}UploadedArchive".format(os.getcwd(), SEP)
# "http://stardog.risis.d2s.labs.vu.nl/annex/risis/sparql/query"
DATABASE = "risis"
TEST_SERVER = "localhost:5820"
PRODUCTION_SERVER = "stardog.risis.d2s.labs.vu.nl"

STARDOG_PATH_PRODUCTION = '/scratch/risis/data/stardog/stardog-5.0/stardog-5.0/bin/'
STARDOG_PATH_TEST_V = '/Applications/stardog-4.2.3/bin/'
STARDOG_PATH_TEST_A = '...'

settings = {

    # TRUE MEANS THE PYTHON SERVER AND THE STARDOG
    # SERVER ARE NOT ON THE SAME LOCAL HOST
    # St.split_sys: True,
    St.split_sys: False,

    # STARDOG LOCAL HOST NAME
    # St.stardog_host_name: TEST_SERVER,
    St.stardog_host_name: PRODUCTION_SERVER,

    # STARDOG PATH
    St.stardog_path: STARDOG_PATH_PRODUCTION,
    # St.stardog_path: STARDOG_PATH_TEST_V,
    # St.stardog_path: STARDOG_PATH_TEST_A,

    # St.stardog_version: "COMPATIBLE",
    St.stardog_version: "NOT COMPATIBLE",

    # MAIN DATA FOLDER
    St.data_dir: DIR,

    # LINKSET FOLDER
    St.linkset_dir: '{0}{1}{1}Linkset'.format(DIR, SEP),
    St.linkset_Exact_dir: '{0}{1}{1}Linkset{1}{1}Exact'.format(DIR, SEP),
    St.linkset_Subset_dir: '{0}{1}{1}Linkset{1}{1}Subset'.format(DIR, SEP),
    St.linkset_Approx_dir: '{0}{1}{1}Linkset{1}{1}Approx'.format(DIR, SEP),
    St.linkset_Emb_dir: '{0}{1}{1}Linkset{1}{1}Embedded'.format(DIR, SEP),
    St.linkset_ID_dir: '{0}{1}{1}Linkset{1}{1}Identifier'.format(DIR, SEP),
    St.linkset_Refined_dir: '{0}{1}{1}Linkset{1}{1}Refined'.format(DIR, SEP),

    # LENS FOLDER
    St.lens_dir: '{0}{1}{1}Lens'.format(DIR, SEP),
    St.lens_Diff_dir: '{0}{1}{1}Lens{1}{1}Diff'.format(DIR, SEP),
    St.lens_transitive__dir: '{0}{1}{1}Lens{1}{1}Transitive'.format(DIR, SEP),
    St.lens_Union__dir: '{0}{1}{1}Lens{1}{1}Union'.format(DIR, SEP),

    # FOLDER FOR DATASET FILES UPLOADED FOR  CONVERSION
    St.uploaded_dataset_dir: '{0}{1}{1}Dataset'.format(DIR, SEP),

    # UPLOADED ALIGNMENTS
    St.uploaded_alignments: '{0}{1}{1}Alignments'.format(DIR, SEP),
}


# print DIR
