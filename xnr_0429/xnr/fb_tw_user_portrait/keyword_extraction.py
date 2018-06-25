# -*- coding: UTF-8 -*-
import os
import time
import re
import scws
import csv
import sys
import json
import random
from collections import Counter
from textrank4zh import TextRank4Keyword, TextRank4Sentence
from langconv import *
sys.path.append('../')
from global_config import S_DATE_FB, S_DATE_TW
from global_utils import es_xnr_2 as es, \
                         fb_portrait_index_name, fb_portrait_index_type, \
                         facebook_user_index_name, facebook_user_index_type, \
                         facebook_flow_text_index_name_pre, facebook_flow_text_index_type, \
                         fb_bci_index_name_pre, fb_bci_index_type, \
                         es_translation, translation_index_name, translation_index_type
from time_utils import get_facebook_flow_text_index_list, get_fb_bci_index_list, datetime2ts, ts2datetime
from parameter import MAX_SEARCH_SIZE, FB_TW_TOPIC_ABS_PATH, FB_DOMAIN_ABS_PATH, DAY, WEEK


sys.path.append(FB_TW_TOPIC_ABS_PATH)
from test_topic import topic_classfiy
from config import name_list, zh_data

tr4w = TextRank4Keyword()

#繁体转简体
def traditional2simplified(sentence):
    '''
    将sentence中的繁体字转为简体字
    :param sentence: 待转换的句子
    :return: 将句子中繁体字转换为简体字之后的句子
    '''
    sentence = Converter('zh-hans').convert(sentence)
    return sentence

#简体转繁体
def simplified2traditional(sentence):  
    sentence = Converter('zh-hant').convert(sentence)  
    return sentence  

def load_black_words():
    one_words = [line.strip('\r\n') for line in file('black.txt')]
    return one_words

black = load_black_words()
# 为了避免其他文件调用该.py文件的其他函数时，black.txt找不到，在get_filter_keywords()里面加载black。
# 因为目前外部只调用get_filter_keywords()函数。
# 好吧还是避免不了……拷贝一份到被调用的地方得了

def cut_filter(text):
    pattern_list = [r'\（分享自 .*\）', r'http://\w*']
    for i in pattern_list:
        p = re.compile(i)
        text = p.sub('', text)
    return text

def re_cut(w_text):#根据一些规则把无关内容过滤掉
    
    w_text = cut_filter(w_text)
    a1 = re.compile(r'回复' )
    w_text = a1.sub('',w_text)
    a1 = re.compile(r'\@.*?\:' )
    w_text = a1.sub('',w_text)
    a1 = re.compile(r'\@.*?\s' )
    w_text = a1.sub('',w_text)
    if w_text == u'转发微博':
        w_text = ''
    return w_text

def get_keyword(w_text, n_gram, n_count):
    tr4w.analyze(text=w_text, lower=True, window=n_gram)
    word_list = dict()
    k_dict = tr4w.get_keywords(n_count, word_min_len=2)
    for item in k_dict:
        if item.word.encode('utf-8').isdigit() or item.word.encode('utf-8') in black:
            continue
        word_list[item.word.encode('utf-8')] = item.weight
    return word_list

def get_weibo_single(text,n_gram=2,n_count=3):
    '''
        针对单条微博提取关键词，但是效率比较低
        输入数据：
        text：单条微博文本，utf-8编码
        n_gram：词语滑动窗口，建议取2
        n_count：返回的关键词数量
        输出数据：
        字典：键是词语，值是词语对应的权重
    '''
    w_text = re_cut(text)
    if w_text:
        w_key = get_keyword(w_text, n_gram, n_count)
        uid_word = w_key
    else:
        uid_word = dict()
    return uid_word

def get_weibo(text,n_gram=2,n_count=20):
    '''
        针对一批微博提取关键词
        输入数据：
        text：微博文本列表，utf-8编码
        n_gram：词语滑动窗口，建议取2
        n_count：返回的关键词数量
        输出数据：
        字典：键是词语，值是词语对应的权重
    '''
    text_str = ''
    for item in text:
        w_text = re_cut(item)
        if w_text:
            text_str = text_str + '。' + w_text
    if text_str:
        w_key = get_keyword(text_str, n_gram, n_count)
        uid_word = w_key
    else:
        uid_word = dict()
    return uid_word

