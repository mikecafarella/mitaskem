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
        "id" : "e456"
    },
    ...
    {
        "type" : "symbol",
        "latex" : "S",
        "id" : "s789",
        "origin" : "e456",
        "matches" : ["v123"]
    },
    ...
]
```