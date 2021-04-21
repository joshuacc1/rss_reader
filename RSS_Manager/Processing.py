from nltk import word_tokenize, Text, pos_tag
import feedparser
from bs4 import BeautifulSoup
from bs4.element import Comment
from requests import request
from nltk import word_tokenize, Counter, pos_tag, sent_tokenize
from nltk.text import ContextIndex
from nltk.chunk.regexp import ChunkRule, ExpandLeftRule, ExpandRightRule, UnChunkRule
from nltk.chunk import RegexpChunkParser
from sklearn.feature_extraction.text import CountVectorizer
import json
from database import DatabaseManagement
import collections
import pprint

class RSSNLTK:
    def __init__(self):
        self.datatags = {'link': '', 'title': '', 'summary': '', 'htmltext': '','author': ''}
        self.texts = []
        self.links = []
        self.content = []
        self.rsslink = None
        self.feedparser = None
        self.tokentext = None
        self.senttokenizedtext = None

    def savetojson(self, filename):
        with open(filename, 'w') as f:
            json.dump(self.texts,f)

    def loadjson(self, filename):
        with open(filename) as f:
            self.texts = json.load(f)

    def getdata(self, rsslink = '', jsonfilename = ''):
        if rsslink:
            self.rsslink = rsslink
            self.feedparser = feedparser.parse(rsslink)
            source = self.feedparser
            self.initializeRSS(source['entries'])
            self.getHTMLlinktext()
            if jsonfilename:
                self.savetojson(jsonfilename)
        elif jsonfilename:
            self.loadjson(jsonfilename)
        else:
            datalink = DatabaseManagement.feedsmanagement()
            source = datalink.getfeeds()
            self.initializeRSS(source)


    def initializeRSS(self, source):
        for entry in source:
            text = self.datatags.copy()
            text['title'] = entry['title']
            if entry['summary']: text['summary'] = entry['summary']
            if entry['link']: text['link'] = entry['link']
            if entry.get('author'): text['author'] = entry['author']
            if entry.get('htmltext'): text['htmltext'] = entry['htmltext']
            self.texts.append(text)

    def getHTMLlinktext(self, sensitivity = 5):
        for text in self.texts:
            response = request('GET', text['link'])
            soup = BeautifulSoup(response.content)
            htmltext = soup.find_all(text=True)
            visibletext = filter(self.tag_visible,htmltext)
            cleantexts = [text for text in visibletext if len(text.split(' ')) > sensitivity]
            mergedtext = ' '.join(cleantexts)
            text['htmltext'] = mergedtext

    def getHTMLtext(self, link, sensitivity = 5):
        response = request('GET', link)
        soup = BeautifulSoup(response.content)
        htmltext = soup.find_all(text=True)
        visibletext = filter(self.tag_visible,htmltext)
        cleantexts = [text for text in visibletext if len(text.split(' ')) > sensitivity]
        mergedtext = ' '.join(cleantexts)
        return mergedtext

    def tokenizetext(self):
        tokentexts = []
        datatags = self.datatags

        for text in self.texts:
            tokeneditem = self.datatags.copy()
            for datatag in datatags:
                try:
                    tokeneditem[datatag] = word_tokenize(text[datatag])
                except:
                    tokeneditem[datatag] = [text[datatag]]
            tokentexts.append(tokeneditem)

        self.tokentext = tokentexts
        return tokentexts

    def senttokenizetext(self):
        tokentexts = []
        datatags = self.datatags

        for text in self.texts:
            tokeneditem = self.datatags.copy()
            for datatag in datatags:
                try:
                    tokeneditem[datatag] = sent_tokenize(text[datatag])
                except:
                    tokeneditem[datatag] = [text[datatag]]
            tokentexts.append(tokeneditem)

        self.senttokenizedtext = tokentexts
        return tokentexts

    def textconcordance(self,word,textsname):
        if self.tokentext:
            for item in self.tokentext:
                text = item[textsname]
                yield self.getconcordance(word,text)

    def getconcordance(self,word,text):
                T = Text(text)
                for match in T.concordance_list(word):
                    if not match == 'no matches':
                        return match.line
    def textsimiliar(self, word, textsname):
        if self.tokentext:
            for item in self.tokentext:
                text = item[textsname]
                yield self.getsimiliar(word,text)

    def getsimiliar(self,word, text):
        T = Text(text)
        word_context_index = ContextIndex(T.tokens,
                                        filter=lambda x: x.isalpha(),
                                        key=lambda s: s.lower())
        word = word.lower()
        wci = word_context_index._word_to_contexts
        words = []
        if word in wci.conditions():
            contexts = set(wci[word])
            fd = Counter(w for w in wci.conditions() for c in wci[w]
                         if c in contexts and not w == word)
            words = [w for w, _ in fd.most_common(20)]
        return words


    def makevector(self,sentences):
        vectorizer_count = CountVectorizer()
        features_text = vectorizer_count.fit_transform(sentences).todense()
        return(vectorizer_count.vocabulary_)

    def getallnouns(self):
        words = {}
        for text in [x['htmltext'] for x in self.tokentext]:
            postag =  pos_tag(text)
            for i in postag:
                if not i[0] in words:
                    words[i[0]] = {'count': 1, 'word': i[0], 'tag': i[1]}
                else:
                    words[i[0]]['count'] += 1

        words = sorted(words.values(), key=lambda x: x['count'])
        words = {x['word']: x for x in words}

        for word in words:
            if 'NNP' == words[word]['tag']:
                print(words[word]['count'], words[word]['word'])

    def countwords(self, text):
        words = {}
        maxcount = 0
        postag =  pos_tag(word_tokenize(text))
        for i in postag:
            if not i[0] in words:
                words[i[0]] = {'count': 1, 'word': i[0], 'tag': i[1]}
            else:
                words[i[0]]['count'] += 1
                if words[i[0]]['count'] > maxcount:
                    maxcount = words[i[0]]['count']

        for word in words:
            if maxcount > 0:
                words[word]['count'] = words[word]['count']/maxcount

        words = sorted(words.values(), key=lambda x: x['count'])
        words = {x['word']: x for x in words}

        return words

    def scoresentences(self,text):
        words = self.countwords(text)

        senttk = sent_tokenize(text)
        scoredsentences = []
        for sent in senttk:
            senttk = word_tokenize(sent)
            sentscore = sum(self.tokenscoreiter(senttk,words))
            scoredsentences.append({'sentence': sent, 'score': sentscore})
        return scoredsentences

    def tokenscoreiter(self, tokens, wordscores):
        for token in tokens:
            if token in wordscores:
                yield wordscores[token]['count']

    def summarizetexts(self,texttype):
        textsummaries = []
        for text in [x[texttype] for x in self.texts]:
            counts = self.scoresentences(text)
            scounts = sorted(counts, key=self.filtercount)
            if scounts:
                print(scounts[-1])

    def filtercount(self,word):
        return word['score']

    def tag_visible(self, element):
        if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
            return False
        if isinstance(element, Comment):
            return False
        return True

