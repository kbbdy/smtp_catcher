# coding: utf-8
import os
import peewee as pw
from .settings import conf
from .log import logger

db = pw.SqliteDatabase(None)


class Message(pw.Model):
    time      = pw.DateTimeField()
    addr_from = pw.CharField()
    addr_to   = pw.CharField()
    subject   = pw.CharField()
    raw_data  = pw.TextField()
    size      = pw.IntegerField()
    raw_tags  = pw.CharField(default='')
    new       = pw.BooleanField(default=True)

    class Meta:
        database = db

    def __str__(self):
        if len(self.subject) > 28:
            s = self.subject[:28]+"..."
        else:
            s = self.subject
        return '<Email FROM: [%s] TO: [%s] SUBJECT: [%s]>' %\
            (self.addr_from, self.addr_to, s)

    @property
    def time_human(self):
        return self.time.strftime('%d.%m.%Y - %H:%M:%S')

    @property
    def tag_list(self):
        return set(filter(bool, self.raw_tags.strip('|').split('|')))

    def add_tag(self, tag):
        tlist = self.tag_list
        tlist.add(tag.replace('|', ' ').strip())
        if len(tlist) > 0:
            self.raw_tags = '|'+('|'.join(tlist)) + '|'
        else:
            self.raw_tags = ''

    @property
    def tags(self):
        res = []
        tl = list(self.tag_list)
        tl.sort()
        for t in tl:
            res.append(process_tag(t))
        return res

    @property
    def has_tags(self):
        return len(self.raw_tags) > 0


def process_tag(tag):
    res = {'text': tag, 'types': []}
    if tag in ('master', 'test'):
        res['types'].append('branch')
    if tag in ('master', 'hot'):
        res['types'].append('hot')
    return res


def all_tags():
    result = set()
    query = Message.select(Message.raw_tags).where(Message.raw_tags != '').distinct()
    for msg in query:
        for t in msg.tag_list:
            result.add(t)
    result = list(result)
    result.sort()
    for t in result:
        yield process_tag(msg.tags)


def prepare_db(dbfile):
    '''
    Create database file if it's not existsing.
    dbfile - name of sqlite database file
    '''
    global db
    db.init(dbfile)
    if os.path.exists(dbfile):
        logger.info("Using existing database file: %s" % dbfile)
    else:
        logger.info("Creating database file: %s" % dbfile)
        db.create_tables([Message])
