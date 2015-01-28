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
    found = re.findall(u".*\:\s(.*)", text)
    if found:
        return found[0].strip()


def retrieve_yes(text):
    found = re.findall(u"((да)|(ок)|(ok)|(yes)|(хорошо)|(\:\))|(\))|(ладно)|(давай)|(щл)|(lf))", text, re.IGNORECASE)
    if found:
        return True


def retrieve_utc(text):
    found = re.findall(u"[-+]?\d+", text)
    if found:
        return int(text)


def retrieve_set_utc(text):
    found = re.findall(u"(set utc )([-+]?\d+)", text)
    if found:
        groups = found[0]
        return int(groups[1])


def retrieve_mentioned(text):
    found = re.match(u"для\s(?P<names>.*)\sнапомни", text, re.IGNORECASE)
    if found:
        names_str = found.group('names')
        names = names_str.split(',')
        result = []
        for name in names:
            name = name.strip()
            if re.match(u'id\d+', name):
                result.append({'id': name[2:]})
            elif re.match(u'^[a-z0-9_\.]+$', name):
                result.append({'domain': name})
            else:
                result.append({'name': name.split()})
        return result


if __name__ == '__main__':
    assert retrieve_type(u'hui') == 1
    assert retrieve_type(u'hui!') == 1
    assert retrieve_type(u'hui!!') == 2
    assert retrieve_type(u'hui!!!') == 3

    assert retrieve_notification_message(
        u"напомни мне в 22:30 что: тебе нужно пойти спать") == u"тебе нужно пойти спать"

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

    assert retrieve_set_utc(u'set utc +6') == 6
    assert retrieve_set_utc(u'+6') == None
    assert retrieve_set_utc(u'-6') == None

    assert retrieve_utc(u'+6') == 6

    assert retrieve_mentioned(u"для 4ikist, sederfes напомни") == [{'domain': u'4ikist'}, {'domain': u'sederfes'}]
    assert retrieve_mentioned(u"для алины луценко напомни") == [{'name': [u'алины', u'луценко']}]
    assert retrieve_mentioned(u"для алины луценко напомни") == [{'name': [u'алины', u'луценко']}]

    assert retrieve_mentioned(u"для меня, enjoily prigmann напомни") == [{'name': [u'меня']},
                                                                    {'name': [u'enjoily', u'prigmann']}]
    assert retrieve_mentioned(u"для id12345, луценко напомни") == [{'id': u'12345'}, {'name': [u'луценко']}, ]
