#!/usr/bin/env python
# -*- coding:utf-8 -*-
from flask import Flask, request
from datetime import datetime
import hmac
import json
import subprocess
from config import key, AURprojectMap, LOGFILE
key = key.encode()
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def updateAUR():
    if request.method == 'GET':
        return "You shouldn't be here. This is intended for POST only. "
    if request.method == 'POST':
        try:
            sig = request.headers.get("X-Hub-Signature")
            event = request.headers.get("X-GitHub-Event")
            body = request.data
            if not hmac.compare_digest(hmac.digest(
                    key, body, "sha1").hex(), sig[5:]):
                return "Error Signature", 403
        except:
            return "Not valid header", 403
        with open(LOGFILE, 'a') as f:
            print(datetime.now(), file=f)
            print(sig, event, file=f)
            print(body.decode(), file=f)
        if event == "create":
            hookinfo = json.loads(body)
            if hookinfo["ref_type"] != "tag":
                return "Ignore non tag result"
            name = hookinfo["repository"]["full_name"]
            if name in AURprojectMap:
                tag = hookinfo["ref"]
                if tag.startswith("v"):
                    tag = tag[1:]
                # check for security
                if len(tag) >= 20 or not all([c.isdigit() or c == "." 
                                              for c in tag]): 
                    return "Invalid tag!"
                result = subprocess.run(["./updateAUR.sh",
                                         AURprojectMap[name],
                                         tag], stderr=subprocess.STDOUT, 
                                        stdout=subprocess.PIPE, 
                                        text=True)
                if result.returncode:
                    reply = (("Error: %d\n" % result.returncode)
                             + result.stdout)
                    print("===REPLY===", reply)
                    return reply, 500
                else:
                    print("===REPLY===", result.stdout)
                    return result.stdout
            else:
                return "AUR package for %s didn't found"%name
        return 'Event: %s'%event
        
# vim: ts=4 sw=4 sts=4 expandtab
