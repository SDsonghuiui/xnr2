# -*-coding: utf-8-*-
import time
import sys
sys.path.append('..')

from sina.weibo_feedback_at import FeedbackAt
from sina.weibo_feedback_comment import FeedbackComment
from sina.weibo_feedback_follow import FeedbackFollow
from sina.weibo_feedback_like import FeedbackLike
from sina.weibo_feedback_private import FeedbackPrivate
from sina.weibo_feedback_retweet import FeedbackRetweet
from tools.Launcher import SinaLauncher

from weibo_publish_func import newest_time_func
from global_utils import es_xnr as es,weibo_xnr_index_name,weibo_xnr_index_type

def get_present_time():
    present_time_stamp = time.localtime(int(time.time()))
    present_time = time.strftime("%Y-%m-%d %H:%M:%S", present_time_stamp)
    year = int(present_time.split(" ")[0].split("-")[0])
    month = int(present_time.split(" ")[0].split("-")[1])
    day = int(present_time.split(" ")[0].split("-")[2])
    hour = int(present_time.split(" ")[1].split(":")[0])
    minute = int(present_time.split(" ")[1].split(":")[1])
    second = int(present_time.split(" ")[1].split(":")[2])
    return year, month, day, hour, minute, second

def execute(uname, upasswd):

    xnr = SinaLauncher(uname, upasswd)
    print xnr.login()
    print 'uname::',uname
    uid = xnr.uid
    current_ts = int(time.time())

    timestamp_retweet, timestamp_like, timestamp_at, timestamp_private, \
    timestamp_comment_receive, timestamp_comment_make = newest_time_func(xnr.uid)

    print timestamp_retweet, timestamp_like, timestamp_at, \
       timestamp_private, timestamp_comment_receive, timestamp_comment_make

    #try:
    print 'start run weibo_feedback_follow.py ...'
    fans, follow, groups = FeedbackFollow(xnr.uid, current_ts).execute()
    print 'run weibo_feedback_follow.py done!'
    # except:
    #     print 'Except Abort'
   
    #try:
    print 'start run weibo_feedback_at.py ...'
    FeedbackAt(xnr.uid, current_ts, fans, follow, groups, timestamp_at).execute()
    print 'run weibo_feedback_at.py done!'
    # except:
    #     print 'Except Abort'

    #try:
    print 'start run weibo_feedback_comment.py ...'
    FeedbackComment(xnr.uid, current_ts, fans, follow, groups, timestamp_comment_make, timestamp_comment_receive).execute()
    print 'run weibo_feedback_comment.py done!'
    # except:
    #     print 'Except Abort'

    # try:
    print 'start run weibo_feedback_like.py ...'
    FeedbackLike(xnr.uid, current_ts, fans, follow, groups, timestamp_like).execute()
    print 'run weibo_feedback_like.py done!'
    # except:
    #     print 'Except Abort'

    # try:
    print 'start run weibo_feedback_private.py ...'
    # print 'timestamp_private:::',timestamp_private
    # print 'current_ts::::::',current_ts
    FeedbackPrivate(xnr.uid, current_ts, fans, follow, groups, timestamp_private).execute()
    print 'run weibo_feedback_private.py done!'
    # except:
    #     print 'Except Abort'

    #try:
    print 'start run weibo_feedback_retweet.py ...'
    FeedbackRetweet(xnr.uid, current_ts, fans, follow, groups, timestamp_retweet).execute()
    print 'run weibo_feedback_retweet.py done!'
    # except:
        #print 'Except Abort'

def all_weibo_xnr_crawler():

	query_body = {
		'query':{'term':{'create_status':2}},
		'size':10000
	}

	search_results = es.search(index=weibo_xnr_index_name,doc_type=weibo_xnr_index_type,body=query_body)['hits']['hits']

	if search_results:
		for result in search_results:
			result = result['_source']
			mail_account = result['weibo_mail_account']
			phone_account = result['weibo_phone_account']
			pwd = result['password']
			if mail_account:
				account_name = mail_account
			elif phone_account:
				account_name = phone_account
			else:
				account_name = False

			if account_name:
				execute(account_name,pwd)
if __name__ == '__main__':

    year, month, day, hour, minute, second = get_present_time()
    #if hour >= 0 and hour <= 7:
    execute('weiboxnr01@126.com','xnr123456')
        #execute('weiboxnr02@126.com','xnr123456')
        #execute('weiboxnr03@126.com','xnr123456')
    execute('weiboxnr04@126.com','xnr1234567')
    start_ts = int(time.time())
    all_weibo_xnr_crawler()
    end_ts = int(time.time())
    print 'cost..',end_ts-start_ts
