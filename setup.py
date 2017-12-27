from models import CryptCurrency, Price, get_engine, setup_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import requests

def main():
  setup_db()

  Session = sessionmaker(bind=get_engine())
  session = Session()

  response = requests.get('https://api.coinmarketcap.com/v1/ticker/')

  for data in response.json():
    id = data['id']
    name = data['name']
    symbol = data['symbol']
    currency = CryptCurrency(id=id, name=name, symbol=symbol)
    session.add(currency)

    session.flush()
    session.commit()


if __name__ == '__main__':
  main()
