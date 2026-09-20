from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# Enums
class UserRole(str, Enum):
    FARMER = "farmer"
    ADMIN = "admin"
    EXPERT = "expert"


class Language(str, Enum):
    ENGLISH = "en"
    HINDI = "hi"
    GUJARATI = "gu"


class CropType(str, Enum):
    WHEAT = "wheat"
    RICE = "rice"
    MAIZE = "maize"
    COTTON = "cotton"
    SUGARCANE = "sugarcane"
    SOYBEAN = "soybean"
    GROUNDNUT = "groundnut"
    MUSTARD = "mustard"
    BAJRA = "bajra"
    JOWAR = "jowar"
    TURMERIC = "turmeric"
    CHILLI = "chilli"
    TOMATO = "tomato"
    POTATO = "potato"
    ONION = "onion"
    OTHER = "other"


class SoilType(str, Enum):
    CLAY = "clay"
    SANDY = "sandy"
    LOAMY = "loamy"
    SILTY = "silty"
    PEATY = "peaty"
    CHALKY = "chalky"
    LATERITE = "laterite"
    BLACK = "black"
    RED = "red"
    ALLUVIAL = "alluvial"


class GrowthStage(str, Enum):
    SEEDLING = "seedling"
    VEGETATIVE = "vegetative"
    FLOWERING = "flowering"
    FRUITING = "fruiting"
    MATURITY = "maturity"
    HARVEST = "harvest"


