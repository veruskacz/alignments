import os
import Settings as St


SEP = os.path.sep
DIR = "{0}{1}{1}Alignments{1}{1}Data".format(os.getcwd(), SEP)
# UPLOAD_FOLDER = "{0}{1}{1}UploadedFiles".format(os.getcwd(), SEP)
UPLOAD_FOLDER = os.getcwd()
settings = {

    # STARDOG LOCAL HOST NAME
    St.stardog_host_name: "localhost:5820",

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