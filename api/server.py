from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from file_cache import init_cache_directory
from routers import code_dataset, code_formula, code_text, avail_check, petri, annotation

tags_metadata = [
    # {
    #     "name": "Debugging",
    #     "description": "Use the following request to test availability.",
    # },
    # {
    #     "name": "Code-to-format",
    #     "description": "Requests for mapping code to data in different formats.",
    # },
    {
        "name": "Code-2-Petri-net",
        "description": "Requests related to extracting Petri net elements from code."
    }, 
    {
        "name": "Paper-2-annotated-vars",
        "description": "Requests related to annotating LaTeX formulas with paper text and grounding them to the DKG/to dataset columns."
    }
]


def build_api(*args) -> FastAPI:

    api = FastAPI(
        title="Annotation API",
        description="MIT annotation API",
        docs_url="/",
        version="0.0.15",
        openapi_tags=tags_metadata
    )
    origins = [
        "http://localhost",
        "http://localhost:8080",
    ]
    api.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @api.on_event("startup")
    async def startup_event():
        init_cache_directory("/tmp/askem")

    return api

app = build_api()

#app.include_router(code_dataset.router, prefix="/code_dataset")
#app.include_router(code_formula.router, prefix="/code_formula")
#app.include_router(code_text.router, prefix="/code_text")
#app.include_router(avail_check.router, prefix="/avail_check")
app.include_router(petri.router, prefix="/petri")
app.include_router(annotation.router, prefix="/annotation")

