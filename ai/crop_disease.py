"""
Crop Disease Detection Module
Uses a pre-trained CNN model for crop disease classification.
Supports multiple crops and diseases with confidence scoring.
"""

import torch
import torch.nn as nn
import torchvision.transforms as transforms
from torchvision import models
from PIL import Image
import numpy as np
import io
import structlog
from typing import List, Dict, Optional, Tuple
from pathlib import Path

logger = structlog.get_logger()


# Disease class mapping - in production, load from database/config
DISEASE_CLASSES = {
    0: {"crop": "tomato", "disease": "Tomato_Bacterial_spot", "scientific": "Xanthomonas campestris"},
    1: {"crop": "tomato", "disease": "Tomato_Early_blight", "scientific": "Alternaria solani"},
    2: {"crop": "tomato", "disease": "Tomato_Late_blight", "scientific": "Phytophthora infestans"},
    3: {"crop": "tomato", "disease": "Tomato_Leaf_Mold", "scientific": "Passalora fulva"},
    4: {"crop": "tomato", "disease": "Tomato_Septoria_leaf_spot", "scientific": "Septoria lycopersici"},
    5: {"crop": "tomato", "disease": "Tomato_Spider_mites", "scientific": "Tetranychus urticae"},
    6: {"crop": "tomato", "disease": "Tomato_Target_Spot", "scientific": "Corynespora cassiicola"},
    7: {"crop": "tomato", "disease": "Tomato_Yellow_Leaf_Curl_Virus", "scientific": "TYLCV"},
    8: {"crop": "tomato", "disease": "Tomato_mosaic_virus", "scientific": "ToMV"},
    9: {"crop": "potato", "disease": "Potato_Early_blight", "scientific": "Alternaria solani"},
    10: {"crop": "potato", "disease": "Potato_Late_blight", "scientific": "Phytophthora infestans"},
    11: {"crop": "wheat", "disease": "Wheat_Leaf_rust", "scientific": "Puccinia triticina"},
    12: {"crop": "wheat", "disease": "Wheat_Stem_rust", "scientific": "Puccinia graminis"},
    13: {"crop": "wheat", "disease": "Wheat_Yellow_rust", "scientific": "Puccinia striiformis"},
    14: {"crop": "rice", "disease": "Rice_Bacterial_blight", "scientific": "Xanthomonas oryzae"},
    15: {"crop": "rice", "disease": "Rice_Blast", "scientific": "Magnaporthe oryzae"},
    16: {"crop": "rice", "disease": "Rice_Brown_spot", "scientific": "Cochliobolus miyabeanus"},
    17: {"crop": "cotton", "disease": "Cotton_Leaf_Curl_Virus", "scientific": "CLCuV"},
    18: {"crop": "cotton", "disease": "Cotton_Aphids", "scientific": "Aphis gossypii"},
    19: {"crop": "healthy", "disease": "Healthy", "scientific": "None"},
}

