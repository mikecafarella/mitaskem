from . import acsets, petris
import ast


def convert_to_pyacset(places_s, transitions_s, arcs_s):

    places = ast.literal_eval(places_s)
    transitions =ast.literal_eval(transitions_s)
    arcs = ast.literal_eval(arcs_s)

    sir = petris.Petri()
    sir.add_species(len(places))
    trans = petris.Transition
    sir.add_parts(trans, len(transitions))

    i = 0
    node_dict = {}
    while i < len(places): 
        sir.set_subpart(i, petris.attr_sname, places[i].strip())
        sir.set_subpart(i, petris.attr_suid, i+1)
        node_dict[places[i].strip()] = i
        i += 1
    
    j = 0
    while j < len(transitions): 
        sir.set_subpart(j, petris.attr_tname, transitions[j].strip())
        sir.set_subpart(j, petris.attr_tuid, i+j+1)
        node_dict[transitions[j].strip()] = i+j
        j += 1
    
    k = 0
    while k < len(arcs): 
        arc = arcs[k]
        print(arc)
        print(node_dict)
        
        print("ins: ", arc[0])
        print("outs: ", arc[1])
        pt1 = sir.add_part(petris.Input)
        sir.set_subpart(pt1, petris.hom_it, k)
        sir.set_subpart(pt1, petris.hom_is, node_dict[arc[0].strip()])
        pt2 = sir.add_part(petris.Output)
        sir.set_subpart(pt2, petris.hom_ot, k)
        sir.set_subpart(pt2, petris.hom_os, node_dict[arc[1].strip()])
        k += 1

    serialized = sir.write_json()

    print(serialized)
    return serialized

if __name__=="__main__":
    places_str = '["S"," I"," D"," A"," R"," T"," H"," E"]'
    transitions_str = '["alpha"," beta"," gamma"," delta"," epsilon"," mu"," zeta"," lamda"," eta"," rho"," theta"," kappa"," nu"," xi"," sigma"," tau"]'
    arcs_str = '[["S"," I"],["I"," D"],["I"," A"],["I"," R"],["D"," E"],["A"," R"],["A"," T"],["R"," H"],["T"," H"],["I"," H"],["D"," H"],["A"," H"],["R"," H"],["T"," E"],["alpha", "S"]]'

    convert_to_pyacset(places_str, transitions_str, arcs_str)