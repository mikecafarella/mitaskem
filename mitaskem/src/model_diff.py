def transisiton_diff(a, b):
  a = [f'{x[0]}-{x[1][1:]}' for x in a]
  b = [f'{x[0]}-{x[1][1:]}' for x in b]

  return set(a).difference(set(b)), set(b).difference(set(a))

if __name__ == '__main__':
  a = [["S"," I"],["I"," D"],["D"," A"],["A"," R"],["R"," T"],["T"," H"],["H"," E"],["E"," S"]]

  b = [["S"," I"],["I"," D"],["D"," A"],["A"," R"],["R"," T"],["T"," H"],["H"," E"],["S"," D"],["S"," A"],["S"," R"],["I"," A"],["I"," R"],["D"," T"],["A"," T"],["R"," H"],["T"," E"]]
  
  print(transisiton_diff(a, b))