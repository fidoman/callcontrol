#!/usr/bin/python3

import httplib2
import os
import json
from itertools import count


from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage


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


def update_data_in_table(db, table, column_prefix, master_field, data_fields, data_field_pos, data_list):
    columns = [column_prefix+x for x in data_fields]
    master_column = column_prefix+master_field

    columns_argn = list(zip(columns, count())) # enumerate
    columns_argn_n = ["$%d"%(x[1]+2) for x in columns_argn] # positional arguments for insert
    columns_argn_set = ["%s=$%d"%(x[0], x[1]+2) for x in columns_argn] # assignments for update

    q = db.prepare("select " + ", ".join(columns) + " from " + table + " where " + master_column + "=$1")
    q_ins = db.prepare("insert into " + table + " (" + master_column + ", " + ", ".join(columns) + ") values ($1, " + ", ".join(columns_argn_n) + ")")
    q_upd = db.prepare("update " + table + " set " + ", ".join(columns_argn_set) + " where " + master_column + "=$1")

    q_masters = db.prepare("select " + master_column + " from " + table)

    max_field = max(data_field_pos.values())

    masters = set()

    for d in data_list:
      # prevent 'out of index' errors
      while len(d)<=max_field:
        d.append('')

      d_master = d[data_field_pos[master_field]]
      if not d_master:
        print("skip", repr(d))
        continue

      if d_master.lower() in masters:
        print("duplicate", d_master)
        continue

      masters.add(d_master.lower())

      d_fields = [d[data_field_pos[x]] for x in data_fields]

      x=q(d_master)
      if len(x)==0:
        print("new item", d_master)
        q_ins(d_master, *d_fields)
      else:
        print("existing item", d_master)
        m_diff = False
        for z in zip(x[0], d_fields, data_fields):
          if z[0]!=z[1]:
            print("diff on", z[2], ":", z[0], "=>", z[1])
            m_diff = True
            break
        if m_diff:
          print(d_master, d_fields)
          q_upd(d_master, *d_fields)

    for (m,) in q_masters():
      if not m: continue
      print(m, m.lower() in masters)
      if m.lower() not in masters:
        db.prepare("delete from "+table+" where "+master_column+"=$1")(m)

if __name__ == '__main__':
    all_data = fetch_all()
    print("sources:", all_data.keys())

    level_cols, levels_data = all_data['levels']
    managers_cols, managers_data = all_data['managers']
    shops_cols, shops_data = all_data['shops']

    import postgresql
    dbconn = json.load(open("database.json"))
    db = postgresql.open(**dbconn)

    update_data_in_table(db, "levels", "l_", "name", ["worktime"], level_cols, levels_data)

    update_data_in_table(db, "operators", "op_", "ext", ["name", "group", "location"], managers_cols, managers_data)

    update_data_in_table(db, "shops", "shop_",
                "name", ['phone', 'script', 'level', 'manager', 'manager2', 'active', 'queue2', 'queue3'],
                shops_cols, shops_data)