# Crop-specific disease info for contextual analysis
DISEASE_INFO = {
    "Tomato_Bacterial_spot": {
        "symptoms": "Small, water-soaked lesions on leaves, stems, and fruits. Lesions turn brown with yellow halos.",
        "immediate_actions": [
            "Remove and destroy infected plant parts immediately",
            "Apply copper-based bactericide (copper hydroxide or copper oxychloride)",
            "Avoid overhead irrigation; use drip irrigation",
            "Ensure proper plant spacing for air circulation"
        ],
        "preventive_measures": [
            "Use certified disease-free seeds",
            "Rotate crops - avoid solanaceous crops for 2-3 years",
            "Apply preventive copper sprays before rainy season",
            "Control weeds that may harbor bacteria",
            "Sanitize tools between plants"
        ],
        "severity": "high"
    },
    "Tomato_Early_blight": {
        "symptoms": "Dark brown concentric rings (target spots) on older leaves. Yellowing around lesions.",
        "immediate_actions": [
            "Remove infected lower leaves",
            "Apply fungicide: chlorothalonil, mancozeb, or azoxystrobin",
            "Improve air circulation through pruning",
            "Mulch around plants to prevent soil splash"
        ],
        "preventive_measures": [
            "Crop rotation with non-solanaceous crops",
            "Use resistant varieties",
            "Avoid overhead watering",
            "Stake plants to keep foliage off ground",
            "Apply preventive fungicide at first flower"
        ],
        "severity": "medium"
    },
    "Tomato_Late_blight": {
        "symptoms": "Large, dark, water-soaked lesions on leaves and stems. White fuzzy growth on underside in humid conditions.",
        "immediate_actions": [
            "URGENT: This spreads rapidly in cool, wet weather",
            "Apply systemic fungicide immediately: metalaxyl, cymoxanil, or dimethomorph",
            "Destroy severely infected plants",
            "Harvest mature fruits immediately"
        ],
        "preventive_measures": [
            "Monitor weather - high risk during cool (10-20°C), wet conditions",
            "Apply preventive fungicides weekly during risk periods",
            "Use resistant varieties (Ph-2, Ph-3 genes)",
            "Ensure excellent drainage",
            "Remove volunteer potatoes and tomatoes"
        ],
        "severity": "critical"
    },
    "Wheat_Leaf_rust": {
        "symptoms": "Orange-brown pustules on leaf surfaces. Powdery spores rub off on fingers.",
        "immediate_actions": [
            "Apply triazole fungicide (propiconazole, tebuconazole) at flag leaf stage",
            "Monitor fields weekly during spring",
            "Harvest early if severe infection on flag leaf"
        ],
        "preventive_measures": [
            "Plant resistant varieties (Lr genes)",
            "Avoid excessive nitrogen fertilization",
            "Plant early to escape peak rust period",
            "Destroy volunteer wheat plants"
        ],
        "severity": "medium"
    },
    "Rice_Blast": {
        "symptoms": "Diamond-shaped lesions with gray centers and brown margins on leaves, nodes, and panicles.",
        "immediate_actions": [
            "Apply tricyclazole or isoprothiolane immediately",
            "Drain field if possible to reduce humidity",
            "Apply potassium fertilizer to strengthen plants"
        ],
        "preventive_measures": [
            "Use resistant varieties (Pi genes)",
            "Balanced fertilization - avoid excess nitrogen",
            "Maintain shallow water (2-3 cm) during tillering",
            "Treat seeds with carbendazim",
            "Remove weed hosts"
        ],
        "severity": "high"
    },
    "Healthy": {
        "symptoms": "No visible disease symptoms. Plant appears healthy with normal coloration.",
        "immediate_actions": [
            "Continue regular monitoring",
            "Maintain good agricultural practices",
            "Follow recommended fertilization schedule"
        ],
        "preventive_measures": [
            "Regular field scouting",
            "Balanced nutrition",
            "Proper irrigation management",
            "Crop rotation",
            "Use of disease-resistant varieties"
        ],
        "severity": "none"
    }
}


