# getFBSample.py
# Python 3.5, MacOS 10.14.2

import facebook
import config
import logging
import json
import os
import sys
import time
import argparse

class FBData():
    # def createFolder(self, dir):
    #     print(dir)
    #     new_path = os.path.join(config.output_path, '/' + dir)
    #     try:
    #         if not os.path.exists(new_path):
    #             os.makedirs(new_path)
    #     except OSError:
    #         print('Error: Creating directory. ' + new_path)

    def get_posts(self,graph_obj,beg_date, end_date,limit):
        print(config.output_path)
        print(os.path.join(config.output_path,end_date.replace('-', '_')))
        try:
            posts = graph_obj.request(config.group_id+'/?fields=feed.since('+beg_date+').until(' + end_date +')'
                                                '.limit('+limit+')')['feed']['data']
        except facebook.GraphAPIError:
            logging.error("facebook.GraphAPIError feed error", exc_info=True)
        else:
            for p in posts:
                # print(p.keys())
                p['post_id'] = p['id']
                p.pop('id', None)
                if 'message' in p:
                    p['post'] = p['message']
                    p.pop('message', None)

            # self.createFolder(end_date.replace('-', '_'))

            with open(os.path.join(config.output_path, end_date.replace('-', '_') + '/' +'posts' +
                    end_date.replace('-', '_') + '.json'), 'w') as f:
                json.dump(posts, f)

            print('%r posts saved\n ' % len(posts))
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
                    if 'message' in c:
                        c['comment'] = c['message']
                        c.pop('message', None)
            else:
                comments = []
        # print(comments)
            return comments

    def get_all_comments(self,posts_list, graph_obj, end_date, limit, delay):
        comments = []

        for p in posts_list:
            comments = comments + self.get_comments(p['post_id'], graph_obj, limit, delay)

        with open(os.path.join(config.output_path, end_date.replace('-', '_') + '/' + 'comments' +
                end_date.replace('-', '_') + '.json'), 'w') as f:
            json.dump(comments, f)

        print('%r comments saved\n ' % len(comments))

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
                    if 'message' in r:
                        r['reply'] = r['message']
                        r.pop('message', None)
            else:
                replies = []

            return replies

    def get_all_replies(self,comments_list, graph_obj, end_date, limit, delay):
        replies = []
        for c in comments_list:
            replies = replies + self.get_replies(c['post_id'], c['comm_id'], graph_obj, limit, delay)

        with open(os.path.join(config.output_path, end_date.replace('-', '_') + '/' +'replies' +
                end_date.replace('-', '_') + '.json'), 'w') as f:
            json.dump(replies, f)

        print('%r Replies saved\n ' % len(replies))

        return replies


    def get_all_data(self,graph_obj,beg_date, end_date,limit, delay=18):
        posts = self.get_posts(graph_obj,beg_date,end_date, limit)

        comments = self.get_all_comments(posts, graph_obj, end_date, limit, delay)

        replies = self.get_all_comments(comments, graph_obj, end_date, limit, delay)

        return posts, comments, replies

    def get_argparser(self):
        """
        Get the command line argument parser.
        """

        parser = argparse.ArgumentParser("FBData")
        parser.add_argument("--post_type",default='a', help="Type of post to get: 'a' for all, 'p' for posts, "
                                                             "'c' for comments, 'r' for replies")
        parser.add_argument("--beg_date", default=None, help= 'Beginning date in YYYY-MM-DD format' )
        parser.add_argument("--end_date", default=None, help= 'End date in YYYY-MM-DD format' )
        parser.add_argument("--input_path", default=config.output_path, help= 'Path for input file; required for c and r post_type')

        return parser

def main():

    fbd = FBData()

    parser = fbd.get_argparser()
    args = parser.parse_args()
    parser.add_argument("--app_id",
                        default=None, help="Facebook app id")

    #
    # date1 = '2019-02-01'
    # date2 = '2019-02-28'
    lim = '100'
    delay = 18

    # post_types: 'a' for all, 'p' for posts, 'c' for comments, 'r' for replies
    # post_type = 'r'
    #file path for input file for c or r post_types
    # inputfp = config.output_path

    # initialize logger
    logging.basicConfig(level=logging.DEBUG,filename='app.log', filemode='w',
                        format='%(name)s - %(levelname)s - %(message)s')

    logging.getLogger('urllib3').setLevel(logging.WARNING)

    if args is None:
        parser.print_help()
        sys.exit(1)

    else:
        # Load keys
        post_type = args.post_type
        date1 = args.beg_date
        date2 = args.end_date
        inputfp = args.input_path

        # Create facebook graphAPI object to connect and retrieve data
        # token and group Id set in config.py
        try:
            graph = facebook.GraphAPI(access_token=config.fb_token, version='3.1')
        except facebook.GraphAPIError:
            logging.error("facebook.GraphAPIError connection error", exc_info=True)
        else:

            if post_type == 'a':
             # Extract all tables
                fbd.get_all_data( graph, date1, date2, lim,delay)

            elif post_type == 'p':

                fbd.get_posts(graph, date1, date2, lim)

            elif post_type == 'c':
                with open(os.path.join(inputfp + '/' + date2.replace('-', '_') + '/' +'posts' +
                             date2.replace('-', '_') + '.json'), 'r') as f:
                    posts = json.load(f)
         # Extract data for comments table
                fbd.get_all_comments(posts,graph, date2, lim, delay)

            elif post_type == 'r':
                with open(os.path.join(inputfp +  '/' +  date2.replace('-', '_') + '/' + 'comments' +
                                               date2.replace('-', '_') + '.json'), 'r') as f:
                    comments = json.load(f)
                # Extract data for replies table
                fbd.get_all_replies(comments, graph, date2, lim, delay)






#-------------------------------------#

if __name__ == '__main__':
    main()