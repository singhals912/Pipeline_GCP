from google.cloud import storage
import os
import pandas as pd
from transformers import pipeline
from io import StringIO


#Creating a Google Cloud Storage (GCS) Client
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "assignmenttwo-315021-b4e55c23dce8.json"
models = {}
client = storage.Client()
bucket = client.get_bucket('mgmt-590-class')
blobs = bucket.list_blobs()
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

def main():
    df_list = []
    # #Then do other things

    for blob in blobs:
        str_test = str(blob.download_as_string(), "utf-8")
        data = StringIO(str_test)
        df_test = pd.read_csv(data)
        print(df_test)
        df_answers = question_answer(df_test)
        print(df_answers)
        df_list.append(df_answers)
    return df_list

def delete_one_file(filename):
    try:
        blob = bucket.blob(filename)
        blob.delete()
    except Exception as ex:
        print("Exception occurred while trying to delete files ",ex)
        raise ex


if __name__ == "__main__":
    main()
