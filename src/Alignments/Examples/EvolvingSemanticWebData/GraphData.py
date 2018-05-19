import Alignments.Query as Qr


test_v1 = """
PREFIX risis:<http://risis.eu/>
PREFIX predicate:<http://risis.eu/predicate/>
{} DATA
{{
  GRAPH  <http://risis.eu/dataset/Test.v1>
  {{
    risis:France            predicate:capital       "Paris" .
    risis:France            predicate:population    "65186215" .
    risis:France            predicate:size          "643801" .

    # ADDED WITH THE WRONG AREA VALUE
    risis:Benin             predicate:cpital        "Cotonou" .
    risis:Benin             predicate:size          "115000" .
    risis:Benin             predicate:population    "11400000" .
    risis:Benin             predicate:population    "11400002" .

    risis:A             predicate:shoeS   2 .
    risis:A             predicate:car   2 .

  }}
}}""".format("INSERT") # DELETE



test_v2 = """
PREFIX risis:<http://risis.eu/>
PREFIX predicate:<http://risis.eu/predicate/>
{} DATA
{{
  GRAPH  <http://risis.eu/dataset/Test.v2>
  {{
    # 1. REMOVED
    # risis:France          predicate:capital       "Paris" .
    # risis:France          predicate:population    "65186215" .
    # risis:France          predicate:size          "643801" .

    # 2. NEW RESOURCE ADDED
    risis:The_Netherlands   predicate:capital       "Amsterdam" .
    risis:The_Netherlands   predicate:population    "17075440" .

    # 3. NEW RESOURCE AND NEW PROPERTY ADDED
    risis:Israel            predicate:religion      "Jewish" .

    # # 4. MODIFIED WITH THE RIGHT AREA VALUE
    # # difficult to automate that both the property and the value got modified
    risis:Benin             predicate:capital        "Cotonou" .
    risis:Benin             predicate:size_kmSquare "114763" .
    risis:Benin             predicate:population    "11427538" .
    risis:Benin             predicate:population    "11400003" .

    risis:A             predicate:shoe   2 .
    risis:A             predicate:car   2 .
  }}
}}""".format("INSERT")


def reload():
    Qr.endpoint("DROP SILENT GRAPH <http://risis.eu/dataset/Test.v1>")
    Qr.endpoint("DROP SILENT GRAPH <http://risis.eu/dataset/Test.v2>")
    Qr.endpoint(test_v1)
    Qr.endpoint(test_v2)
