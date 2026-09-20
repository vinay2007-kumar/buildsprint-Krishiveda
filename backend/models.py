from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Text, ForeignKey, Enum, Boolean, JSON
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
from datetime import datetime
import enum

Base = declarative_base()


class UserRole(str, enum.Enum):
    FARMER = "farmer"
    ADMIN = "admin"
    EXPERT = "expert"


class Language(str, enum.Enum):
    ENGLISH = "en"
    HINDI = "hi"
    GUJARATI = "gu"


class CropType(str, enum.Enum):
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


class SoilType(str, enum.Enum):
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


class GrowthStage(str, enum.Enum):
    SEEDLING = "seedling"
    VEGETATIVE = "vegetative"
    FLOWERING = "flowering"
    FRUITING = "fruiting"
    MATURITY = "maturity"
    HARVEST = "harvest"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=True)
    hashed_password = Column(String(255), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.FARMER)
    language = Column(Enum(Language), default=Language.HINDI)
    location = Column(String(200), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    farm_size = Column(Float, nullable=True)  # in acres
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    crops = relationship("UserCrop", back_populates="user")
    soil_analyses = relationship("SoilAnalysis", back_populates="user")
    chat_history = relationship("ChatHistory", back_populates="user")
    disease_predictions = relationship("DiseasePrediction", back_populates="user")
    scheme_documents = relationship("SchemeDocument", back_populates="user")


class Crop(Base):
    __tablename__ = "crops"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    scientific_name = Column(String(100), nullable=True)
    category = Column(String(50), nullable=True)  # cereal, pulse, oilseed, vegetable, fruit
    growing_season = Column(String(50), nullable=True)  # kharif, rabi, zaid
    description = Column(Text, nullable=True)
    common_diseases = Column(JSON, nullable=True)  # list of disease IDs
    nutrient_requirements = Column(JSON, nullable=True)  # N, P, K requirements per stage
    water_requirements = Column(JSON, nullable=True)  # mm per stage
    ideal_ph_range = Column(String(20), nullable=True)  # e.g., "6.0-7.0"
    ideal_temp_range = Column(String(20), nullable=True)  # e.g., "20-30°C"
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user_crops = relationship("UserCrop", back_populates="crop")
    diseases = relationship("Disease", back_populates="crop")


class Disease(Base):
    __tablename__ = "diseases"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    scientific_name = Column(String(100), nullable=True)
    crop_id = Column(Integer, ForeignKey("crops.id"), nullable=False)
    symptoms = Column(Text, nullable=False)
    causes = Column(Text, nullable=True)
    treatment = Column(Text, nullable=False)
    prevention = Column(Text, nullable=True)
    severity = Column(String(20), nullable=True)  # low, medium, high, critical
    image_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    crop = relationship("Crop", back_populates="diseases")
    predictions = relationship("DiseasePrediction", back_populates="disease")


class UserCrop(Base):
    __tablename__ = "user_crops"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    crop_id = Column(Integer, ForeignKey("crops.id"), nullable=False)
    area = Column(Float, nullable=True)  # in acres
    planting_date = Column(DateTime, nullable=True)
    growth_stage = Column(Enum(GrowthStage), nullable=True)
    soil_type = Column(Enum(SoilType), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="crops")
    crop = relationship("Crop", back_populates="user_crops")


class SoilAnalysis(Base):
    __tablename__ = "soil_analyses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    crop_id = Column(Integer, ForeignKey("crops.id"), nullable=True)
    soil_type = Column(Enum(SoilType), nullable=False)
    ph = Column(Float, nullable=False)
    nitrogen = Column(Float, nullable=False)  # kg/ha
    phosphorus = Column(Float, nullable=False)  # kg/ha
    potassium = Column(Float, nullable=False)  # kg/ha
    organic_matter = Column(Float, nullable=True)  # %
    ec = Column(Float, nullable=True)  # Electrical conductivity dS/m
    sulfur = Column(Float, nullable=True)
    zinc = Column(Float, nullable=True)
    boron = Column(Float, nullable=True)
    iron = Column(Float, nullable=True)
    manganese = Column(Float, nullable=True)
    copper = Column(Float, nullable=True)
    growth_stage = Column(Enum(GrowthStage), nullable=True)
    recommendations = Column(JSON, nullable=True)  # fertilizer recommendations
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="soil_analyses")
    crop = relationship("Crop")


