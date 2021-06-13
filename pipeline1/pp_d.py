from google.cloud import storage
import os
from transformers.pipelines import pipeline
import csv
import time

# creating a GCS client
client = storage.Client()

bucket = client.get_bucket('mgmt-590-class')

for filecsv in client.list_blobs('mgmt-590-class'):
    blob = bucket.blob(filecsv.name)
    blob.download_to_filename(os.path.join("/tmp",filecsv.name))
    #blob.download_to_filename(filecsv.name)
    models = {"name": "distilled-bert",
             "tokenizer": "distilbert-base-uncased-distilled-squad",
             "model": "distilbert-base-uncased-distilled-squad",
             "pipeline": pipeline('question-answering',
             model="distilbert-base-uncased-distilled-squad",
             tokenizer="distilbert-base-uncased-distilled-squad")
             }
    final_file = []
    hg_comp = models['pipeline']
    answer = []
    questions = []
    contexts = []

    with open(os.path.join("/tmp",filecsv.name), 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            context = row["context"]
            question = row["question"]
            answer.append(hg_comp({'question': question, 'context': context})['answer'])
            questions.append(question)
            contexts.append(context)
        final_file.append(questions)
        final_file.append(contexts)
        final_file.append(answer)
        print(final_file)
    timestamp = str(int(time.time()))
    try:
        with open(os.path.join("/pfs/out",filecsv.name.replace(".csv",timestamp+".csv")), 'w') as f:
            fieldnames = ['question','context','answer']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for row in zip(*final_file):
                writer.writerow({'question': row[0],'context': row[1], 'answer': row[2]})

    except:
        print("Failed created csv file with answers for "+filecsv.name)
    else:
        print("Successfully processed the file "+filecsv.name)
        print("Deleting csv file "+filecsv.name)
        blob.delete()
