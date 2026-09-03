"""Shared Pydantic schemas for testing."""

from typing import Optional, List
from pydantic import BaseModel, Field


class PersonSchema(BaseModel):
    """Schema for person entities."""

    name: str = Field(description="Full name of the person")
    age: Optional[int] = Field(default=None, description="Age of the person")
    occupation: Optional[str] = Field(default=None, description="Job or profession")
    email: Optional[str] = Field(default=None, description="Email address")


class CompanySchema(BaseModel):
    """Schema for company entities."""

    name: str = Field(description="Company name")
    industry: Optional[str] = Field(default=None, description="Industry sector")
    founded_year: Optional[int] = Field(default=None, description="Year founded")
    headquarters: Optional[str] = Field(default=None, description="Headquarters location")


class EntitySchema(BaseModel):
    """Schema for graph entity/node extraction."""

    name: str = Field(description="Entity name")
    type: str = Field(description="Entity type (e.g., PERSON, ORGANIZATION, LOCATION)")
    properties: dict = Field(default_factory=dict, description="Additional properties")


class RelationSchema(BaseModel):
    """Schema for graph relation/edge extraction."""

    source: str = Field(description="Source entity name")
    target: str = Field(description="Target entity name")
    relation_type: str = Field(description="Type of relationship")
    description: Optional[str] = Field(default=None, description="Relationship description")


class KeywordSchema(BaseModel):
    """Schema for keyword extraction."""

    term: str = Field(description="Keyword or key phrase")
    category: Optional[str] = Field(default=None, description="Category or domain")
    frequency: Optional[int] = Field(default=None, description="Frequency count")


class ProductSchema(BaseModel):
    """Schema for product extraction."""

    name: str = Field(description="Product name")
    price: Optional[float] = Field(default=None, description="Product price")
    description: Optional[str] = Field(default=None, description="Product description")
    features: List[str] = Field(default_factory=list, description="List of features")


class BiographySchema(BaseModel):
    """Schema for biography/summary extraction."""

    name: str = Field(description="Person's full name")
    birth_date: Optional[str] = Field(default=None, description="Date of birth")
    death_date: Optional[str] = Field(default=None, description="Date of death")
    nationality: Optional[str] = Field(default=None, description="Nationality")
    occupation: List[str] = Field(default_factory=list, description="Professions/occupations")
    summary: str = Field(description="Brief biography summary")


class EarningsSummarySchema(BaseModel):
    """Schema for financial earnings summary."""

    company_name: str = Field(description="Company name")
    quarter: str = Field(description="Fiscal quarter (e.g., Q1 2024)")
    revenue: Optional[float] = Field(default=None, description="Revenue in millions")
    net_income: Optional[float] = Field(default=None, description="Net income in millions")
    earnings_per_share: Optional[float] = Field(default=None, description="EPS")
