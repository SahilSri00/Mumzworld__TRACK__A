"""
Pydantic v2 schemas for request/response validation.

Every field is strictly typed. The LLM output is validated against these
schemas before being returned to the client — malformed output is caught
here, not silently swallowed.
"""

from __future__ import annotations
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator


# ── Enums ───────────────────────────────────────────────────────

class Priority(str, Enum):
    urgent = "urgent"
    high = "high"
    medium = "medium"
    low = "low"


class ItemCategory(str, Enum):
    diapering = "diapering"
    feeding = "feeding"
    clothing = "clothing"
    toys = "toys"
    gear = "gear"            # strollers, car seats, carriers
    nursery = "nursery"
    bath_skincare = "bath_skincare"
    health_safety = "health_safety"
    maternity = "maternity"
    party_celebration = "party_celebration"
    gift = "gift"
    books_learning = "books_learning"
    other = "other"


# ── Shopping Item ───────────────────────────────────────────────

class ShoppingItem(BaseModel):
    """A single parsed shopping item from the mom's message."""

    item_name: str = Field(
        ..., min_length=1,
        description="What the mom wants to buy, e.g. 'Diapers Size 3'"
    )
    category: ItemCategory = Field(
        ..., description="Product category on Mumzworld"
    )
    brand_preference: Optional[str] = Field(
        None, description="Brand if mentioned, else null"
    )
    size_or_age: Optional[str] = Field(
        None, description="Size, age range, or variant if mentioned"
    )
    quantity: Optional[str] = Field(
        None, description="Quantity if mentioned (e.g. '2', '2 boxes')"
    )
    budget_max_aed: Optional[str] = Field(
        None, description="Max budget in AED if mentioned (e.g. '250', '250 AED')"
    )
    priority: Priority = Field(
        default=Priority.medium,
        description="Urgency inferred from context"
    )
    search_query: str = Field(
        ..., min_length=1,
        description="Suggested Mumzworld search query for this item"
    )
    notes: Optional[str] = Field(
        None, description="Extra context from the message"
    )
    confidence: float = Field(
        ..., ge=0.0, le=1.0,
        description="How confident the model is about this extraction"
    )
    uncertainty_reason: Optional[str] = Field(
        None,
        description="If confidence < 0.6, explain what's unclear"
    )

    @field_validator('quantity', 'budget_max_aed', mode='before')
    @classmethod
    def coerce_to_str(cls, v):
        """LLMs sometimes return numbers instead of strings for these fields."""
        if v is None:
            return v
        return str(v)


# ── Calendar Event ──────────────────────────────────────────────

class CalendarEvent(BaseModel):
    """A date-bound event extracted from the message."""

    event_name: str = Field(..., min_length=1)
    event_type: str = Field(
        ..., description="birthday, milestone, delivery_deadline, appointment, other"
    )
    date_text: Optional[str] = Field(
        None,
        description="Date as mentioned by the mom, e.g. 'next month', 'June 15'"
    )
    estimated_date: Optional[str] = Field(
        None,
        description="ISO-8601 date if inferrable, else null"
    )
    related_items: list[str] = Field(
        default_factory=list,
        description="Shopping items linked to this event"
    )
    confidence: float = Field(..., ge=0.0, le=1.0)
    uncertainty_reason: Optional[str] = Field(None)


# ── Full Parse Response ─────────────────────────────────────────

class ParseResponse(BaseModel):
    """The complete structured output returned by the parser."""

    detected_language: str = Field(
        ..., description="ISO 639-1 code: 'en' or 'ar'"
    )
    original_message: str = Field(
        ..., description="The input message echoed back"
    )
    summary: str = Field(
        ..., min_length=1,
        description="One-sentence summary of what the mom needs, in the detected language"
    )
    shopping_items: list[ShoppingItem] = Field(default_factory=list)
    calendar_events: list[CalendarEvent] = Field(default_factory=list)
    overall_confidence: float = Field(
        ..., ge=0.0, le=1.0,
        description="Aggregate confidence across all extractions"
    )
    uncertainty_notes: list[str] = Field(
        default_factory=list,
        description="Top-level uncertainty flags for the whole parse"
    )
    is_out_of_scope: bool = Field(
        default=False,
        description="True if the message is not a shopping/parenting request"
    )
    out_of_scope_reason: Optional[str] = Field(
        None,
        description="Explanation if refusing to parse"
    )


# ── API Request ─────────────────────────────────────────────────

class ParseRequest(BaseModel):
    """Incoming request from the frontend."""
    message: str = Field(
        ..., min_length=1,
        description="The mom's text or voice-transcribed message"
    )
    language_hint: Optional[str] = Field(
        None, description="Optional language hint: 'en' or 'ar'"
    )