# User Schemas
class UserBase(BaseModel):
    phone: str = Field(..., min_length=10, max_length=15)
    name: str = Field(..., min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    language: Language = Language.HINDI
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    farm_size: Optional[float] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    language: Optional[Language] = None
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    farm_size: Optional[float] = None


class UserResponse(UserBase):
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# Crop Schemas
class CropBase(BaseModel):
    name: str
    scientific_name: Optional[str] = None
    category: Optional[str] = None
    growing_season: Optional[str] = None
    description: Optional[str] = None
    ideal_ph_range: Optional[str] = None
    ideal_temp_range: Optional[str] = None


class CropCreate(CropBase):
    pass


class CropResponse(CropBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Disease Schemas
class DiseaseBase(BaseModel):
    name: str
    scientific_name: Optional[str] = None
    crop_id: int
    symptoms: str
    causes: Optional[str] = None
    treatment: str
    prevention: Optional[str] = None
    severity: Optional[str] = None
    image_url: Optional[str] = None


class DiseaseCreate(DiseaseBase):
    pass


class DiseaseResponse(DiseaseBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# UserCrop Schemas
class UserCropBase(BaseModel):
    crop_id: int
    area: Optional[float] = None
    planting_date: Optional[datetime] = None
    growth_stage: Optional[GrowthStage] = None
    soil_type: Optional[SoilType] = None
    notes: Optional[str] = None


class UserCropCreate(UserCropBase):
    pass


class UserCropUpdate(BaseModel):
    area: Optional[float] = None
    growth_stage: Optional[GrowthStage] = None
    soil_type: Optional[SoilType] = None
    notes: Optional[str] = None


class UserCropResponse(UserCropBase):
    id: int
    user_id: int
    crop: Optional[CropResponse] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Soil Analysis Schemas
class SoilAnalysisBase(BaseModel):
    crop_id: Optional[int] = None
    soil_type: SoilType
    ph: float = Field(..., ge=0, le=14)
    nitrogen: float = Field(..., ge=0)  # kg/ha
    phosphorus: float = Field(..., ge=0)  # kg/ha
    potassium: float = Field(..., ge=0)  # kg/ha
    organic_matter: Optional[float] = Field(None, ge=0, le=100)
    ec: Optional[float] = Field(None, ge=0)
    sulfur: Optional[float] = Field(None, ge=0)
    zinc: Optional[float] = Field(None, ge=0)
    boron: Optional[float] = Field(None, ge=0)
    iron: Optional[float] = Field(None, ge=0)
    manganese: Optional[float] = Field(None, ge=0)
    copper: Optional[float] = Field(None, ge=0)
    growth_stage: Optional[GrowthStage] = None


class SoilAnalysisCreate(SoilAnalysisBase):
    pass


class SoilAnalysisResponse(SoilAnalysisBase):
    id: int
    user_id: int
    recommendations: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class FertilizerRecommendation(BaseModel):
    fertilizer_name: str
    nutrient_content: Dict[str, float]  # e.g., {"N": 46, "P": 0, "K": 0}
    dosage_per_acre: float  # kg
    application_method: str  # basal, top_dressing, foliar
    timing: str  # e.g., "At sowing", "30 days after sowing"
    cost_estimate: Optional[float] = None  # INR per acre


class SoilRecommendationResponse(BaseModel):
    soil_health_score: float = Field(..., ge=0, le=100)
    nutrient_status: Dict[str, str]  # e.g., {"N": "Low", "P": "Medium", "K": "High"}
    ph_status: str  # "Acidic", "Neutral", "Alkaline"
    recommendations: List[FertilizerRecommendation]
    soil_amendments: List[str]
    general_advice: List[str]


# Weather Schemas
class WeatherCurrent(BaseModel):
    temperature: float  # °C
    humidity: float  # %
    rainfall: float  # mm
    wind_speed: float  # km/h
    wind_direction: Optional[str] = None
    pressure: Optional[float] = None  # hPa
    uv_index: Optional[float] = None
    condition: str  # sunny, cloudy, rainy, etc.
    description: str
    location: str
    recorded_at: datetime


class WeatherForecastDay(BaseModel):
    date: str
    temp_min: float
    temp_max: float
    humidity: float
    rainfall_probability: float
    rainfall_amount: float
    condition: str
    wind_speed: float


class WeatherForecast(BaseModel):
    location: str
    latitude: float
    longitude: float
    current: WeatherCurrent
    forecast: List[WeatherForecastDay]
    agricultural_advice: List[str]


# Chat Schemas
class ChatMessage(BaseModel):
    role: str  # user, assistant
    content: str
    language: Language = Language.HINDI
    metadata: Optional[Dict[str, Any]] = None


class ChatRequest(BaseModel):
    message: str
    language: Language = Language.HINDI
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None  # crop_id, location, weather, etc.


class ChatResponse(BaseModel):
    response: str
    language: Language
    session_id: str
    metadata: Optional[Dict[str, Any]] = None
    confidence: Optional[float] = None


# Disease Detection Schemas
class DiseasePredictionResult(BaseModel):
    disease_name: str
    confidence: float
    scientific_name: Optional[str] = None


class DiseasePredictRequest(BaseModel):
    crop_id: Optional[int] = None
    symptoms: Optional[str] = None


class DiseasePredictResponse(BaseModel):
    predictions: List[DiseasePredictionResult]
    top_prediction: DiseasePredictionResult
    symptoms_observed: Optional[str] = None
    ai_analysis: str
    recommended_actions: List[str]
    preventive_measures: List[str]
    warning: Optional[str] = None
    confidence_threshold: float = 0.7
    model: Optional[str] = None  # which engine produced the result (for transparency)
    display: Optional[str] = None  # raw model label (e.g. 'Tomato with Early Blight')


# Government Scheme Schemas
class SchemeDocumentBase(BaseModel):
    title: str
    source: Optional[str] = None
    scheme_name: Optional[str] = None
    scheme_type: Optional[str] = None
    language: Language = Language.HINDI


class SchemeDocumentCreate(SchemeDocumentBase):
    pass


class SchemeDocumentResponse(SchemeDocumentBase):
    id: int
    user_id: int
    file_path: Optional[str] = None
    is_processed: bool
    eligibility: Optional[str] = None
    benefits: Optional[str] = None
    required_documents: Optional[str] = None
    application_process: Optional[str] = None
    deadline: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SchemeQueryRequest(BaseModel):
    document_id: str  # uuid string from /upload (int legacy ids also accepted as str)
    question: str
    language: Language = Language.HINDI


class SchemeQueryResponse(BaseModel):
    question: str
    answer: str
    source_chunks: List[str]
    confidence: float
    language: Language
    disclaimer: str = "This information is extracted from the uploaded document. Please verify with official sources."


# Voice Schemas
class VoiceTranscribeRequest(BaseModel):
    language: Optional[Language] = None  # auto-detect if not provided


class VoiceTranscribeResponse(BaseModel):
    transcript: str
    detected_language: Language
    confidence: float


class VoiceSpeakRequest(BaseModel):
    text: str
    language: Language = Language.HINDI
    slow: bool = False


class VoiceSpeakResponse(BaseModel):
    audio_url: str
    duration_seconds: float


# Generic Response
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
    error: Optional[str] = None


class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    error: str
    details: Optional[Dict[str, Any]] = None