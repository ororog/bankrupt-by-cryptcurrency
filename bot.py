from models import CryptCurrency, Price
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import random
import datetime

NOTIFY_SPAN = 1
NOTIFY_PERCENTAGE = 1

def main():
  engine = create_engine('sqlite:///./cryptcurrency.db')
  Session = sessionmaker(bind=engine)
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
      # if percentage > NOTIFY_PERCENTAGE:
      if True:
        currency.last_notified_at = price.updated
        session.commit()
        notify(currency, percentage, price.updated)
        break

# TODO
def notify(currency, percentage, from_date):
  image_path = get_random_image()
  output = '''
    {currency} で有り金全部溶かした人の顔です。
    {image}
    {currency} が{from_date}から {percentage}% 下落しました。
  '''.format(currency=currency.name,
             image=image_path,
             from_date=from_date.strftime('%m月%d日%H時%M分'),
             percentage=percentage)
  print(output)

def get_random_image():
  current_dir = os.path.abspath(os.path.dirname(__file__))
  image_paths = []
  for file in os.listdir('{}/images'.format(current_dir)):
    image_path = '{}/images/{}'.format(current_dir, file)
    if not os.path.isdir(image_path):
      image_paths.append(image_path)
  return random.choice(image_paths)


if __name__ == '__main__':
  main()
