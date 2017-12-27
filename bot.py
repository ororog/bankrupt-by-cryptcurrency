from models import CryptCurrency, Price, get_engine
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from functools import lru_cache
import datetime
import os
import random
import requests
import textwrap
import twitter

NOTIFY_SPAN = 6
NOTIFY_PERCENTAGE = 10
CONSUMER_KEY=os.environ['TWITTER_CONSUMER_KEY']
CONSUMER_SECRET=os.environ['TWITTER_CONSUMER_SECRET']
TOKEN=os.environ['TWITTER_TOKEN']
TOKEN_SECRET=os.environ['TWITTER_TOKEN_SECRET']

def main():
  Session = sessionmaker(bind=get_engine())
  session = Session()

  currencies = session.query(CryptCurrency).all()

  JST = datetime.timezone(datetime.timedelta(hours=9), 'JST')
  from_date = datetime.datetime.now(JST) - datetime.timedelta(hours=NOTIFY_SPAN)

  for currency in currencies:
    from_date_for_currncy = from_date
    if (currency.last_notified_at is not None and
        currency.last_notified_at.timestamp() > from_date.timestamp()):
      from_date_for_currncy = currency.last_notified_at

    prices = session.query(Price).filter(
      Price.crypt_currency_id==currency.id).filter(
      Price.updated > from_date_for_currncy).order_by(
      Price.updated.desc()).all()

    current_price = None

    for price in prices:
      if current_price is None:
        current_price = price.price_usd

      percentage = (price.price_usd - current_price) / price.price_usd * 100
      if percentage > NOTIFY_PERCENTAGE:
        currency.last_notified_at = price.updated
        session.commit()
        notify(currency, price, percentage)
        break

def notify(currency, price, percentage):
  image_path = get_random_image()
  output = textwrap.dedent('''
    {currency.name} で有り金全部溶かした人の顔です。
    {currency.name} (https://coinmarketcap.com/currencies/{currency.id}) が{from_date}から {percentage}% 下落し、{price_jpy} 円になりました。
  ''').format(currency=currency,
             from_date=price.updated.strftime('%m月%d日%H時%M分'),
             price_jpy=round(get_usd_jpy() * price.price_usd, 2),
             percentage=round(percentage, 2)).strip()

  with open(image_path, "rb") as image_file:
    image_data=image_file.read()
    image_upload = twitter.Twitter(domain='upload.twitter.com',auth=auth)
    image_id = image_upload.media.upload(media=image_data)["media_id_string"]
    get_twitter_client().statuses.update(status=output, media_ids=",".join([image_id]))

  print(output)


def get_random_image():
  current_dir = os.path.abspath(os.path.dirname(__file__))
  image_paths = []
  for file in os.listdir('{}/images'.format(current_dir)):
    image_path = '{}/images/{}'.format(current_dir, file)
    if not os.path.isdir(image_path):
      image_paths.append(image_path)
  return random.choice(image_paths)


@lru_cache(maxsize=None)
def get_usd_jpy():
  pairs = requests.get('http://www.gaitameonline.com/rateaj/getrate').json()['quotes']
  return float([pair for pair in pairs if pair['currencyPairCode'] == 'USDJPY'][0]['ask'])


@lru_cache(maxsize=None)
def get_twitter_client():
  auth = twitter.OAuth(consumer_key=CONSUMER_KEY,
                       consumer_secret=CONSUMER_SECRET,
                       token=TOKEN,
                       token_secret=TOKEN_SECRET)

  twitter_client = twitter.Twitter(auth=auth)
  return twitter_client

if __name__ == '__main__':
  main()
