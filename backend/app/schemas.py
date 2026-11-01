from pydantic import BaseModel, EmailStr, Field


class RegisterIn(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=6, max_length=72)


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class ProfileIn(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    bio: str = ""
    experience: int = Field(ge=1, le=5)
    availability: list[str] = []
    offered: list[str] = []
    wanted: list[str] = []


class ProfileOut(ProfileIn):
    id: int
    email: str
    setup_done: bool


class TokenOut(BaseModel):
    token: str
    user: ProfileOut


class PeerOut(BaseModel):
    id: int
    name: str
    experience: int
    rating: float
    rating_count: int
    offered: list[str]
    wanted: list[str]


class MatchOut(BaseModel):
    peer: PeerOut
    score: float
    parts: dict[str, float]
    reasons: list[str]
    request_status: str | None = None     # None, pending_out, pending_in, accepted, declined


class RequestIn(BaseModel):
    receiver_id: int


class RespondIn(BaseModel):
    action: str = Field(pattern="^(accept|decline)$")


class RequestOut(BaseModel):
    id: int
    direction: str                         # "in" or "out"
    status: str
    peer: PeerOut
    score: float
    reasons: list[str]


class SessionOut(BaseModel):
    id: int
    peer: PeerOut
    score: float
    reasons: list[str]
    shared_slots: list[str]
    slot: str | None
    completed: bool
    my_rating: int | None
    feedback: str


class ScheduleIn(BaseModel):
    slot: str


class RatingIn(BaseModel):
    score: int = Field(ge=1, le=5)
    feedback: str = Field(default="", max_length=500)
