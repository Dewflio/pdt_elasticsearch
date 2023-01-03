# SCHEMA FROM POSTGRES
#
# conversation_id       - row[0]
# author_id             - row[1]
# content               - row[2]
# possibly_sensitive    - row[3]
# language              - row[4]
# source                - row[5]
# retweet_count         - row[6]
# reply_count           - row[7]
# like_count            - row[8]
# quota_count           - row[9]
# created_at            - row[10]
# author_name           - row[11]
# author_username       - row[12]
# author_description    - row[13]
# author_followers_count- row[14]
# author_following_count- row[15]
# author_tweet_count    - row[16]
# author_listed_count   - row[17]
# annotations_id        - row[18]   - ARRAY
# annotations_values    - row[19]   - ARRAY
# annotations_types     - row[20]   - ARRAY
# annotations_probabilites- row[21] - ARRAY
# domain_ids            - row[22]   - ARRAY
# domain_names          - row[23]   - ARRAY
# domain_descriptions   - row[24]   - ARRAY
# entity_ids            - row[25]   - ARRAY
# entity_names          - row[26]   - ARRAY
# entity_descriptions   - row[27]   - ARRAY
# link_ids              - row[28]   - ARRAY
# link_titles           - row[29]   - ARRAY
# link_urls             - row[30]   - ARRAY
# link_descriptions     - row[31]   - ARRAY
# hashtag_ids           - row[32]   - ARRAY
# hashtag_tags          - row[33]   - ARRAY
# conversation_reference_parent_ids - row[34] - ARRAY
# conversation_reference_types      - row[35] - ARRAY


import psycopg2
from elasticsearch import Elasticsearch
from elasticsearch import helpers
from datetime import datetime
import pprint

conn = psycopg2.connect(
   database="pdt_tweets", user='postgres', password='postgres', host='127.0.0.1', port= '5432'
)
cursor = conn.cursor()
cursor.execute("SELECT * FROM denormalized_tweets LIMIT 10")

es = Elasticsearch(hosts=['http://localhost:9200'])

BLOKSIZE = 10000
import_arr = []
counter = 0

for row in cursor:
    # init a new json record
    record = {}
    # set up the _index and _id of the record
    record['_index'] = 'tweet_index'
    record['_id'] = str(row[0])
    # set up fields
    record['author'] = {}
    record['tweet_info'] = {}
    record['annotations'] = []
    record['context_domains'] = []
    record['context_entities'] = []
    record['links'] = []
    record['hashtags'] = []
    record['conversation_references'] = []
    # author
    
    record['author']['id'] = row[1]
    if row[11] != None:
        record['author']['name'] = row[11]
    if row[12] != None:
        record['author']['username'] = row[12]
    if row[13] != None:
        record['author']['description'] = row[13]
    if row[14] != None:
        record['author']['followers_count'] = row[14]
    if row[15] != None:
        record['author']['following_count'] = row[15]
    if row[16] != None:
        record['author']['tweet_count'] = row[16]
    if row[17] != None:
        record['author']['listed_count'] = row[17]
    # tweet_info
    record['tweet_info']['id'] = row[0]
    record['tweet_info']['content'] = row[2]
    record['tweet_info']['possibly_sensitive'] = row[3]
    record['tweet_info']['language'] = row[4]
    record['tweet_info']['source'] = row[5]
    
    if row[6] != None:
        record['tweet_info']['retweet_count'] = row[6]
    if row[7] != None:
        record['tweet_info']['reply_count'] = row[7]
    if row[8] != None:
        record['tweet_info']['like_count'] = row[8]
    if row[9] != None:
        record['tweet_info']['quote_count'] = row[9]
    record['tweet_info']['created_at'] = datetime.strftime(row[10].replace(tzinfo=None), '%Y-%m-%d %H:%M:%S')
    # annotations
    if row[18] != None:
        for i in range(len(row[18])):
            new_annotation = {}
            if row[18][i] != None:
                new_annotation['id'] = row[18][i]
            if row[19][i] != None:
                new_annotation['value'] = row[19][i]
            if row[20][i] != None:
                new_annotation['type'] = row[20][i]
            if row[21][i] != None:
                new_annotation['probability'] = row[21][i]   #DECIMAL
            record['annotations'].append(new_annotation)
    # context_domains
    if row[22] != None:
        for i in range(len(row[22])):
            new_cont_domain = {}
            if row[22][i] != None:
                new_cont_domain['id'] = row[22][i]
            if row[23][i] != None:
                new_cont_domain['name'] = row[23][i]
            if row[23][i] != None:
                new_cont_domain['description'] = row[24][i]
            record['context_domains'].append(new_cont_domain)
    # context_entities
    if row[25] != None:
        for i in range(len(row[25])):
            new_cont_entity = {}
            if row[25][i] != None:
                new_cont_entity['id'] = row[25][i]
            if row[26][i] != None:
                new_cont_entity['name'] = row[26][i]
            if row[27][i] != None:
                new_cont_entity['description'] = row[27][i]
            record['context_entities'].append(new_cont_entity)
    # links
    if row[28] != None:
        for i in range(len(row[28])):
            new_link = {}
            if row[28][i] != None:
                new_link['id'] = row[28][i]
            if row[29][i] != None:
                new_link['title'] = row[29][i]
            if row[30][i] != None:
                new_link['url'] = row[30][i]
            if row[31][i] != None:
                new_link['description'] = row[31][i]
            record['links'].append(new_link)
    #hashtags
    if row[32] != None:
        for i in range(len(row[32])):
            new_hashtag = {}
            if row[32][i] != None:
                new_hashtag['id'] = row[32][i]
            if row[33][i] != None:
                new_hashtag['tag'] = row[33][i]
            record['hashtags'].append(new_hashtag)
    #conv references
    if row[34] != None:
        for i in range(len(row[34])):
            new_conv_ref = {}
            new_conv_ref['conversation_id'] = row[0]
            if row[34][i] != None:
                new_conv_ref['parent_id'] = row[34][i]
            if row[35][i] != None:
                new_conv_ref['reference_type'] = row[35][i]
            record['conversation_references'].append(new_conv_ref)

    counter +=1
    import_arr.append(record)
    pprint.pprint(record)
    if counter % BLOKSIZE == 0:
        helpers.bulk(es, import_arr)
        print(counter)
        import_arr = []

if import_arr != []:
    helpers.bulk(es, import_arr)
    print(counter)


    






