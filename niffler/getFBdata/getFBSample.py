# getFBSample.py
# Python 3.5, MacOS 10.14.2

import facebook
import config
import logging
import json
import os
import time


class FBSample():

    def get_comments(self,obj_id, graph_obj, limit, delay):
        # to prevent rate limit problems
        time.sleep(delay)
        try:
            comments = graph_obj.request(obj_id + '/?fields=comments')
        except facebook.GraphAPIError():
            logging.error("Graph API comments error", exc_info=True)

        if 'comments' in comments.keys():
            comments = comments['comments']['data']
            for c in comments:
                try:
                    time.sleep(delay)
                    replies= graph_obj.request(c['id'] + '/?fields=comments.limit('+ limit + ')')
                    if 'comments' in replies.keys():
                        c['replies'] = replies['comments']['data']

                except facebook.GraphAPIError():
                    logging.error("Graph API replies error", exc_info=True)

        # print(comments)
        return comments

    def get_data(self,graph_obj,beg_date, end_date,limit, delay=18):
        try:
            posts = graph_obj.request(config.group_id+'/?fields=feed.since('+beg_date+').until(' + end_date +').limit('+limit+')')
        except facebook.GraphAPIError:
            logging.error("facebook.GraphAPIError feed error", exc_info=True)
        else:
            for p in posts['feed']['data']:
                p['comments'] = self.get_comments(p['id'], graph_obj, limit, delay)
            return posts

def main():
    date1 = '2019-02-01'
    date2 = '2019-02-03'
    lim = '100'
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
        fbd = FBSample()
        data = fbd.get_data( graph, date1, date2, lim)

    # export to json/csv
        with open(os.path.join(config.output_path,'full_'+ date2.replace('/','_') +'.json'), 'w') as f:
            json.dump(data['feed']['data'], f)

#-------------------------------------#

if __name__ == '__main__':
    main()