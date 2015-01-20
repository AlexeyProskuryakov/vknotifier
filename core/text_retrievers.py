# coding:utf-8
__author__ = '4ikist'
import re

def retrieve_type(text):
    found = re.findall(u"(\!{1,3})", text, re.IGNORECASE)
    if found:
        groups = found[0]
        return len(groups)
    return 1

def retrieve_notification_message(text):
    found = re.findall(u".*\:\s(.*)",text)
    if found:
        return found[0].strip()

def retrieve_yes(text):
    found = re.findall(u"((да)|(ок)|(ok)|(yes)|(хорошо)|(\:\))|(\))|(ладно)|(давай)|(щл)|(lf))",text, re.IGNORECASE)
    if found:
        return True

if __name__ == '__main__':
    assert retrieve_type(u'hui') == 1
    assert retrieve_type(u'hui!') == 1
    assert retrieve_type(u'hui!!') == 2
    assert retrieve_type(u'hui!!!') == 3

    assert retrieve_notification_message(u"напомни мне в 22:30 что: тебе нужно пойти спать") == u"тебе нужно пойти спать"

    assert retrieve_yes(u"пиздец да!")
    assert retrieve_yes(u"пиздец хорошо!")
    assert retrieve_yes(u"ладно")
    assert retrieve_yes(u"ок")
    assert retrieve_yes(u"ok!")
    assert retrieve_yes(u"давай")
    assert retrieve_yes(u")")
    assert retrieve_yes(u":)")
    assert retrieve_yes(u"lf")

    assert not retrieve_yes(u'нет')