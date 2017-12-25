from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
from sqlalchemy.orm import *

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

engine = create_engine('sqlite:///./cryptcurrency.db', echo=True)
Base.metadata.create_all(engine)
