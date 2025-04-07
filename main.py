from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.endpoint import (
    azure_blob_storage,
    bill_of_lading_inventory_comparison,
    chatbot,
    image_comparison,
    invoice_analysis,
    prompts,
    shipping_document_review,
haz_waste_analysis,
)

app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.add_middleware(CORSMiddleware,
                   allow_origins=["*"],
                   allow_credentials=True,
                   allow_methods=["*"],
                   allow_headers=["*"])

app.include_router(invoice_analysis.router)
app.include_router(prompts.router)
app.include_router(image_comparison.router)
app.include_router(shipping_document_review.router)
app.include_router(bill_of_lading_inventory_comparison.router)
app.include_router(azure_blob_storage.router)
app.include_router(haz_waste_analysis.router)

app.include_router(chatbot.router)


@app.get("/")
def read_root():
    return {"message": "Fast API Server is Running!!."}
