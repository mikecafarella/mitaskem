import sys
import gpt3 as gpt

# targets = ['population', 'infectious time']
# terms = ['population', 'doubling time', 'recovery time', 'infectious time']
#
# parameters = set()
# var_dict = {}
# for nop in nops:
#     if nop[1] is not None:
#         parameters.add(nop[0])
#         var_dict[nop[0]] = nop
# #         print((nop))
# discoveredParameterConnections = gpt.match_gromet_targets(targets, list(parameters), var_dict, terms)
# print(discoveredParameterConnections)
import os
import requests



def get_mml(image_path: str) -> str:
    with open(image_path, 'rb') as f:
        r = requests.put("http://127.0.0.1:8000/get_mml", files = {"file": f})
    return r.text

# Convert formula into MathML representation with image2MathML translator
def parse_model_formula(model_path: str):
    mml = os.path.join(model_path, 'mml.txt')
    model = model_path.split("/")[-1]
    fw = open(mml, "w")
    for filename in os.listdir(model_path):
        idx = filename.split(".")[0]
        image_path = os.path.join(model_path, filename)
        # checking if it is a png file
        if os.path.isfile(image_path) and image_path.endswith(".png"):
            print(image_path)
            with open(image_path, 'rb') as f:
                r = requests.put("http://127.0.0.1:8000/get_mml", files={"file": f})
            fw.write("{}\t{}\n".format(idx, r.text))

    fw.close()


# parse_model_formula("images/SVIIvR/")
# mml = get_mml("images/10.png")
# print(mml)
# index_text("./model/CHIME_SIR_while_loop.py")