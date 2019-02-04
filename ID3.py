from os import listdir
from os.path import isfile, join
import csv
import string
from numpy import log1p


class Data:
    def __init__(self, t):
        self.words = {}
        self.type = t

    def countWords(self, word):
        if word in self.words:
            return self.words[word]
        else:
            return 0


class Node:

    def __init__(self, spamC, hamC):
        self.hamC = hamC
        self.spamC = spamC
        self.word = None
        self.true = None
        self.false = None
        self.result = None


class ID3Tree:

    def create(self, h, s, u, d):
        node = Node(s, h)
        if len(u) == 0:
            node.result = 1 if len(h) < len(s) else -1
            return node
        elif len(h) == 0 and len(s) == 0:
            node.result = d
            return node
        elif len(h) == 0:
            node.result = 1
            return node
        elif len(s) == 0:
            node.result = -1
            return node

        word = getMaxGain(u)
        node.word = word
        node.result = 1 if len(h) < len(s) else -1

        uuf, uhf = removeMail(h, word, u)
        uuf, usf = removeMail(s, word, uuf)

        uut1, uht = keepMail(h, word, u)
        uut2, ust = keepMail(s, word, u)
        uut = uut1.copy()
        uut.update(uut2)

        node.false = self.create(uhf, usf, uuf, d)
        node.true = self.create(uht, ust, uut, d)
        return node


def cleaner(text):
    text = text.lower()
    translation_table = dict.fromkeys(map(ord, string.punctuation), None)

    stopWords = []
    f = open('stopwords.txt', 'r')
    for line in f:
        stopWords.append(line.strip())
    text = text.replace('\n', ' ')
    text = text.translate(translation_table)
    mail = text.split(' ')
    mail = [word for word in mail if word not in stopWords]
    return mail


def train(filename, type):
    files = [f for f in listdir(filename) if isfile(join(filename, f))]
    trainData = []
    for file in files:
        file = open(filename + "/" + file, errors='ignore')
        text = file.read()
        file.close()
        mail = cleaner(text)
        mailData = Data(type)
        for word in mail:
            if word is not '':
                if word in mailData.words:
                    mailData.words[word] += 1
                else:
                    mailData.words[word] = 1
                if (word, type) in uniqueWords:
                    uniqueWords[(word, type)] += 1
                else:
                    uniqueWords[(word, type)] = 1
                    uniqueWords[(word, -type)] = 0

        trainData.append(mailData)
    return trainData


def removeMail(data, word, u):
    for mail in data:
        if word in mail.words:
            for mailWord in mail.words:
                u[(mailWord, mail.type)] -= mail.words[mailWord]
            data.remove(mail)
    return u, data


def keepMail(data, word, u):
    newd = list()
    newu = dict()
    for mail in data:
        if word in mail.words:
            for mailWord in mail.words:
                newu[(mailWord, mail.type)] = mail.words[mailWord]
            newd.append(mail)
    return u, data


def countWords(data, word):
    g = 0
    for mail in data:
        g += mail.countWords(word)
    return g


def entropy(w, u):
    ps = ph = psl = phl = 0.0
    if w is None:
        ps = len(spam) / total
        ph = len(ham) / total
    else:
        ps = u[(w, 1)] / total
        ph = u[(w, -1)] / total

    psl = log1p(ps)
    phl = log1p(ph)
    return - psl * ps - phl * ph


def gain(w, u):
    hcx = entropy(w, u)
    x = u[(w, 1)] + u[(w, -1)]
    px = x / total
    return hc - px * hcx


def getMaxGain(u):
    maxW = None
    maxG = -9
    for (word, num) in u:
        if u[word, num] is not 0:
            g = gain(word, u)
            if g > maxG:
                maxG = g
                maxW = word
    return maxW


def classify(message):
    curNode = root
    result = None
    while curNode.word is not None:
        result = curNode.result
        if curNode.word in message:
            curNode = curNode.true
        else:
            curNode = curNode.false
    return result


def test():
    files = [f for f in listdir("input") if isfile(join("input", f))]
    spamC = hamC = 0
    for file in files:
        file = open("input" + "/" + file, errors = "ignore")
        text = file.read()
        file.close()
        text = cleaner(text)
        r = classify(text)
        if r == 1:
            spamC += 1
        else:
            hamC += 1
    print("Spam:\t" + str(spamC))
    print("Ham:\t" + str(hamC))


uniqueWords = dict()
spam = train("spam", 1)
ham = train("ham", -1)
total = 0
for word in uniqueWords:
    total += uniqueWords[word]
total = float(total)
hc = entropy(None, uniqueWords)
tree = ID3Tree()
root = tree.create(ham, spam, uniqueWords, -1)
test()

