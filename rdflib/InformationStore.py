from rdflib.TripleStore import TripleStore
from rdflib.Store import Store
from rdflib.Store import check_subject, check_predicate, check_object
from rdflib.backends.SleepyCatBackend import SleepyCatBackend


from rdflib.exceptions import ContextTypeError

from rdflib.URIRef import URIRef
from rdflib.BNode import BNode
from rdflib.Literal import Literal
from rdflib.Namespace import Namespace

from rdflib.constants import TYPE

INFORMATION_STORE = Namespace("http://rdflib.net/2002/InformationStore#")
CONTEXT = INFORMATION_STORE["Context"]
SOURCE = INFORMATION_STORE["source"]

def check_context(c):
    if not (isinstance(c, URIRef) or \
       isinstance(c, BNode)):
        raise ContextTypeError("%s:%s" % (c, type(c)))

class ContextBackend(object):

    def __init__(self, backend, identifier):
        super(ContextBackend, self).__init__()
        self.backend = backend
        self.identifier = identifier

    def add(self, (subject, predicate, object)):
        context = self.identifier
        self.backend.add((subject, predicate, object), context)
        
    def remove(self, (subject, predicate, object)):
        context = self.identifier
        self.backend.remove((subject, predicate, object), context)
        
    def triples(self, triple):
        context = self.identifier
        for triple in self.backend.triples(triple, context):
            yield triple

    def __len__(self):
        # TODO: backends should support len
        i = 0
        for triple in self.triples((None, None, None)):
            i += 1
        return i
    

class Context(TripleStore):
    def __init__(self, backend, identifier):
        super(Context, self).__init__(None, ContextBackend(backend, identifier))
        self.identifier = identifier


class InformationStore(Store):
    def __init__(self, path=None, backend=None):
        backend = backend or SleepyCatBackend()
        super(InformationStore, self).__init__(backend)
        if path:
            self.open(path)
        
    def load(self, location, format="xml"):
        location = self.absolutize(location)
        for id in self.subjects(SOURCE, location):
            context = self.get_context(id)
            self.remove_context(id)
        id = BNode()
        context = self.get_context(id)
        context.add((id, TYPE, CONTEXT))
        context.add((id, SOURCE, location))
        context.load(location, format)

    def get_context(self, identifier):
        check_context(identifier)        
        return Context(self.backend, identifier)

    def remove_context(self, identifier):
        self.backend.remove_context(identifier)
        
    def add(self, (subject, predicate, object), context):
        check_subject(subject)
        check_predicate(predicate)
        check_object(object)
        check_context(context)
        self.backend.add((subject, predicate, object), context)

    def remove(self, (subject, predicate, object), context=None):
        if subject:
            check_subject(subject)
        if predicate:
            check_predicate(predicate)
        if object:
            check_object(object)
        if context:
            check_context(context)
        self.backend.remove((s, p, o), context)

    def triples(self, (subject, predicate, object), context=None):
        if subject:
            check_subject(subject)
        if predicate:
            check_predicate(predicate)
        if object:
            check_object(object)
        if context:
            check_context(context)
        for triple in self.backend.triples((subject, predicate, object), context):
            yield triple
        
    def contexts(self, triple=None):
        for context in self.backend.contexts(triple):
            yield context
            
