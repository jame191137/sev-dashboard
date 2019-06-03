from header import *
import pymongo
from bson.json_util import dumps
from os.path import join
import zipfile
import shutil
import boto3
import os

@app.route('/backup_mongo', methods=['GET'])
def backup_mongo():
    DATETIME = time.strftime('%Y%m%d-%H%M%S')
    backup_db_dir = 'backup/mongo' + '/cozy-mongo-' + DATETIME

    if not os.path.exists(backup_db_dir):
        os.makedirs(backup_db_dir)

    myCmd = os.popen('mongodump --forceTableScan -h "'+os.environ['MONGO_IP']+'" -d Cozy -u "'+os.environ['MONGO_USERNAME']+'" -p "'+os.environ['MONGO_PASSWORD']+'" -o "'+backup_db_dir+'" ').read()

    # client = pymongo.MongoClient(host=os.environ['MONGO_IP'], port=27017)
    # database = client['Cozy']
    # authenticated = database.authenticate(os.environ['MONGO_USERNAME'], os.environ['MONGO_PASSWORD'])
    # assert authenticated, "Could not authenticate to database!"
    # collections = database.collection_names()
    # for i, collection_name in enumerate(collections):
    #     col = getattr(database,collections[i])
    #     collection = col.find()
    #     jsonpath = collection_name + ".json"
    #     jsonpath = join(backup_db_dir, jsonpath)
    #     with open(jsonpath, 'wb') as jsonfile:
    #         jsonfile.write(dumps(collection))

    zip_file_backup(backup_db_dir)
    shutil.rmtree('backup/mongo')
    saveMongoToS3(backup_db_dir)
    return 'success'


def zip_file_backup(backup_path):
    backup_db_dir_zip = 'backup/mongo_zip'
    if not os.path.exists(backup_db_dir_zip):
        os.makedirs(backup_db_dir_zip)

    filename = backup_path.split('/')[-1] + '.zip'
    zipf = zipfile.ZipFile('backup/mongo_zip/' + filename, 'w', zipfile.ZIP_DEFLATED)
    zipdir(backup_path, zipf)
    zipf.close()
    return 'success'

def zipdir(path, ziph):
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))

def saveMongoToS3(backup_path):
    filename = backup_path.split('/')[-1] + '.zip'
    s3_client = boto3.client(
                    's3',
                    aws_access_key_id='EHYEK7MBRNVC018XF0FP',
                    aws_secret_access_key='nzjt5e9SmpwK+WWShAgMy6CrHqhgpLBh0Oms0Pgk',
                    endpoint_url='https://s3gw.inet.co.th:8082'
        )
    with open('./backup/mongo_zip/' + filename, 'rb') as f:
        s3_client.upload_fileobj(f, "bucket_backup", 'backup/mongo_zip/' + filename)

@app.route('/trymongo', methods=['GET'])
def trymongo():
    client = pymongo.MongoClient(host=os.environ['MONGO_IP'], port=27017)
    mndb = client.Cozy
    mndb.authenticate(os.environ['MONGO_USERNAME'], os.environ['MONGO_PASSWORD'])

    if os.environ['ENV'] == 'dev':
        result = mndb.room.find({"tokenroom":'R5bb46c8095389919394dd77714bec3c0cbef5f68a8ce974560ed7df0'})
        return str(result[0])
    else:
        result = mndb.check.find({"id":'1'})
        return str(result[0])

@app.route('/remove/<id>', methods=['GET'])
def removeAll(id):
    if not id == 'korkla':
        abort(403)
    try:
        shutil.rmtree('backup/mongo_zip')
        shutil.rmtree('backup/sql')
    except:
        return 'fail'
    return 'success'
