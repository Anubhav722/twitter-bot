import tweepy
import os
import requests
import json
from datetime import datetime
from pyshorteners import Shortener
import random

def get_env_variable(var_name):
    """
    Get an environment variable or raise exception
    """
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = "Set the {} environment variable".format(var_name)
        raise Exception(error_msg)

CONSUMER_KEY = get_env_variable('CONSUMER_KEY')
CONSUMER_SECRET = get_env_variable('CONSUMER_SECRET')
ACCESS_TOKEN = get_env_variable('ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = get_env_variable('ACCESS_TOKEN_SECRET')
AIRCTO_HOST = get_env_variable('AIRCTO_HOST')
GOOGLE_SHORTENER_API_KEY = get_env_variable('GOOGLE_SHORTENER_API_KEY')

MESSAGES = [
    "{} is looking out for an awesome {}.",
    "Do you code even in your dreams? Join {} as a {}.",
    "Is coding your passion? {} is looking out for {}."
]

hashtags = {
    "Data Scientist": "#BigData #ML #AI #jobs",
    "Software Architect": "#jobs #IT #aws #career",
    "Backend Developer": "#backend #jobs #IT #python",
    "Frontend Developer": "#tech #Jobs #FrontEnd #Angular",
    "Fulstack Developer": "#fullstack #developer #jobs",
    "DevOps Engineer": "#jobs #cloud #devops #aws",
    "QA Engineer": "#qa #jobs #IT #Testing",
    "Android Developer": "#android #jobs #java #ios",
    "iOS Developer": "#jobs #swift #ios #mobile"
}

def get_short_url(url):
    shortener = Shortener('Google', api_key=GOOGLE_SHORTENER_API_KEY, timeout=1)
    return shortener.short(url)

def get_messages(job_title, company_name):
    global MESSAGES
    return random.choice(MESSAGES).format(company_name, job_title)

# OAuth process, using the keys and tokens
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
 
# Creation of the actual interface, using authentication
api = tweepy.API(auth)

def fetch_jobs():
    data = requests.get('https://api.aircto.com/api/v1/external/jobs/?limit=100000')
    data = data.content.decode('utf-8')
    jobs = json.loads(data)['data']
    return jobs

def get_structured_data_for_jobs():
    jobs = fetch_jobs()
    job = random.choice([a for a in jobs if (datetime.now().date() - (datetime.strptime(a.get('updated_at').split('T')[0], '%Y-%m-%d')).date()).days <= 14])

    job_id = job.get('id')
    company_slug = job.get('slug')
    job_category_slug = job.get('category').get('slug')
    JOB_DETAIL_URL = AIRCTO_HOST + 'jobs/' + job_category_slug + '/' + str(job_id)
    job_elements = {
            "job_title": job.get('title'),
            "job_location": job.get('location'),
            "company_name": job.get('company').get('name'),
            "job_category_name": job.get('category').get('name'),
            "job_detail_url": get_short_url(JOB_DETAIL_URL),
            "hashtags": hashtags.get(job.get('category').get('name'))}
    return job_elements

def get_job(job):
    message = get_messages(job['job_title'], job['company_name'])
    message = message + " {} {}".format(job['job_detail_url'], job['hashtags'])
    return message

# Send the tweet.
def tweet_jobs(message):
    print("Tweeting now")
    try:
        # print(message)
        api.update_status(message, tweet_mode='extended')
    except tweepy.error.TweepError as e:
        print (e)
        job_data = get_structured_data_for_jobs()
        message = get_job(job_data)
        tweet_jobs(message)

job_data = get_structured_data_for_jobs()
message = get_job(job_data)
tweet_jobs(message)
