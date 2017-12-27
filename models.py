from functools import lru_cache
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import *
import os

DB_NAME='cryptcurrency.db'
Base = declarative_base()
class CryptCurrency(Base):
  __tablename__ = 'crypt_currency'
  id = Column(Text, primary_key=True)
  name = Column(Text)
  symbol = Column(Text)
  last_notified_at = Column(DateTime)
  prices = relationship('Price', backref='crypt_currency')

class Price(Base):
  __tablename__ = 'price'
  id = Column(Integer, primary_key=True)
  price_usd = Column(Float)
  updated = Column(DateTime)
  crypt_currency_id = Column(Text, ForeignKey('crypt_currency.id'))


@lru_cache(maxsize=None)
def get_engine(debug=False):
  return create_engine('sqlite:///{}/{}'.format(
    os.path.abspath(os.path.dirname(__file__)), DB_NAME), echo=debug)


def setup_db():
  Base.metadata.create_all(get_engine(debug=True))
