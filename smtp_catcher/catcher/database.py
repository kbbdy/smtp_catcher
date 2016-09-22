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
    branch    = pw.CharField(default='')
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
    def tags(self):
        res = []
        if self.branch == 'master':
            res.append({'types': ('branch', 'hot'),
                        'text': 'master'})
        elif self.branch:
            types = ['branch']
            if 'demo' in self.branch:
                types.append('demo')
            res.append({'types': types,
                        'text': self.branch})
        return res


def create_tag_for_branch(branchname):
    types = ['branch']
    if branchname == 'master':
        return {'types': ('branch', 'hot'),
                'text': 'master'}
    if 'demo' in branchname:
        types.append('demo')
    return {'types': types,
            'text': branchname}


def all_tags():
    query = Message.select(Message.branch).where(Message.branch != '').distinct()
    result = []
    for msg in query:
        yield create_tag_for_branch(msg.branch)


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
