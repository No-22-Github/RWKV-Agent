"""Manual labels for the stratified review sample (seed 20261010, 120 closed T-workbank steps).
Codes: P plan, R result-driven, S shallow restate+act, E empty/recite; flags: X action!=think,
W reasoning/fact error (incl. nonexistent tool/path), A think promises change but repeats same action.
Index i refers to the i-th item of the sample built in analyze_think.review_sample().
"""
LABELS = {}
def add(batch):
    LABELS.update(batch)
add({0:"R",1:"R+X",2:"R+X",3:"P",4:"R",5:"S",6:"R",7:"P",8:"R",9:"S",10:"R+X",11:"R",12:"R",13:"R",14:"P",
     15:"R",16:"R+W",17:"E",18:"R",19:"P",20:"R+X",21:"R",22:"S+W",23:"R",24:"S",25:"R+X",26:"P",27:"R",
     28:"E",29:"R"})
add({30:"R+W",31:"S",32:"R",33:"R",34:"S",35:"R",36:"S",37:"P",38:"R+X",39:"P",40:"P",41:"R",42:"R",43:"R",
     44:"R",45:"S+W+X",46:"R",47:"R",48:"R+X",49:"R",50:"R",51:"R+W",52:"P+W",53:"R+W",54:"E",55:"R",56:"R+W",
     57:"S",58:"R+X",59:"E+W"})
add({60:"R",61:"R",62:"R",63:"R+W",64:"R",65:"R",66:"R",67:"P",68:"S",69:"R",70:"R",71:"S",72:"R+X",73:"R",
     74:"R",75:"S",76:"R",77:"R",78:"R",79:"R",80:"R",81:"R+X",82:"R",83:"P",84:"R+X",85:"S",86:"R",87:"S",
     88:"R+W",89:"R+X"})
add({90:"R",91:"R",92:"E",93:"R",94:"R+X",95:"R",96:"R",97:"P",98:"R+X",99:"R",100:"S",101:"R+W",102:"S",103:"P",
     104:"S",105:"R",106:"R+X",107:"E+W",108:"P",109:"R",110:"P",111:"E",112:"S",113:"S",114:"S+W",115:"S",116:"R",
     117:"R+X",118:"R+X",119:"R+X"})
assert len(LABELS) == 120

# Failed T case-runs (k0/k1 workbank) in which the think states the correct answer. Auto string-match flagged 33
# case-runs; after reading each one, these 21 are genuine (others were incidental token matches such as dates/digits).
# F: correct value also reached the final output but the answer contract (bare value / relative path / no tool) failed
# G: correct value in think, final lost to protocol/harness failure (unclosed think, JSON decode, loop, contract wrapper)
# H: correct value in think, but the action/tool result overrode it and the final was wrong
RIGHT_IN_THINK = {
    "F": [("k0", "code-0009"), ("k0", "fs-0002"), ("k0", "fs-0010"), ("k0", "nt-0002"), ("k1", "nt-0002"),
          ("k0", "web-0014"), ("k1", "web-0014"), ("k0", "web-0016"), ("k1", "cfg-0001"), ("k1", "doc-0005"),
          ("k1", "web-0013"), ("k1", "nt-0005"), ("k1", "nt-0006"), ("k1", "nt-0010")],
    "G": [("k0", "tab-0010"), ("k1", "doc-0002"), ("k0", "nt-0008"), ("k0", "nt-0005")],
    "H": [("k0", "tab-0019"), ("k0", "nt-0009"), ("k1", "nt-0009")],
}

# Wins of T over A (case passed in T, failed in A of the same replicate) and a manual verdict on whether the think
# plausibly caused the win. C = think causal, F = format/contract luck, L = lucky abstention/answer, N = not think-related
WINS = {
    ("k0", "code-0005"): "F", ("k0", "doc-0001"): "C", ("k0", "doc-0005"): "C", ("k0", "fs-0001"): "C",
    ("k0", "fs-0012"): "L", ("k0", "log-0017"): "C", ("k0", "nt-0006"): "F", ("k0", "web-0009"): "C",
    ("k1", "cfg-0012"): "L", ("k1", "doc-0001"): "C", ("k1", "fs-0001"): "C", ("k1", "log-0017"): "C",
    ("k1", "nt-0007"): "F", ("k1", "nt-0008"): "F", ("k1", "tab-0010"): "C",
}

# 24 closed, non-degenerate think steps from A-workbank-k0/k1 (random.seed(8), see analyze_think.review_sample_A)
A_LABELS = {0:"E",1:"S",2:"P",3:"S",4:"S",5:"E+X+W",6:"P",7:"S",8:"S",9:"P",10:"P",11:"E+W",12:"P",13:"P",14:"S",
            15:"E+W",16:"E+W",17:"S",18:"P",19:"E+W",20:"P",21:"S",22:"P",23:"S+W"}
