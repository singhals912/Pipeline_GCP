from google.cloud import storage
import os
import pandas as pd
from transformers import pipeline
#Creating a Google Cloud Storage (GCS) Client
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials.json"
client = storage.Client()
bucket = client.get_bucket('mgmt-590-class')
models = {}
# Initialize our default model
models = {
    "default": "distilled-bert",
    "models": [
        {
            "name": "distilled-bert",
            "tokenizer": "distilbert-base-uncased-distilled-squad",
            "model": "distilbert-base-uncased-distilled-squad",
            "pipeline": pipeline('question-answering',
                                 model="distilbert-base-uncased-distilled-squad",
                                 tokenizer="distilbert-base-uncased-distilled-squad")
        }
    ]
}
# #Then do other things
blobs = bucket.list_blobs()
def question_answer(df):
    df.columns = [df.columns[0].lower(), df.columns[1].lower(), df.columns[2].lower()]
    answers =[]
    for i in range(len(df)):
        model_Name =""
        if 'model' in df.columns:
            if pd.isna(df['model'][i]):
                model_Name = models['default']
            else:
                model_Name = df['model'][i]
        else:
            model_Name = models['default']
        for m in models['models']:
            if m['name'] == model_Name:
                hg_comp = m['pipeline']
        answer = hg_comp({'question': df['question'][i], 'context': df['context'][i]})['answer']
        answers.append(answer)
    df['answer'] = answers
    return df
for blob in blobs:
    blob.download_to_filename(blob.name)
    df = pd.read_csv(blob.name)
    df_answers = question_answer(df)
    print(df_answers)
