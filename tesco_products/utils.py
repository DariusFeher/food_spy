from gensim.parsing.preprocessing import remove_stopwords, strip_punctuation, strip_numeric, strip_non_alphanum, strip_multiple_whitespaces, strip_short
from nltk.stem import WordNetLemmatizer
import re
import nltk
from nltk import word_tokenize


def clean_mention(mention):

  wnl = WordNetLemmatizer()
  copy_mention = mention
  mention = remove_stopwords(mention)
  mention = mention.lower()
  mention = strip_numeric(mention)
  mention = strip_punctuation(mention)
  mention = strip_non_alphanum(mention)
  mention = strip_multiple_whitespaces(mention)
  mention = strip_short(mention, 2)

  mention = re.sub(r'\(.*oz.\)|(®)|\bpint(s)*\b|\bkg\b|\bmg\b|\btesco\b|\bamazon\b|\bpack\b|\bportion(s)*\b|tast|\bsprig\b|\binch\b|\bpurpose\b|\bflmy\b|\btaste\b|boneless|skinless|chunks|fresh|\blarge\b|cook drain|green|frozen|\bground\b|tablespoon|teaspoon|cup|\bone\b|\btwo\b|\bthree\b|\bfour\b|\bfive\b|\bsix\b|\bseven\b|\beight\b|\bnine\b|\bten\b|\beleven\b|\btwelve\b|','',mention).strip()

  tokens = word_tokenize(mention)
  tags = nltk.pos_tag(tokens, tagset='universal')
  tokens_sentence = [wnl.lemmatize(tag[0]) if tag[1] == 'NOUN' else tag[0] for tag in tags]
  sentence = ' '.join(token for token in tokens_sentence)
  if sentence:
    return sentence
  else:
    return copy_mention.lower().strip()