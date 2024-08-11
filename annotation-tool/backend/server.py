from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from pydantic import BaseModel
import joblib

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Load the CSV file
CURRENT_EXP = "COREX_KEYWORD"
df = pd.read_csv("ethnic_dataset_exp0_5342.csv").reset_index(drop=True)
if CURRENT_EXP=="Initial": grouped_docs = joblib.load("grouped_docs_110724.joblib")
elif CURRENT_EXP=="COREX_KEYWORD": grouped_docs = joblib.load("docs_per_topic_28July.joblib")

# Placeholder for annotations
annotations = pd.DataFrame(columns=['id', 'isEthnic', 'reason'])

class Annotation(BaseModel):
    id: int
    isEthnic: bool
    reason: str
class NewAnnotation(BaseModel):
    id: int
    classification: str

class AnnotationsRequest(BaseModel):
    annotations: list[NewAnnotation]

@app.get("/articles/{article_id}")
async def get_article(article_id: int):
    print(article_id)
    try:
        article = df.iloc[article_id]
    except IndexError:
        raise HTTPException(status_code=404, detail="Article not found")
    return {"article": {"id": article_id, "content": article['content']}}

@app.post("/annotate/")
async def annotate(annotation: Annotation):
    global annotations
    new_row = pd.DataFrame([annotation.dict()])
    annotations = pd.concat([annotations, new_row], ignore_index=True)
    annotations.to_csv("ethnic_dataset_exp0_5342_annotated.csv")
    return {"message": "Annotation saved"}

@app.get("/articles/topic/{topic_id}")
async def get_article(topic_id: int):
    try:
        articles = grouped_docs[topic_id]
    except IndexError:
        raise HTTPException(status_code=404, detail="Article not found")
    return {"article": {"id": topic_id, "content": articles}}

@app.post("/submit_annotations")
async def submit_annotations(request: AnnotationsRequest):
    annotations_data = []
    for annotation in request.annotations:
        annotations_data.append({
            "id": annotation.id,
            "classification": annotation.classification
        })

    annotations_df = pd.DataFrame(annotations_data)
    annotations_df.to_csv("ethnic_dataset_exp0_5342_annotated.csv", index=False)
    return {"message": "Annotations submitted successfully"}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000)