def load_fb_flow_text(fb_flow_text_index_list, uid_list, fb_flow_text_query_body={}):
    if not fb_flow_text_query_body:
        fb_flow_text_query_body = {
            'query':{
                "filtered":{
                    "filter": {
                        "bool": {
                            "must": [
                                {"terms": {"uid": uid_list}},
                                {'range': {'flag_ch': {'gte': -1}}},
                            ]
                         }
                    }
                }
            },
            'size': MAX_SEARCH_SIZE,
            "sort": {"timestamp": {"order": "desc"}},
            "fields": ["text_ch", "uid"]
        }
    fb_flow_text = {}
    for index_name in fb_flow_text_index_list:
        try:
            search_results = es.search(index=index_name, doc_type=facebook_flow_text_index_type, body=fb_flow_text_query_body)['hits']['hits']
            for item in search_results:
                content = item['fields']
                uid = content['uid'][0]
                if not uid in fb_flow_text:
                    fb_flow_text[uid] = {
                        'text_dict': {}
                    }
                if content.has_key('text_ch'):
                    fb_flow_text[uid]['text_dict'][item['_id']] = traditional2simplified(content['text_ch'][0][:1800]) #对文本内容长度做出限制[:1800]，以免翻译时麻烦
                else:
                    fb_flow_text[uid]['text_dict'][item['_id']] = ''
        except Exception,e:
            print e
    #如果没有某个uid对应的记录值，则添上一条空的数据
    fb_flow_text_uid_list = fb_flow_text.keys() 
    for uid in uid_list:
        if not uid in fb_flow_text_uid_list:
            fb_flow_text[uid] = {
                'text_dict': {}
            }
    return fb_flow_text

def get_filter_keywords(fb_flow_text_index_list, uid_list):
    global black
    black = load_black_words()
    filter_keywords_result = {}
    fb_flow_text = load_fb_flow_text(fb_flow_text_index_list, uid_list)

    for uid, content in fb_flow_text.items():
        #对于一个用户的微博文本list，先随机抽取一定比例(k)的文章进行计算关键词，
        #如果没有结果则对其进行翻译，得到最终结果；反之，不用进行翻译直接进行重新计算得到最终结果
        text_dict = content['text_dict']
        #text_dict = {'mid1': text1, 'mid2': text2, ...}

        if len(text_dict):  #如果有内容的话，至少抽取一篇
            result = get_weibo(text_dict.values())

            filter_keywords_result[uid] = result
        else:
            filter_keywords_result[uid] = {}
    return filter_keywords_result

#提供给 计算new_xnr_flow_text_里面的topic_field_first字段 用
def get_filter_keywords_for_match_function(fb_flow_text_index_list, uid_list):
    global black
    black = load_black_words()
    filter_keywords_result = {}
    fb_flow_text_query_body = {
        'query':{
            "filtered":{
                "filter": {
                    "bool": {
                        "must": [
                            {"terms": {"uid": uid_list}},
                            {'range': {'flag_ch': {'gte': -1}}},
                        ],
                        "must_not": {
                            "exists": {
                                "field": "topic_field_first"
                            }
                        },
                    }
                }
            }
        },
        'size': 999,
        "sort": {"timestamp": {"order": "desc"}},
        "fields": ["text_ch", "uid"]
    }
    fb_flow_text = load_fb_flow_text(fb_flow_text_index_list, uid_list, fb_flow_text_query_body)

    for uid, content in fb_flow_text.items():
        filter_keywords_result[uid] = {}
        #对于一个用户的微博文本list，先随机抽取一定比例(k)的文章进行计算关键词，
        #如果没有结果则对其进行翻译，得到最终结果；反之，不用进行翻译直接进行重新计算得到最终结果
        text_dict = content['text_dict']
        #text_dict = {'mid1': text1, 'mid2': text2, ...}

        if len(text_dict):  #如果有内容的话，至少抽取一篇
            for mid,text in text_dict.items():
                result = get_weibo_single(text)
                if result:
                    filter_keywords_result[uid][mid] = result
                else:
                    filter_keywords_result[uid][mid] = {}
    return filter_keywords_result


if __name__ == '__main__':
    # uid_list = ['100010739386824']
    # type = 'test'
    # if type == 'test':
    #     timestamp =  datetime2ts(S_DATE_FB)
    # else:
    #     timestamp = time.time()
    # fb_flow_text_index_list = get_facebook_flow_text_index_list(timestamp)    #获取不包括今天在内的最近7天的表的index_name
    # res = get_filter_keywords(fb_flow_text_index_list, uid_list)
    # for uid, filter_keywords in res.items():
    #     print uid
    #     for key, val in filter_keywords.items():
    #         print key, val
    # load_black_words()
    # print load_fb_flow_text(['facebook_flow_text_2017-10-15'],['100012258524129'])
    print get_filter_keywords_for_match_function(['new_fb_xnr_flow_text_2017-10-15'],['100018797745111'])
