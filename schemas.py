"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogpost" collection
- Service -> "service" collection
- ContactMessage -> "contactmessage" collection
"""

from pydantic import BaseModel, Field, HttpUrl, EmailStr
from typing import Optional, List
from datetime import datetime

# Example schemas (replace with your own):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    address: Optional[str] = Field(None, description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in INR")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Portfolio-specific schemas

class Service(BaseModel):
    """Company Secretary service offerings"""
    title: str
    summary: str
    icon: Optional[str] = Field(None, description="Lucide icon name")
    starting_price: Optional[float] = Field(None, ge=0)
    tags: List[str] = []

class BlogPost(BaseModel):
    """Blog posts about compliance, ROC filings, GST, etc."""
    title: str
    slug: str
    excerpt: str
    content: str
    author: str = "Admin"
    cover_image: Optional[HttpUrl] = None
    tags: List[str] = []

class ContactMessage(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    subject: str
    message: str
    source: Optional[str] = None
    created_at: Optional[datetime] = None
