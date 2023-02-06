import argparse 
import os
import xlsxwriter


def main(args):

    out_filename = args.dir + "/" + "params.xlsx"
    wb = xlsxwriter.Workbook(out_filename)
    ws = wb.add_worksheet()
    bold = wb.add_format({'bold': True})

    col_headers = 	["doc",	"type",	"text", "arg_name_1","arg_val_1","arg_name_2","arg_val_2","arg_name_3","arg_val_3","arg_name_4","arg_val_4"]

    for col, item in enumerate(col_headers):
        ws.write(0, col+1, item, bold)
    
    row = 1
 
    for filename in os.listdir(args.dir):
        filepath = os.path.join(args.dir, filename)

        with open(filepath, "r") as fi:
            for line in fi:
                if line == "None":
                    continue

                
                toks = line.split(" ")

                

                # Write ID, doc, type, text
                ws.write(row, 0, row - 1, bold)
                ws.write(row, 1, "extractions_documents_" + filename.split("_")[0] + "--COSMOS-data.json")
                ws.write(row, 2, "ParameterSetting")
                ws.write(row, 3, line)

                # Write the rest
                ws.write(row, 4, "value")
                ws.write(row, 5, toks[0])
                ws.write(row, 6, "variable")
                ws.write(row, 7, ' '.join(toks[i] for i in range(1, len(toks))))

                row += 1
    
    wb.close()

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dir", type=str)
    args = parser.parse_args()

    main(args)