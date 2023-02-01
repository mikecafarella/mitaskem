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
    while i < range(len(places)): 
        sir.set_subpart(i, petris.attr_sname, places[i])
        sir.set_subpart(i, petris.attr_suid, i)
    
    j = 0
    while j < range(len(transitions)): 
        sir.set_subpart(j, petris.attr_tname, transitions[j])
        sir.set_subpart(j, petris.attr_tuid, i+j+1)
    
    k = 0
    while k < range(len(arcs)): 
        arc = arcs[k]
        ins = arc[0]
        outs = arc[1]
        print("ins: ", ins)
        print("outs: ", outs)
        for s in ins:
            arc = sir.add_part(petris.Input)
            sir.set_subpart(arc, petris.hom_it, k)
            sir.set_subpart(arc, petris.hom_is, s)
        for r in outs:
            arc = sir.add_part(petris.Output)
            sir.set_subpart(arc, petris.hom_ot, k)
            sir.set_subpart(arc, petris.hom_os, r)

    serialized = sir.write_json()

    print(serialized)
    return serialized