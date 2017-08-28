import httplib2
import os
import json
from itertools import count


from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import postgresql

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Sheets API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sheets.googleapis.com-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def fetch_doc(doc_id, doc_range):
    """Shows basic usage of the Sheets API.

    Creates a Sheets API service object and prints the names and majors of
    students in a sample spreadsheet:
    https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)

#    spreadsheetId = '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'
    spreadsheetId = doc_id
#    rangeName = 'C2:C59'
    print("range:", doc_range)
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheetId, range=doc_range).execute() #, range=rangeName
    values = result.get('values', [])

    return values


def fetch_all():
  doc_list=json.load(open('gdocs.json'))
  all_data = {}
  for what, doc in doc_list.items():
    doc_id = doc["id"]
    doc_columns = doc["columns"]
    doc_range = doc["range"]
    data = fetch_doc(doc_id, doc_range)
    header = None
    while not header: # skip empty lines
      header, data = data[0], data[1:]
    print(what, doc_columns, header)
    coltext_n = {} # make map header text -> col_n
    for n, h in zip(count(0), header):
      print(n, h)
      coltext_n[h] = n

    col_n = {}
    for colname, coltext in doc_columns.items():
      if coltext in coltext_n:
        col_n[colname] = coltext_n[coltext] # or error - no needed column
      else:
        raise Exception("Document %s does not have column %s"%(doc_id, coltext))


#    print(col_n)
#    for data1 in data:
#      print(data1)

    all_data[what]=(col_n, data)

  return all_data

#    if not values:
#        print('No data found.')
#    else:
#        out = []
#        for row in values:
#          if row:
#            # Print columns A and E, which correspond to indices 0 and 4.
#            if len(row)>=5:
#              pass #print(row[0], row[2], row[4:])
#              out.append((row[0], row[2], row[4:]))
#            else:
#              print(row)
#        import json
#        json.dump(out, open("shops.json", "w"))

def getval(l, i):
  if len(l)>i:
    return l[i]
  else:
    return None

if __name__ == '__main__':
    dbconn = json.load(open("database.json"))
    db = postgresql.open(**dbconn)

    op_fields = ["group", "ext", "location"]
    op_columns = ["op_"+x for x in op_fields]
    op_columns_argn = list(zip(op_columns, count()))
    op_columns_argn_n = ["$%d"%(x[1]+2) for x in op_columns_argn]
    op_columns_argn_set = ["%s=$%d"%(x[0], x[1]+2) for x in op_columns_argn]

    op_fields_full = ['name'] + op_fields

    q_ops = db.prepare("select " + ", ".join(op_columns) + " from operators where op_name=$1")
    q_op_ins = db.prepare("insert into operators (op_name, " + ", ".join(op_columns) + ") values ($1, " + ", ".join(op_columns_argn_n) + ")")
    q_op_upd = db.prepare("update operators set " + ", ".join(op_columns_argn_set) + " where op_name=$1")


    all_data = fetch_all()
    print("sources:", all_data.keys())
    managers_cols, managers_data = all_data['managers']

    for m in managers_data:
      if len(m)<=max(managers_cols.values()):
        print("short line", repr(m))
        continue

      m_name = m[managers_cols['name']]
      m_data = [m[managers_cols[x]] for x in op_fields]

      x=q_ops(m_name)
      if len(x)==0:
        print("new operator", m_name)
        q_op_ins(m_name, *m_data)
      else:
        print("existing operator", m_name)
        m_diff = False
        for z in zip(x[0], m_data, op_columns):
          if z[0]!=z[1]:
            print("diff on", z[2], "->", z[0], "!=", z[1])
            m_diff = True
            break
        if m_diff:
          q_op_upd(m_name, *m_data)

    exit()

    shops_cols, shops_data = all_data['shops']
    for s in shops_data:
      # insert/update on shop_name (add record or update record with same shop_data)
      shop_name=getval(s, shops_cols['shop'])
      shop_phone=getval(s, shops_cols['phone'])
      shop_script=getval(s, shops_cols['script'])
      shop_worktime=getval(s, shops_cols['worktime'])
      shop_manager=getval(s, shops_cols['manager'])
      existing = db.prepare("select shop_phone, shop_script, shop_worktime, shop_pri_manager from shops where shop_name=$1")(shop_name)
      if len(existing)==0:
        print("add", shop_name)
        db.prepare("insert into shops (shop_name, shop_phone, shop_script, shop_worktime, shop_pri_manager) values ($1,$2,$3,$4,$5)")\
		(shop_name, shop_phone, shop_script, shop_worktime, shop_manager)
      else:
        if existing[0][0]!=shop_phone:
          print("update phone")
          db.prepare("update shops set shop_phone=$2 where shop_name=$1")(shop_name, shop_phone)
        if existing[0][1]!=shop_script:
          print("update script")
          db.prepare("update shops set shop_script=$2 where shop_name=$1")(shop_name, shop_script)
        if existing[0][2]!=shop_worktime:
          print("update worktime")
          db.prepare("update shops set shop_worktime=$2 where shop_name=$1")(shop_name, shop_worktime)
        if existing[0][3]!=shop_manager:
          print("update primary manager")
          db.prepare("update shops set shop_pri_manager=$2 where shop_name=$1")(shop_name, shop_manager)