if __name__ == "__main__":
    rssproc = RSSNLTK()
    #rssproc.initRSSdatabase()
    #rssproc.getdata(rsslink='http://feeds.foxnews.com/foxnews/politics', jsonfilename = 'foxnews.json')
    rssproc.getdata()
    rssproc.tokenizetext()
    rssproc.senttokenizetext()
    rssproc.summarizetexts('htmltext')

    # filcounts = filter(rssproc.filtercount,counts.values())
    # highestcount = [x for x in filcounts][-1]['count']
    # filcounts = filter(rssproc.filtercount, counts.values())
    # filweights = {}
    # for x in filcounts:
    #     item =x
    #     item['count'] = item['count']/highestcount
    #     filweights[x['word']] = item
    # print([x for x in filweights.values()])
    senttokens = rssproc.senttokenizedtext[1]['htmltext']

    s = 'there are 12 boxes in the closet'

    ur = ChunkRule('<CD>', 'single noun')
    el = ExpandLeftRule('<NNS>', '<CD>', 'get left determiner')
    er = ExpandRightRule('<CD>', '<NNS>', 'get right plural noun')
    un = UnChunkRule('<DT><NN.*>*', 'unchunk everything')

    chunker = RegexpChunkParser([ur,el,er])

    print(chunker.parse(pos_tag(word_tokenize(s))))

    d = []
    for sent in senttokens:
        tk = word_tokenize(sent)
        tkpos = pos_tag(tk)
        for x in tkpos:

            if 'CD' in x:
                w = chunker.parse(tkpos)
                d.append(w)
                break
    for x in d:
        #print(x)
        pass


    for match in rssproc.textconcordance("Russia", "htmltext"):
        if match:
         print(match)
    for match in rssproc.textsimiliar("Manafort","htmltext"):
        if match:
            print(match)