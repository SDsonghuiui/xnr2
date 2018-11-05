# -*- coding:utf-8 -*-
import sys
import json
reload(sys)
sys.path.append('../../')

from global_utils import es_xnr as es, new_history_tw_xnr_flow_text_index_name,


def new_history_tw_xnr_flow_text_mappings(index_name):
    index_info = {
            'settings':{
                'analysis':{
                    'analyzer':{
                        'my_analyzer':{
                            'type': 'pattern',
                            'pattern': '&'
                        }
                    }
                }
            },
            'mappings':{
                'text':{
                    'properties':{
                        'history_date': {
                            'type': 'string',
                            'index': 'not_analyzed'
                        },
                        'task_source':{  # 日常发帖，热点跟随，业务发帖，此处空着
                            'type':'string',
                            'index':'not_analyzed'
                        },
                        'xnr_user_no':{ #虚拟人编号
                            'type':'string',
                            'index':'not_analyzed'
                        },
                        'uid':{ #虚拟人uid
                            'type':'string',
                            'index':'not_analyzed'
                        },
                        'text':{ #文本内容
                            'type': 'string',
                            'index': 'not_analyzed'
                            },
                        'picture_url':{ #图片url
                            'type':'string',
                            'index':'not_analyzed'
                        },
                        'vedio_url':{ #视频url
                            'type':'string',
                            'index':'not_analyzed'
                        },
                        'user_fansnum':{ #粉丝数
                            'type':'long'
                        },
                        'user_followersum':{ #关注者数
                            'type':'long'
                        },
                        'weibos_sum':{ #发帖总数
                            'type':'long'
                        },
                        'tid':{ #帖子id
                            'type': 'string',
                            'index': 'not_analyzed'
                            },
                        'ip':{ #IP地址
                            'type': 'string',
                            'index': 'not_analyzed'
                            },
                        'directed_uid':{#直接转发帖子的源uid
                            'type':'long',
                            },
                        'directed_uname':{#直接转发帖子的源用户昵称
                            'type': 'string',
                            'index': 'not_analyzed'
                            },
                        'timestamp':{#时间戳
                            'type': 'long'
                            },
                        'sentiment': {
                            'type': 'string',
                            'index': 'not_analyzed'
                            },
                        'geo':{#地理位置
                            'type': 'string',
                            'analyzer': 'my_analyzer'
                            },
                        'keywords_dict':{#关键词dict
                            'type': 'string',
                            'index': 'not_analyzed'
                            },
                        'keywords_string':{ #关键词string
                            'type': 'string',
                            'analyzer': 'my_analyzer'
                            },
                        'sensitive_words_dict':{#敏感词dict
                            'type': 'string',
                            'index': 'not_analyzed'
                            },
                        'sensitive_words_string':{#敏感词string
                            'type': 'string',
                            'analyzer': 'my_analyzer'
                            },
                        'message_type':{#数据类型，、原创——1、转发——2、评论——3
                            'type': 'long'
                            },
                        'root_uid':{#源头帖子的uid
                            'type': 'string',
                            'index': 'not_analyzed'
                            },
                        'root_tid':{#源头帖子的tid
                            'type': 'string',
                            'index': 'not_analyzed'
                            },
                         # uncut weibo text
                        'origin_text':{#源头帖子的文本
                            'type': 'string',
                            'index': 'not_analyzed'
                            },
                        'origin_keywords_dict':{#源头帖子的dict
                            'type': 'string',
                            'index': 'not_analyzed'
                            },
                        'origin_keywords_string':{#源头帖子的string
                            'type': 'string',
                            'analyzer': 'my_analyzer'
                            },
                        'comment':{#评论数
                            'type':'long'
                            },
                        'sensitive':{#敏感度
                            'type':'long'
                            },
                        'retweeted':{#转发数
                            'type':'long'
                            },
                        'like':{ #点赞数
                            'type':'long'
                        },
                        'topic_field_first': {
                            'index': 'not_analyzed',
                            'type': 'string'
                        },
                        'topic_field':{
                            'type':'string',
                            'index':'not_analyzed'
                        }
                        }
                    }
                }
            }
    exist_indice = es.indices.exists(index=index_name)
    if not exist_indice:
        es.indices.create(index=index_name, body=index_info, ignore=400)



if __name__ == '__main__':
    new_history_tw_xnr_flow_text_mappings(new_history_tw_xnr_flow_text_index_name)
