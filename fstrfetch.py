#!/usr/bin/python3

import httplib2
import os
import json
from itertools import count
import urllib.request

def mkquery(q, what):
    print("mkquery", what)
    base = q[what]
    # url, args
    url = base["url"]
    args = base.get("args", [])
    if "add-args" in q:
      args += q["add-args"]


    print(args)
    if args:
      url += "?" + "&".join([ak+"="+av for ak, av in args])

    print("  =>", url)
    return url

def fetch_all():
  queries=json.load(open('fstr.json'))

  op_q = mkquery(queries, "operators")
#url=queries["shop_id"]%{"shop_name": urllib.parse.quote(shop_name)}
  try:
        resp = urllib.request.urlopen(op_q)
        if resp.headers.get_content_type() != 'application/json':
          print("error:", repr(resp.read(1000)))
          raise Exception("server did not return JSON data")
        else:
          data = json.loads(resp.read().decode("utf-8"))
          #print(data["items"])
          for d in data["items"]:
            op_phone = d["internal_number"]
            if op_phone:
              print("%-30s %d"%(d["fio"].strip(), op_phone), d["group_id"])
  except Exception as e:
        import traceback
        traceback.print_exc(e)
        print("error", e)


  shop_q = mkquery(queries, "shops")
  try:
        resp = urllib.request.urlopen(shop_q)
        if resp.headers.get_content_type() != 'application/json':
          print("error:", repr(resp.read(1000)))
          raise Exception("server did not return JSON data")
        else:
          data = json.loads(resp.read().decode("utf-8"))
           
          print(data.keys())
          for d in data["items"]:
            print(d)
#            op_phone = d["internal_number"]
#            if op_phone:
#              print("%-30s %d"%(d["fio"].strip(), op_phone), d["group_id"])
  except Exception as e:
        import traceback
        traceback.print_exc(e)
        print("error", e)

  exit()


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

      if d_master in masters:
        print("duplicate", d_master)
        continue

      masters.add(d_master)

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
      if m is None: continue
      if m not in masters:
        print("delete", m)
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

#    update_data_in_table(db, "shops", "shop_",
#                "name", ['eid', 'phone', 'script', 'level', 'manager', 'manager2', 'active', 'queue2', 'queue3'],
#                shops_cols, shops_data)

    update_data_in_table(db, "shops", "shop_",
                "name", ['eid', 'phone', 'script', 'level', 'manager', 'active', 'queue2', 'queue3'],
                shops_cols, shops_data)

