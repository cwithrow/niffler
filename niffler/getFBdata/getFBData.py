# getFBSample.py
# Python 3.5, MacOS 10.14.2

import facebook
import config
import logging
import json
import os
import time


class FBData():

    def get_posts(self,graph_obj,beg_date, end_date,limit):

        try:
            posts = graph_obj.request(config.group_id+'/?fields=feed.since('+beg_date+').until(' + end_date +')'
                                                '.limit('+limit+')')['feed']['data']
        except facebook.GraphAPIError:
            logging.error("facebook.GraphAPIError feed error", exc_info=True)
        else:
            for p in posts:
                p['post_id'] = p['id']
                p.pop('id', None)
                p['post'] = p['message']
                p.pop('message', None)
            return posts

    def get_comments(self, obj_id, graph_obj, limit, delay):
        # to prevent rate limit problems
        time.sleep(delay)
        try:
            comments= graph_obj.request(obj_id + '/?fields=comments.limit(' + limit + ')')
        except facebook.GraphAPIError():
            logging.error("Graph API comments error", exc_info=True)

        else:
            if 'comments' in comments.keys():
                comments = comments['comments']['data']
                for c in comments:
                    c['post_id'] = obj_id
                    c['comm_id'] = c['id']
                    c.pop('id', None)
                    c['comment'] = c['message']
                    c.pop('message', None)
            else:
                comments = []
        # print(comments)
            return comments

    def get_replies(self,post_id,obj_id, graph_obj, limit, delay):
        time.sleep(delay)
        try:
            replies = graph_obj.request(obj_id + '/?fields=comments.limit(' + limit + ')')
        except facebook.GraphAPIError():
            logging.error("Graph API replies error", exc_info=True)
        else:
            if 'comments' in replies.keys():
                replies = replies['comments']['data']
                for r in replies:
                    r['post_id'] = post_id
                    r['comm_id'] = obj_id
                    r['rep_id'] = r['id']
                    r.pop('id', None)
                    r['reply'] = r['message']
                    r.pop('message', None)
            else:
                replies = []

            return replies


    def get_data(self,graph_obj,beg_date, end_date,limit, delay=18):
        posts = self.get_posts(graph_obj,beg_date,end_date, limit, delay)


        comments = []
        replies = []
        for p in posts:
            comments = comments + self.get_comments(p['post_id'], graph_obj, limit, delay)

        for c in comments:
            replies = replies + self.get_replies(c['post_id'],c['comm_id'],graph_obj,limit,delay)

        return posts, comments, replies

def main():
    date1 = '2019-02-01'
    date2 = '2019-02-28'
    lim = '100'
    delay = 18
    # initialize logger
    logging.basicConfig(level=logging.DEBUG,filename='app.log', filemode='w',
                        format='%(name)s - %(levelname)s - %(message)s')

# Create facebook graphAPI object to connect and retrieve data
# token and group Id set in config.py
    try:
        graph = facebook.GraphAPI(access_token=config.fb_token, version='3.1')
    except facebook.GraphAPIError:
        logging.error("facebook.GraphAPIError connection error", exc_info=True)
    else:
        fbd = FBData()
    # Extract data for posts table
    #     posts_list, comments_list, replies_list = fbd.get_data( graph, date1, date2, lim,delay)

        posts = fbd.get_posts(graph, date1, date2, lim)

        with open(os.path.join(config.output_path, 'posts' + date2.replace('/', '_') + '.json'), 'w') as f:
            json.dump(posts, f)

        print('Posts saved\n ')

    # Extract data for comments table
        comments = []

        for p in posts:
            comments = comments + fbd.get_comments(p['post_id'], graph, lim, delay)

        with open(os.path.join(config.output_path, 'comments' + date2.replace('/', '_') + '.json'), 'w') as f:
            json.dump(comments, f)

        print('Comments saved\n ')

    # Extract data for replies table
        replies = []
        for c in comments:
            replies = replies + fbd.get_replies(c['post_id'], c['comm_id'], graph, lim, delay)

        with open(os.path.join(config.output_path,'replies'+ date2.replace('/','_') +'.json'), 'w') as f:
            json.dump(replies, f)

        print('Replies saved\n ')
#-------------------------------------#

if __name__ == '__main__':
    main()