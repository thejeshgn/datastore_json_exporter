# Thejesh GN
# Needs Python 2
import os
import sys
import json
import datetime


def default(o):
    if o is None:
      return ''
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.isoformat()

sys.path.append('./google_appengine')

input_file = "/opt/datastore/export/output-{index}"
max_num = 78 #how many output files are there?
index = 0

from google.appengine.api.files import records
from google.appengine.datastore import entity_pb
from google.appengine.api import datastore

with open('/opt/datastore/json/output.jsonl', mode='w') as fp:
    for index in range(0,38):
        raw = open(input_file.format(index=index), 'r')
        reader = records.RecordsReader(raw)
        for record in reader:
                entity_proto = entity_pb.EntityProto(contents=record)
                entity = datastore.Entity.FromPb(entity_proto)

                _kind = entity.kind()
                _key = str(entity.key())
                if entity:
                  entity["_kind"] = _kind
                  entity["_key"] = _key
                  fp.write(json.dumps(entity, default=default))
                  fp.write(u'\n')
                  fp.flush()
                break
        break
    fp.close()