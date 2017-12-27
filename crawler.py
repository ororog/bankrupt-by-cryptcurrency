from models import CryptCurrency, Price, get_engine
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime
import requests

def main():
  Session = sessionmaker(bind=get_engine())
  session = Session()

  response = requests.get('https://api.coinmarketcap.com/v1/ticker/')

  for data in response.json():
    price_usd = data['price_usd']
    updated = data['last_updated']
    crypt_currency_id = data['id']

    price = Price(price_usd=price_usd,
                  updated=datetime.datetime.fromtimestamp(int(updated)),
                  crypt_currency_id=crypt_currency_id)
    session.add(price)

  session.flush()
  session.commit()

if __name__ == '__main__':
  main()