class WeatherData(Base):
    __tablename__ = "weather_data"

    id = Column(Integer, primary_key=True, index=True)
    location = Column(String(200), index=True, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    temperature = Column(Float, nullable=True)  # °C
    humidity = Column(Float, nullable=True)  # %
    rainfall = Column(Float, nullable=True)  # mm
    wind_speed = Column(Float, nullable=True)  # km/h
    wind_direction = Column(String(20), nullable=True)
    pressure = Column(Float, nullable=True)  # hPa
    uv_index = Column(Float, nullable=True)
    condition = Column(String(50), nullable=True)  # sunny, cloudy, rainy, etc.
    forecast = Column(JSON, nullable=True)  # 5-day forecast
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(String(100), index=True, nullable=False)
    role = Column(String(20), nullable=False)  # user, assistant
    content = Column(Text, nullable=False)
    language = Column(Enum(Language), default=Language.HINDI)
    # NOTE: attribute named context_data (DB column still 'metadata') because
    # 'metadata' is reserved by SQLAlchemy Declarative API.
    context_data = Column("metadata", JSON, nullable=True)  # context: crop, location, weather, etc.
    tokens_used = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="chat_history")


class DiseasePrediction(Base):
    __tablename__ = "disease_predictions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    crop_id = Column(Integer, ForeignKey("crops.id"), nullable=True)
    disease_id = Column(Integer, ForeignKey("diseases.id"), nullable=True)
    image_path = Column(String(500), nullable=False)
    predicted_disease = Column(String(100), nullable=False)
    confidence = Column(Float, nullable=False)
    all_predictions = Column(JSON, nullable=True)  # top 5 predictions
    symptoms_observed = Column(Text, nullable=True)
    ai_analysis = Column(Text, nullable=True)
    recommended_actions = Column(JSON, nullable=True)
    is_verified = Column(Boolean, default=False)
    expert_feedback = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="disease_predictions")
    disease = relationship("Disease", back_populates="predictions")
    crop = relationship("Crop")


class SchemeDocument(Base):
    __tablename__ = "scheme_documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    source = Column(String(200), nullable=True)  # government website, PDF upload, etc.
    file_path = Column(String(500), nullable=True)
    content = Column(Text, nullable=True)  # extracted text
    language = Column(Enum(Language), default=Language.HINDI)
    scheme_name = Column(String(200), nullable=True)
    scheme_type = Column(String(100), nullable=True)  # subsidy, insurance, loan, etc.
    eligibility = Column(Text, nullable=True)
    benefits = Column(Text, nullable=True)
    required_documents = Column(Text, nullable=True)
    application_process = Column(Text, nullable=True)
    deadline = Column(DateTime, nullable=True)
    is_processed = Column(Boolean, default=False)
    vector_ids = Column(JSON, nullable=True)  # FAISS/Chroma vector IDs
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="scheme_documents")
    queries = relationship("SchemeQuery", back_populates="document")


class SchemeQuery(Base):
    __tablename__ = "scheme_queries"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("scheme_documents.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    source_chunks = Column(JSON, nullable=True)  # references to document chunks
    confidence = Column(Float, nullable=True)
    language = Column(Enum(Language), default=Language.HINDI)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    document = relationship("SchemeDocument", back_populates="queries")
    user = relationship("User")


class VoiceInteraction(Base):
    __tablename__ = "voice_interactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    audio_path = Column(String(500), nullable=True)
    transcript = Column(Text, nullable=True)
    detected_language = Column(Enum(Language), nullable=True)
    intent = Column(String(100), nullable=True)
    response_text = Column(Text, nullable=True)
    response_audio_path = Column(String(500), nullable=True)
    processing_time_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())