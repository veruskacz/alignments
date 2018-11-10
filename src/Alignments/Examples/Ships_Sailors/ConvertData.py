import Alignments.Utility as Ut
from os.path import join


def load_data(data_path, save_in):

    count_record = 0
    clusters = {}
    base = "http://voc.nl/people/"

    # READING THE CLUSTER FILE
    with open(data_path, "rb") as data:

        for record in data:

            count_record += 1
            print "\r\t\t>>>", count_record,
            features = record.split(";")

            if len(features) > 0:

                if features[1] not in clusters:
                    clusters[features[1]] = {"nodes": ["<{}{}>".format(base, features[2])]}
                else:
                    clusters[features[1]]["nodes"] += ["<{}{}>".format(base, features[2])]

            # if count_record == 5:
            #     break

    freq = {}
    for key, val in clusters.items():

        clusters[key]["links"] = Ut.ordered_combinations(val["nodes"])

        strengths = {}
        for link in clusters[key]["links"]:
            link_key = Ut.get_key(link[0], link[1])
            strengths[link_key] = 1
        clusters[key]["strengths"] = strengths

        size = str(len(val["nodes"]))
        if size not in freq:
            freq[size] = 1
        else:
            freq[size] += 1

    print "SERIALIZING THE DICTIONARY"
    serialize_dict(save_in, clusters, cluster_limit=1000)

    print "JOB DONE!!!"
    # Ut.print_dict(freq)
    # Ut.print_dict(clusters)


def serialize_dict(directory, dictionary, cluster_limit=1000):

    with open(join(directory, "{}.txt".format(hash(directory))), 'wb') as writer:

        counting = 0
        sub_cluster = {}

        for key, value in dictionary.items():
            counting += 1
            sub_cluster[key] = value

            if counting == cluster_limit:
                writer.write(sub_cluster.__str__() + "\n")
                sub_cluster = {}
                counting = 0

        if counting != 0:
            writer.write(sub_cluster.__str__() + "\n")

load_data("C:\Users\Al\Dropbox\@VU\Ve\Golden Agents\ShipsAndSailors\\clusters.csv",
          save_in="C:\Users\Al\Dropbox\@VU\Ve\Golden Agents\ShipsAndSailors")

