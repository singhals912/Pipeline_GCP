import os
import io
from io import BytesIO
from transformers.pipelines import pipeline

hg_BERT = pipeline('question-answering', model="distilbert-base-uncased-distilled-squad",
                   tokenizer="distilbert-base-uncased-distilled-squad")
from google.cloud import storage
import pandas as pd

storage_client = storage.Client()
bucket = storage_client.get_bucket('mgmt-590-class')

files = bucket.list_blobs()
fileList = [file.name for file in files if '.' in file.name]

answer_li = []
df_final = pd.DataFrame()
df_new = pd.DataFrame()
for i in fileList:
    # print(i)
    blop = bucket.blob(i)
    data = blop.download_as_string()
    df = pd.read_csv(io.BytesIO(data), encoding='utf-8', sep=',')
    df_final = df_final.append(df, ignore_index=True)
    for i, row in df.iterrows():
        context = row['context']
        question = row['question']
        answer = hg_BERT({'question': question, 'context': context})['answer']
        answer_li.append(answer)
# print(answer_li)
df_new['context'] = df_final['context']
df_new['question'] = df_final['question']
df_new['answer'] = answer_li
