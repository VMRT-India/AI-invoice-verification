"""
Database models for Invoice and PO verification system
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import config

Base = declarative_base()


class Invoice(Base):
    __tablename__ = 'invoices'

    id = Column(Integer, primary_key=True, autoincrement=True)
    invoice_number = Column(String(100), unique=True, nullable=False)
    vendor_name = Column(String(200), nullable=False)
    invoice_date = Column(DateTime, nullable=False)
    total_amount = Column(Float, nullable=False)
    currency = Column(String(10), default='USD')
    tax_amount = Column(Float, default=0.0)
    subtotal = Column(Float, nullable=False)
    file_path = Column(String(500), nullable=False)
    extracted_text = Column(Text)
    processing_status = Column(String(50), default='pending')  # pending, processed, error
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PurchaseOrder(Base):
    __tablename__ = 'purchase_orders'

    id = Column(Integer, primary_key=True, autoincrement=True)
    po_number = Column(String(100), unique=True, nullable=False)
    vendor_name = Column(String(200), nullable=False)
    po_date = Column(DateTime, nullable=False)
    total_amount = Column(Float, nullable=False)
    currency = Column(String(10), default='USD')
    file_path = Column(String(500), nullable=False)
    extracted_text = Column(Text)
    processing_status = Column(String(50), default='pending')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class InvoiceLineItem(Base):
    __tablename__ = 'invoice_line_items'

    id = Column(Integer, primary_key=True, autoincrement=True)
    invoice_id = Column(Integer, nullable=False)
    invoice_number = Column(String(100), nullable=False)
    item_description = Column(String(500), nullable=False)
    quantity = Column(Float, nullable=False)
    unit_price = Column(Float, nullable=False)
    line_total = Column(Float, nullable=False)
    item_code = Column(String(100))
    unit = Column(String(50), default='pcs')


class POLineItem(Base):
    __tablename__ = 'po_line_items'

    id = Column(Integer, primary_key=True, autoincrement=True)
    po_id = Column(Integer, nullable=False)
    po_number = Column(String(100), nullable=False)
    item_description = Column(String(500), nullable=False)
    quantity = Column(Float, nullable=False)
    unit_price = Column(Float, nullable=False)
    line_total = Column(Float, nullable=False)
    item_code = Column(String(100))
    unit = Column(String(50), default='pcs')


class MatchResult(Base):
    __tablename__ = 'match_results'

    id = Column(Integer, primary_key=True, autoincrement=True)
    invoice_number = Column(String(100), nullable=False)
    po_number = Column(String(100), nullable=False)
    match_status = Column(String(50), nullable=False)  # matched, discrepancy, not_found
    match_score = Column(Float, default=0.0)  # 0-100
    vendor_match = Column(Boolean, default=False)
    amount_match = Column(Boolean, default=False)
    quantity_match = Column(Boolean, default=False)
    discrepancies = Column(Text)  # JSON string of discrepancies
    created_at = Column(DateTime, default=datetime.utcnow)


# Database initialization
def init_database():
    """Initialize database and create tables"""
    engine = create_engine(f'sqlite:///{config.DATABASE_PATH}')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


def get_session():
    """Get database session"""
    engine = create_engine(f'sqlite:///{config.DATABASE_PATH}')
    Session = sessionmaker(bind=engine)
    return Session()
