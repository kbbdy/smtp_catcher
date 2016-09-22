#!/usr/bin/env python3.5
# coding: utf-8
import email, re, binascii
from email import message_from_string

CID_PREFIX = 'cid:'


class EmailViewer:
    def __init__(self, static_url='/'):
        self.msg = None
        self._media = None
        self.static_url = static_url

    def load_from_file(self, filename):
        with open(filename) as fp:
            self.msg = message_from_string(fp.read())

    def load_from_string(self, data):
        self.msg = message_from_string(data)

    def fields(self):
        fields = ('Subject', 'From', 'To')
        res = {}
        for f in fields:
            res[f] = self.msg[f]
        return res

    def body(self, html=True):
        if html:
            expected_type = 'text/html'
        else:
            expected_type = 'text/plain'
        if self.msg.is_multipart():
            for part in self.msg.walk():
                ctype = part.get_content_type()
                cdispo = str(part.get('Content-Disposition'))
                # skip any text/plain (txt) attachments
                if (ctype == expected_type) and ('attachment' not in cdispo):
                    decode = part.get('Content-Transfer-Encoding', None) != '8bit'
                    body = part.get_payload(decode=decode)
                    break
        else:
            decode = self.msg.get('Content-Transfer-Encoding', None) != '8bit'
            body = self.msg.get_payload(decode=decode)
        if type(body) == bytes:
            body = body.decode('utf-8', 'ignore')
        return body

    def _cid_replace(self, cid):
        if not cid.lower().startswith(CID_PREFIX):
            return "-"
        content_name = cid[len(CID_PREFIX):]
        hx = str(binascii.hexlify(bytes(content_name, 'utf-8')), 'ascii')
        if content_name not in self._media:
            self._media[hx] = content_name
        return self.static_url+hx

    def processed_body(self):
        if self._media is None:
            self._media = {}
        body = self.body()
        if body is None:
            body = self.body(False)
        reg = re.compile(r'<[\s\S^>]+?src="('+CID_PREFIX+r'\S+)"[\s\S]*?>')
        limit = 100
        start = 0
        while True:
            res = reg.search(body)
            if res is None:
                break
            cid = body[res.start(1):res.end(1)]
            cid = self._cid_replace(res.groups()[0])
            body = body[:res.start(1)] + cid + body[res.end(1):]
            limit -= 1
            if limit == 0:
                break
        return body

    def get_part_by_name(self, content_name):
        if not self.msg.is_multipart():
            return None
        for part in self.msg.walk():
            name = part.get('Content-ID')
            if name is None:
                continue
            if name.strip("<>") == content_name:
                return part
        return None

    def media_file(self, content_name):
        if self._media is None:
            self.processed_body()
        cid = self._media[content_name]
        media_part = self.get_part_by_name(cid)
        fn = media_part.get_filename()
        mime_type = media_part.get('Content-Type')
        payload = media_part.get_payload(decode=True)
        return mime_type, payload
