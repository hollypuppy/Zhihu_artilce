import requests
from lxml import etree
import json
import pandas as pd
import time

def crawler(url_token):
    global df_comments, df_child_comments
    comment_url = "https://www.zhihu.com/api/v4/comment_v5/articles/" + url_token + "/root_comment?"
    comment_text = requests.get(url=comment_url, headers=headers).text
    res = json.loads(comment_text)
    if res['data']:
        for comment in res['data']:
            answer_url = url_token
            comment_id = comment['id']
            comment_author_id = comment['author']['id']
            comment_author_url = comment['author']['url_token']
            content = comment['content']
            comment_created_time = comment['created_time']
            comment_upvote = comment['like_count']
            row = {
                'answer_url': [answer_url],
                'comment_id': [comment_id],
                'comment_author_id': [comment_author_id],
                'comment_author_url': [comment_author_url],
                'content': [content],
                'created_time': [comment_created_time],
                'comment_upvote': [comment_upvote]
            }
            df_comments = pd.concat([df_comments, pd.DataFrame(row)], axis=0, ignore_index=True)
            # child comments
            if comment['child_comments']:
                for child_comment in comment['child_comments']:
                    answer_url = url_token
                    comment_id = comment['id']
                    child_comment_id = child_comment['id']
                    child_comment_author_id = child_comment['author']['id']
                    child_comment_author_url = child_comment['author']['url_token']
                    child_comment_content = child_comment['content']
                    created_time = child_comment['created_time']
                    child_comment_upvote = child_comment['like_count']
                    child_comment_row = {
                        'answer_url': [answer_url],
                        'comment_id': [comment_id],
                        'child_comment_id': [child_comment_id],
                        'child_comment_author_id': [child_comment_author_id],
                        'child_comment_author_url': [child_comment_author_url],
                        'child_comment_content': [child_comment_content],
                        'created_time': [created_time],
                        'child_comment_upvote': [child_comment_upvote]
                    }
                    df_child_comments = pd.concat([df_child_comments, pd.DataFrame(child_comment_row)],
                                                  axis=0,
                                                  ignore_index=True)


if __name__ == "__main__":
    headers={
        "authority": "zhuanlan.zhihu.com",
        'scheme': 'https',
        #'Connection': 'close',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
        }
    df_comments = pd.DataFrame(
        columns=['answer_url', 'comment_id', 'comment_author_id', 'comment_author_url', 'content', 'created_time',
                 'comment_upvote'])
    df_child_comments = pd.DataFrame(
        columns=['answer_url', 'comment_id', 'child_comment_id', 'child_comment_author_id',
                 'child_comment_author_url', 'child_comment_content', 'created_time', 'child_comment_upvote'])

    df = pd.read_csv('./articles_0-250.csv')
    tokens = df['url_token'].tolist()
    i=1
    for url_token in tokens:
        url_token = str(url_token)
        crawler(url_token)
        print("已抓取第"+str(i)+"篇文章的评论")
        i+=1
        time.sleep(1)
    df_comments.to_csv('./comment.csv', mode='w', index=False, encoding="utf-8-sig")
    df_child_comments.to_csv('./child_comment.csv', mode='w', index=False, encoding="utf-8-sig")
