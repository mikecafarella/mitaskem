# mitaskem

This project includes MIT efforts to integrate the GroMet workflow, enable annotation and interact with XDD APIs. The project provides a simple tool and necessary test files for ASKEM TA1 MIT group workflow test.
The tool supports gromet extraction from a python program, put and get operation of json object interacting with XDD, annotation gromet represention with lineage tracing. Please refer to usage by  



        python mitlink.py -h


1. Python code to gromet representation: mitlink takes python file as input (arg0) and generates gromet representation.



        python mitlink.py -i model/x1.py 


    

        

2. Upload object in XDD: mitlink takes gromet file as input and uploads the corresponding object to XDD and return XDD key. 



        python mitlink.py  -p x1--Gromet-FN-auto.json 



        
        


3. Get XDD object with a given key: mitlink takes UUID as a input key, gets the object from XDD, and save it to the local _model_ folder with file name rule _UUID---Gromet-FN-auto.json_.



        python mitlink.py  -g b3669d32-d422-49c7-ad0b-becf1e2bc0b0



        
        


4. Annotate the gromet representation and update with lineage information: mitlink check the local directory for gromet file corresponding to target _key_, 
then apply annotation with given _attribute_ and _value_ and generates a new version of gromet file. 
The tool automatically adds the source key for lineage tracking and upload to XDD. 
The tool pulls the target object with _key_ from XDD, if the local directory does contain this file. 



        python mitlink.py  -a b3669d32-d422-49c7-ad0b-becf1e2bc0b0 attibute value



        
        


