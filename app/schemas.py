#from __future__ import annotations

#from datetime import datetime
#from pydantic import BaseModel, EmailStr, Field


#from pydantic import BaseModel, EmailStr, Field

#class UserCreate(BaseModel):
 #   email: EmailStr
#    password: str = Field(min_length=8, max_length=72)


#class UserOut(BaseModel):
 #   id: int
 #   email: EmailStr
   # created_at: datetime

  #  class Config:
 #       from_attributes = True  # Pydantic v2


#class TokenOut(BaseModel):
 #   access_token: str
  #  token_type: str = "bearer"


#from typing import Optional, List


#class WishlistCreate(BaseModel):
  #  name: str = Field(min_length=1, max_length=100)
  #  description: Optional[str] = Field(default=None, max_length=500)


#class WishlistUpdate(BaseModel):
  #  name: Optional[str] = Field(default=None, min_length=1, max_length=100)
  #  description: Optional[str] = Field(default=None, max_length=500)


#class WishlistOut(BaseModel):
 #   id: int
  #  user_id: int
 #   name: str
  #  description: Optional[str]
 #   created_at: datetime

 #   class Config:
 #       from_attributes = True


#class WishlistItemCreate(BaseModel):
  #  destination_id: int
  #  notes: Optional[str] = Field(default=None, max_length=1000)
  #  priority: Optional[int] = Field(default=None, ge=0)


#class WishlistItemUpdate(BaseModel):
#   notes: Optional[str] = Field(default=None, max_length=1000)
 #   priority: Optional[int] = Field(default=None, ge=0)


#class DestinationOut(BaseModel):
 #   id: int
  #  name: str
  #  country: str
  #  continent: Optional[str] = None
  #  type: Optional[str] = None
 #   best_season: Optional[str] = None
  #  avg_cost_usd: Optional[float] = None
 #   rating: Optional[float] = None
  #  annual_visitors_m: Optional[float] = None
 #   unesco: Optional[bool] = None

  #  class Config:
  #      from_attributes = True


#class WishlistItemOut(BaseModel):
 #   id: int
 #   wishlist_id: int
  #  destination_id: int
  #  notes: Optional[str]
  #  priority: Optional[int]
 #   created_at: datetime
 #   destination: DestinationOut

  #  class Config:
   #     from_attributes = True