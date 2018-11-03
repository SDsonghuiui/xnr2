# -*-coding:utf-8-*-

import sys
import json
import time
reload(sys)
sys.path.append('../../')
from time_utils import ts2datetime,datetime2ts,ts2yeartime
from parameter import MAX_VALUE,DAY,WARMING_DAY
from global_config import S_TYPE,FACEBOOK_FLOW_START_DATE
from elasticsearch import Elasticsearch
from global_utils import es_xnr_2 as es,es_xnr
from global_utils import facebook_user_history_warning_index_name,facebook_user_history_warning_index_type,\
						facebook_event_history_warning_index_name,facebook_event_history_warning_index_type,\
						facebook_speech_history_warning_index_name,facebook_speech_history_warning_index_type



def facebook_user_history_warning_mappings():
	index_info = {
		'settings':{
			'number_of_replicas':0,
			'number_of_shards':5
		},
		'mappings':{
			facebook_user_history_warning_index_type:{
				'properties':{
					'xnr_user_no':{  # 虚拟人  
						'type':'string',
						'index':'not_analyzed'
					},
					'user_name':{    #预警用户昵称
						'type':'string',
						'index':'not_analyzed'
					},
					'uid':{     #预警用户id
						'type':'string',
						'index':'not_analyzed'
					},
					'user_sensitive':{  #预警用户敏感度
						'type':'long'
					},
					'validity':{   #用户预警有效性，有效1，无效-1
						'type':'long'
					},
					'content':{     #敏感言论内容
						'type':'string',
						'index':'not_analyzed'
					},
					'timestamp':{    #预警生成时间
						'type':'long'
					}
				}
			}
		}
	}

	if not es.indices.exists(index=facebook_user_history_warning_index_name):
		es.indices.create(index=facebook_user_history_warning_index_name,body=index_info,ignore=400)


def facebook_event_history_warning_mappings():
	index_info = {
		'settings':{
			'number_of_replicas':0,
			'number_of_shards':5
		},
		'mappings':{
			facebook_event_history_warning_index_type:{
				'properties':{
					'xnr_user_no':{  #虚拟人
						'type':'string',
						'index':'not_analyzed'
					},
					'event_name':{   #事件名称
						'type':'string',
						'index':'not_analyzed'
					},
					'main_user_info':{ #主要参与用户信息列表
						'type':'string',
						'index':'not_analyzed'
					},
					'event_time':{ #事件时间
						'type':'long'
					},
					'main_facebook_info':{ #典型微博信息
						'type':'string',
						'index':'not_analyzed'
					},
					'event_influence':{
						'type':'string',
						'index':'not_analyzed'
					},
					'validity':{   #预警有效性，有效1，无效-1
						'type':'long'
					},
					'timestamp':{
						'type':'long'
					}
				}
			}
		}
	}

	if not es.indices.exists(index=facebook_event_history_warning_index_name):
		es.indices.create(index=facebook_event_history_warning_index_name,body=index_info,ignore=400)


def facebook_speech_history_warning_mappings():
	index_info = {
		'settings':{
			'number_of_replicas':0,
			'number_of_shards':5,
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
			facebook_speech_history_warning_index_type:{
				'properties':{
					'xnr_user_no':{
						'type':'string',
						'index':'not_analyzed'
					},
					'content_type':{  # friends - 好友，unfriends - 非好友
						'type':'string',
						'index':'not_analyzed'
					},					
					'validity':{   #预警有效性，有效1，无效-1
						'type':'long'
					},
					'timestamp':{
						'type':'long'
					},
					'uid':{ 
						'type':'string',
						'index':'not_analyzed'
					},
					'sensitive':{
						'type':'long'
					},	
					'sentiment':{ 
						'type':'string',
						'index':'not_analyzed'
					},
					'sensitive_words_string':{
						'type': 'string',
						'analyzer': 'my_analyzer'
					},
					'text':{ 
						'type':'string',
						'index':'not_analyzed'
					},
					'fid':{
						'type':'string',
						'index':'not_analyzed'
					},
					'keywords_string':{
						'type': 'string',
						'analyzer': 'my_analyzer'
					},
					'sensitive_words_dict':{
						'type': 'string',
						'index': 'not_analyzed'
					},
					'keywords_dict':{
						'type': 'string',
						'index': 'not_analyzed'
					},
					'share':{
						'type':'long'
					},
					'comment':{
						'type':'long'
					},
					'favorite':{
						'type':'long'
					},
					'nick_name':{
						'type':'string',
						'index':'not_analyzed'
					}
				}
			}
		}
	}

	if not es.indices.exists(index=facebook_speech_history_warning_index_name):
		es.indices.create(index=facebook_speech_history_warning_index_name,body=index_info,ignore=400)




if __name__ == '__main__':
	facebook_user_history_warning_mappings()
	facebook_event_history_warning_mappings()
	facebook_speech_history_warning_mappings()



