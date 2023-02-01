## JSON format used for producing annotated equation variables

```
[
    {
        "type" : "variable", 
        "name": "S", 
        "id" : "v123"
        "text_annotations": ["susceptible", "people that are susceptible"],
        "dkg_annotations" : ["id123", "id456"]
    }, 
    ...
    { 
        "type" : "equation", 
        "latex" : "\alphaS = \beta",
        "id" : "e456", 
        "matches" : {"S":["v123"], ...}
    },
    ...
]
```