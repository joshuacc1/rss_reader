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
#from database import DatabaseManagement

import pprint

class RSSNLTK:
    def __init__(self):
        self.texts = {'titles': [], 'summaries': [], 'htmltexts': []}
        self.links = []
        self.content = []
        self.rsslink = None
        self.feedparser = None
        self.tokentext = None
        self.senttokenizedtext = None

    def savetojson(self, filename):
        with open(filename, 'w') as f:
            json.dump(self.texts)

    def loadjson(self, filename):
        with open(filename) as f:
            self.texts = json.load(f)

    def initializeRSS(self, rsslink):
        self.rsslink = rsslink
        self.feedparser = feedparser.parse(rsslink)
        for entry in self.feedparser.entries:
            self.texts['titles'].append(entry['title'])
            if entry['summary']: self.texts['summaries'].append(entry['summary'])
            if not entry.link in self.links: self.links.append(entry.link)

    def initRSSdatabase(self):
        datalink = DatabaseManagement.feedsmanagement()
        for entry in datalink.getfeeds():
            self.texts['titles'].append(entry['title'])
            if entry['summary']: self.texts['summaries'].append(entry['summary'])
            if not entry['link'] in self.links: self.links.append(entry['link'])
            if 'htmltext' in entry and entry['htmltext']: self.texts['htmltexts'].append(entry['htmltext'])


    def getHTMLlinktext(self, sensitivity = 5):
        for link in self.links:
            response = request('GET', link)
            soup = BeautifulSoup(response.content)
            htmltext = soup.find_all(text=True)
            visibletext = filter(self.tag_visible,htmltext)
            cleantexts = [text for text in visibletext if len(text.split(' ')) > sensitivity]
            mergedtext = ' '.join(cleantexts)
            self.texts['htmltexts'].append(mergedtext)

    def tokenizetext(self):
        tokentexts = {}

        for src in self.texts:
            tokentexts[src] = []

        for src in self.texts:
            for text in self.texts[src]:
                tokentexts[src].append(word_tokenize(text))

        self.tokentext = tokentexts
        return tokentexts

    def senttokenizetext(self):
        senttokentexts = {}

        for src in self.texts:
            senttokentexts[src] = []

        for src in self.texts:
            for text in self.texts[src]:
                senttokentexts[src].append(sent_tokenize(text))

        self.senttokenizedtext = senttokentexts
        return senttokentexts

    def textconcordance(self,word,textsname):
        if self.tokentext:
            for text in self.tokentext[textsname]:
                yield self.getconcordance(word,text)

    def getconcordance(self,word,text):
                T = Text(text)
                for match in T.concordance_list(word):
                    if not match == 'no matches':
                        return match.line
    def textsimiliar(self, word, textsname):
        if self.tokentext:
            for text in self.tokentext[textsname]:
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
        for text in self.tokentext['htmltexts']:
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
            words[word]['count'] = words[word]['count']/maxcount

        words = sorted(words.values(), key=lambda x: x['count'])
        words = {x['word']: x for x in words}

        return words

    def scoresentences(self,text):
        words = self.countwords(text)

        senttk = sent_tokenize(text)
        scoredsentences = []
        for sent in senttk:
            sentscore = 0
            for word in word_tokenize(sent):
                sentscore += words[word]['count']
            scoredsentences.append({'sentence': sent, 'score': sentscore})

        #csenttks = [{'sentence': x, 'count': 1} for x in senttks]

        # for senttk in senttks:
        #     tscore = 0
        #     for word in word_tokenize(senttk):
        #         tscore += words[word]

        return scoredsentences

    def summarizetexts(self,texttype):
        textsummaries = []
        for text in self.texts[texttype]:
            counts = self.scoresentences(text)
            scounts = sorted(counts, key=self.filtercount)
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
    rssproc.loadjson('junk.json')
    rssproc.tokenizetext()
    rssproc.senttokenizetext()
    rssproc.summarizetexts('htmltexts')

    # filcounts = filter(rssproc.filtercount,counts.values())
    # highestcount = [x for x in filcounts][-1]['count']
    # filcounts = filter(rssproc.filtercount, counts.values())
    # filweights = {}
    # for x in filcounts:
    #     item =x
    #     item['count'] = item['count']/highestcount
    #     filweights[x['word']] = item
    # print([x for x in filweights.values()])
    senttokens = rssproc.senttokenizedtext['htmltexts'][10]

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


    for match in rssproc.textconcordance("election", "summaries"):
        if match:
         print(match)
    for match in rssproc.textsimiliar("Peloci","htmltexts"):
        if match:
            print(match)