import pandas as pd
import psycopg2
import os
import datetime, time
import base64

#Function to run the sql queries..
def runSqlQuery(query, params = None):
    
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :return:
    """
    
    if not os.path.exists('.ssl'):
        os.makedirs('.ssl')
         
    #Get GCS credentials 
    filecontents = os.environ.get('PG_SSLROOTCERT').replace("@","=")
    decoded_creds = base64.b64decode(filecontents)
    with open('.ssl/server-ca.pem', 'w') as f1:
        f1.write(decoded_creds.decode("utf-8"))
      
    filecontents = os.environ.get('PG_SSLCERT').replace("@","=")
    decoded_creds = base64.b64decode(filecontents)
    with open('.ssl/client-cert.pem', 'w') as f2:
        f2.write(decoded_creds.decode("utf-8"))
          
    filecontents = os.environ.get('PG_SSLKEY').replace("@","=")
    decoded_creds = base64.b64decode(filecontents)
    with open('.ssl/client-key.pem', 'w') as f3:
        f3.write(decoded_creds.decode("utf-8"))
    


    #Change unix permissions to restricted
    os.chmod(".ssl/server-ca.pem",0o600)
    os.chmod(".ssl/client-cert.pem",0o600)
    os.chmod(".ssl/client-key.pem",0o600)

    sslmode="sslmode=verify-ca"
    sslrootcert = "sslrootcert=.ssl/server-ca.pem"
    sslcert = "sslcert=.ssl/client-cert.pem"
    sslkey = "sslkey=.ssl/client-key.pem"
    hostaddr = "hostaddr={}".format(os.environ.get('PG_HOST'))
    user = "user=postgres"
    password = "password={}".format(os.environ.get('PG_PASSWORD'))
    dbname="dbname=mgmt590"

    dbconnect = " ".join([sslmode,
                            sslrootcert,
                            sslcert,
                            sslkey,
                            hostaddr,
                            user,
                            dbname,password])
    conn = psycopg2.connect(dbconnect)
    cur = conn.cursor()
    if params == None:
        cur.execute(query)
    else:
        cur.execute(query,params)

    conn.commit()

    conn.close()

#Function to get Unixtimestamp
def getUnixTimeStamp():
    systime = datetime.datetime.now()
    unixTimeStamp = int(time.mktime(systime.timetuple()))
    return unixTimeStamp

def insertInDB(csvfilename):
    df = pd.read_csv(csvfilename)
    for index,row in df.iterrows():
        question = row['question']
        context = row['context']
        answer = row['answer']
        modelName = 'distilled-bert'
        timestamp = getUnixTimeStamp()
        params = (modelName,question,context,answer,timestamp)
        query = '''insert into answer_history(model_name, question, context, answer, timestamp) values(%s,%s,%s,%s,%s)'''
        runSqlQuery(query, params)
        time.sleep(1) 


for dirpath, dirs, files in os.walk("/pfs/getfiles"):
   for file in files:
       print(os.path.join(dirpath, file)) 
       insertInDB(os.path.join(dirpath, file))
