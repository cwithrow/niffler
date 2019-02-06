import facebook
import config
import logging
import json
import os

def get_comments(obj_id, graph_obj):

    comments = graph_obj.request(obj_id+'/?fields=comments')

    for c in comments['comments']['data']:
        try:
            c['replies']=graph_obj.request(c['id']+'/?fields=comments')
        except KeyError():
            logging.error("get_comments error: No replies", exc_info=True)

    # print(comments)
    return comments






# Get comments while there are any



# How to store and attach to



def main():

    logging.basicConfig(level=logging.DEBUG,filename='app.log', filemode='w',
                        format='%(name)s - %(levelname)s - %(message)s')

# Create facebook graphAPI object to connect and retrieve data
# token and group Id set in config.py
    try:
        graph = facebook.GraphAPI(access_token=config.fb_token, version='3.1')
    except facebook.GraphAPIError:
        logging.error("facebook.GraphAPIError occurred", exc_info=True)

# May add date options to cl inputs, then could also be regularly run/updated
    date1 = '01/01/2019'
    date2 = '02/05/2019'

    if graph:
        try:
            posts = graph.request(config.group_id+'/?fields=feed.since('+date1+').until(' + date2 +')')
        except facebook.GraphAPIError:
            logging.error("facebook.GraphAPIError occurred", exc_info=True)

    if posts:

        try:
            for p in posts['feed']['data']:
                p['comments'] = get_comments(p['id'], graph)['comments']

        except facebook.GraphAPIError:
            logging.error("facebook.GraphAPIError occurred", exc_info=True)


# export to json/csv

    with open(os.path.join(config.output_path,'posts '+ date2.replace('/','_') +'.json'), 'w') as f:
        json.dump(posts, f)
#-------------------------------------#

if __name__ == '__main__':
    main()