from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from file_cache import init_cache_directory
from routers import code_dataset, code_formula, code_text, avail_check, petri, evaluation, annotation, integration, cards, debugging

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
    },
    {
        "name": "TA1-Integration",
        "description": "Integate Arizona's output with the MIT extraction pipeline."
    },
    {
        "name": "Data-and-model-cards",
        "description": "Requests related to generating data and model cards.",
    },
    {
        "name": "Debugging",
        "description": "Version check and debugging requests."
    },
    {
        "name": "Evaluation",
        "description": "Evaluating the MIT extraction services."
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
app.include_router(integration.router, prefix="/integration")
app.include_router(cards.router, prefix="/cards")
app.include_router(debugging.router, prefix="/debugging")
app.include_router(evaluation.router, prefix="/evaluation")