class CropDiseaseModel:
    """Crop disease detection using CNN."""
    
    def __init__(self, model_path: Optional[str] = None, num_classes: int = len(DISEASE_CLASSES)):
        self.num_classes = num_classes
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = self._build_model()
        self.transform = self._get_transforms()
        
        if model_path and Path(model_path).exists():
            self.load_model(model_path)
        else:
            logger.warning("No model file found, using random weights. Load a trained model for production.")
        
        self.model.to(self.device)
        self.model.eval()
    
    def _build_model(self) -> nn.Module:
        """Build ResNet50 model with custom classifier."""
        model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V2)
        # Freeze early layers
        for param in model.parameters():
            param.requires_grad = False
        # Unfreeze last few layers for fine-tuning
        for param in model.layer4.parameters():
            param.requires_grad = True
        for param in model.fc.parameters():
            param.requires_grad = True
        
        # Custom classifier
        model.fc = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(model.fc.in_features, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, self.num_classes)
        )
        return model
    
    def _get_transforms(self) -> transforms.Compose:
        """Image preprocessing transforms."""
        return transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
    
    def load_model(self, path: str) -> None:
        """Load trained model weights."""
        try:
            checkpoint = torch.load(path, map_location=self.device)
            if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
                self.model.load_state_dict(checkpoint['model_state_dict'])
            else:
                self.model.load_state_dict(checkpoint)
            logger.info("Model loaded successfully", path=path)
        except Exception as e:
            logger.error("Failed to load model", path=path, error=str(e))
            raise
    
    def predict(self, image: Image.Image, top_k: int = 5) -> List[Dict]:
        """Predict disease from image."""
        # Preprocess
        input_tensor = self.transform(image).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(input_tensor)
            probabilities = torch.nn.functional.softmax(outputs, dim=1)
            top_probs, top_indices = torch.topk(probabilities, top_k)
        
        results = []
        for i in range(top_k):
            idx = top_indices[0][i].item()
            prob = top_probs[0][i].item()
            class_info = DISEASE_CLASSES.get(idx, {"crop": "unknown", "disease": "unknown", "scientific": "unknown"})
            results.append({
                "class_index": idx,
                "crop": class_info["crop"],
                "disease": class_info["disease"],
                "scientific_name": class_info["scientific"],
                "confidence": round(prob, 4)
            })
        
        return results
    
    def predict_from_bytes(self, image_bytes: bytes, top_k: int = 5) -> List[Dict]:
        """Predict from image bytes."""
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        return self.predict(image, top_k)


def get_disease_details(disease_name: str) -> Dict:
    """Get detailed information about a disease."""
    return DISEASE_INFO.get(disease_name, {
        "symptoms": "Information not available for this disease.",
        "immediate_actions": ["Consult local agricultural extension officer"],
        "preventive_measures": ["Follow general good agricultural practices"],
        "severity": "unknown"
    })


def generate_ai_analysis(predictions: List[Dict], crop_context: Optional[str] = None) -> str:
    """Generate contextual AI analysis based on predictions."""
    top = predictions[0]
    disease_name = top["disease"]
    confidence = top["confidence"]
    crop = top["crop"]
    
    details = get_disease_details(disease_name)
    severity = details.get("severity", "unknown")
    
    analysis_parts = []
    
    # Confidence warning
    if confidence < 0.5:
        analysis_parts.append(
            f"⚠️ **Low Confidence Warning**: The model is only {confidence*100:.0f}% confident. "
            f"Please verify with an agricultural expert before taking action."
        )
    elif confidence < 0.7:
        analysis_parts.append(
            f"⚠️ **Moderate Confidence**: The model is {confidence*100:.0f}% confident. "
            f"Consider getting a second opinion from an expert."
        )
    
    # Disease analysis
    if disease_name == "Healthy":
        analysis_parts.append(
            f"✅ **Good News**: The {crop} plant appears healthy! No disease symptoms detected."
        )
    else:
        analysis_parts.append(
            f"🔍 **Detected**: {disease_name.replace('_', ' ')} "
            f"({details.get('scientific', 'N/A')}) on {crop}."
        )
        analysis_parts.append(f"📋 **Symptoms**: {details.get('symptoms', 'N/A')}")
        analysis_parts.append(f"⚡ **Severity**: {severity.upper()}")
    
    # Context-aware advice
    if crop_context and crop_context.lower() != crop.lower():
        analysis_parts.append(
            f"📝 **Note**: You mentioned {crop_context}, but the model detected {crop}. "
            f"Please confirm the crop type for accurate advice."
        )
    
    return "\n\n".join(analysis_parts)


def get_recommendations(predictions: List[Dict]) -> Tuple[List[str], List[str]]:
    """Get immediate actions and preventive measures."""
    top = predictions[0]
    disease_name = top["disease"]
    details = get_disease_details(disease_name)
    
    immediate = details.get("immediate_actions", [])
    preventive = details.get("preventive_measures", [])
    
    return immediate, preventive


# Singleton instance
_model_instance: Optional[CropDiseaseModel] = None


def get_disease_model(model_path: Optional[str] = None) -> CropDiseaseModel:
    """Get or create singleton model instance."""
    global _model_instance
    if _model_instance is None:
        _model_instance = CropDiseaseModel(model_path)
    return _model_instance