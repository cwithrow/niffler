import facebook
import config
import logging
import json

def get_comments(obj_id, graph_obj):

    comments = graph_obj.request('obj_id/?fields=comments')






# Get comments while there are any



# How to store and attach to



def main():

    logging.basicConfig(level=logging.DEBUG,filename='app.log', filemode='w',
                        format='%(name)s - %(levelname)s - %(message)s')

    try:
        graph = facebook.GraphAPI(access_token=config.fb_token, version='3.1')
    except facebook.GraphAPIError:
        logging.error("facebook.GraphAPIError occurred", exc_info=True)

    date1 = '01/20/2019'
    date2 = '01/27/2019'

    if graph:
        try:
          posts = graph.request(config.group_id+'/?fields=feed.since('+date1+').until(' + date2 +')')
        except facebook.GraphAPIError:
            logging.error("facebook.GraphAPIError occurred", exc_info=True)

    if posts:

        print(len(posts['feed']['data']))
        # for p in posts['feed']['data']:
        #     p['comments'] = get_comments(p['id'])




if __name__ == '__main__':
    main()