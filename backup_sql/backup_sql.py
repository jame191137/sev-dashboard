from header import *
import boto3
from flask import send_from_directory,send_file
import tempfile
@app.route('/trysql', methods=['GET'])
def tryconnect():
    if os.environ['ENV'] == 'dev':
        connection = mysql.connect()
        cursor = connection.cursor()
        sql = "SELECT * FROM test"
        cursor.execute(sql)
        columns = [column[0] for column in cursor.description]
        result = toJson(cursor.fetchall(),columns)
        connection.commit()
        connection.close()
        return jsonify(result)
    else:
        connection = mysql.connect()
        cursor = connection.cursor()
        sql = "SELECT * FROM ipsocketio WHERE id=1"
        cursor.execute(sql)
        columns = [column[0] for column in cursor.description]
        result = toJson(cursor.fetchall(),columns)
        connection.commit()
        connection.close()
        return jsonify(result)

@app.route('/backup', methods=['GET'])
def backup():
    DB_HOST = os.environ['SQL_IP']
    DB_USER = os.environ['SQL_USERNAME']
    DB_USER_PASSWORD = os.environ['SQL_PASSWORD']
    DB_NAME = os.environ['SQL_DB']
    BACKUP_PATH = 'backup/sql'
    DATETIME = time.strftime('%Y%m%d-%H%M%S')

    if not os.path.exists(BACKUP_PATH):
        os.makedirs(BACKUP_PATH)

    db = DB_NAME
    fileName = db + '_' + DATETIME
    dumpcmd = "mysqldump -h " + DB_HOST + " -u " + DB_USER + " -p" + "\"" + DB_USER_PASSWORD + "\"" + " " + db + " > " + pipes.quote(BACKUP_PATH) + "/" + fileName + ".sql"
    os.system(dumpcmd)
    gzipcmd = "gzip " + pipes.quote(BACKUP_PATH) + "/" + fileName + ".sql"
    os.system(gzipcmd)
    # return 'success'
    s3_client = boto3.client(
                    's3',
                    aws_access_key_id='EHYEK7MBRNVC018XF0FP',
                    aws_secret_access_key='nzjt5e9SmpwK+WWShAgMy6CrHqhgpLBh0Oms0Pgk',
                    endpoint_url='https://s3gw.inet.co.th:8082'
        )
    with open('./backup/sql/'+fileName+'.sql.gz', 'rb') as f:
        s3_client.upload_fileobj(f, "bucket_backup", 'backup/sql/'+fileName+'.gz')
    return 'success'

# @app.route('/create_bucket',methods = ['GET'])
# def create_b():
#     s3_client = boto3.client(
#                     's3',
#                     aws_access_key_id='EHYEK7MBRNVC018XF0FP',
#                     aws_secret_access_key='nzjt5e9SmpwK+WWShAgMy6CrHqhgpLBh0Oms0Pgk',
#                     endpoint_url='https://s3gw.inet.co.th:8082'
#         )
#     s3_client.create_bucket(Bucket='bucket_backup')
#     return 'success'

@app.route('/download',methods = ['GET'])
def downl():
    s3_client = boto3.client(
                    's3',
                    aws_access_key_id='EHYEK7MBRNVC018XF0FP',
                    aws_secret_access_key='nzjt5e9SmpwK+WWShAgMy6CrHqhgpLBh0Oms0Pgk',
                    endpoint_url='https://s3gw.inet.co.th:8082'
        )
    tmp = tempfile.NamedTemporaryFile(suffix = '.sql.gz',dir='',delete=True)
    tmp.flush()
    tmp.close()
    with open(tmp.name, 'wb') as f:
                # current_app.logger.info("test")
                s3_client.download_fileobj('bucket_backup','backup/sql/korkla_test_20190212-072510.gz',f)
    return 'success'

    # s3_client.meta.client.download_file('bucket_backup', 'backup/sql/korkla_test_20190212-072510.sql.gz', 'file_dow.sql.gz')
    # return 'success'
    # s3_client.Bucket('bucket_backup').download_file('/backup/sql/korkla_test_20190212-063409.sql.gz', os.path.basename('file_dow.sql.gz'))
    # return 'success'
    with open('download2.sql.gz', 'wb') as data:
        s3_client.download_fileobj('bucket_backup', 'backup/sql/korkla_test_20190212-072510.sql.gz', data)

    return 'success'
