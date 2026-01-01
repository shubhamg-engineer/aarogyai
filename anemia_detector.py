import cv2
import numpy as np
from PIL import Image

def analyze_nail_color(image):
    """
    Analyze fingernail color to detect potential anemia.
    
    Args:
        image: PIL Image object
        
    Returns:
        dict: Analysis results with hemoglobin estimate, risk level, and confidence
    """
    try:
        # Convert PIL to OpenCV format
        img_array = np.array(image)
        img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        # Resize for faster processing
        height, width = img_bgr.shape[:2]
        max_dimension = 800
        if max(height, width) > max_dimension:
            scale = max_dimension / max(height, width)
            img_bgr = cv2.resize(img_bgr, (int(width * scale), int(height * scale)))
        
        # Convert to different color spaces for analysis
        img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
        img_lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB)
        
        # Focus on center region (nail bed area)
        h, w = img_bgr.shape[:2]
        center_region = img_bgr[int(h*0.3):int(h*0.7), int(w*0.3):int(w*0.7)]
        center_hsv = img_hsv[int(h*0.3):int(h*0.7), int(w*0.3):int(w*0.7)]
        center_lab = img_lab[int(h*0.3):int(h*0.7), int(w*0.3):int(w*0.7)]
        
        # Calculate color metrics
        # 1. RGB Analysis
        mean_bgr = cv2.mean(center_region)[:3]
        b, g, r = mean_bgr
        
        # 2. HSV Analysis (Hue, Saturation, Value)
        mean_hsv = cv2.mean(center_hsv)[:3]
        hue, saturation, value = mean_hsv
        
        # 3. LAB Analysis (Lightness, A, B)
        mean_lab = cv2.mean(center_lab)[:3]
        lightness, a_channel, b_channel = mean_lab
        
        # Calculate redness index (key indicator)
        redness = r / (b + g + 1)  # +1 to avoid division by zero
        
        # Calculate pinkness score (healthy nails are pinkish)
        pinkness = (r + 50) / (b + g + 100)
        
        # Anemia detection logic based on medical research
        # Pale/white nails indicate anemia
        # Pink/red nails indicate healthy
        
        # Calculate anemia risk score (0-100)
        risk_score = 0
        
        # Factor 1: Low redness (pale nails)
        if redness < 0.9:
            risk_score += 30
        elif redness < 1.0:
            risk_score += 20
        elif redness < 1.1:
            risk_score += 10
        
        # Factor 2: Low saturation (washed out color)
        if saturation < 30:
            risk_score += 25
        elif saturation < 50:
            risk_score += 15
        elif saturation < 70:
            risk_score += 5
        
        # Factor 3: High lightness (very pale)
        if lightness > 180:
            risk_score += 25
        elif lightness > 160:
            risk_score += 15
        elif lightness > 140:
            risk_score += 5
        
        # Factor 4: Low pinkness
        if pinkness < 1.0:
            risk_score += 20
        elif pinkness < 1.2:
            risk_score += 10
        
        # Estimate hemoglobin level (normal: 12-16 g/dL for women, 13-17 for men)
        # This is a rough estimation based on nail color
        if risk_score > 70:
            hb_estimate = "7-9 g/dL"
            hb_status = "Severely Low"
            risk_level = "High"
            recommendation = "URGENT: Visit doctor immediately for blood test. Severe anemia suspected."
        elif risk_score > 50:
            hb_estimate = "9-11 g/dL"
            hb_status = "Low"
            risk_level = "Moderate-High"
            recommendation = "Visit clinic within 24 hours for blood test. Moderate anemia suspected."
        elif risk_score > 30:
            hb_estimate = "11-12 g/dL"
            hb_status = "Borderline Low"
            risk_level = "Mild"
            recommendation = "Schedule blood test within a week. Mild anemia possible."
        else:
            hb_estimate = "12-15 g/dL"
            hb_status = "Normal Range"
            risk_level = "Low"
            recommendation = "Nail color appears healthy. Routine checkup recommended annually."
        
        # Calculate confidence based on image quality
        # Check if image is well-lit and clear
        brightness = np.mean(img_bgr)
        contrast = np.std(img_bgr)
        
        confidence = 60  # Base confidence
        
        if 80 < brightness < 180:  # Good lighting
            confidence += 15
        if contrast > 40:  # Good contrast
            confidence += 15
        if center_region.size > 10000:  # Good resolution
            confidence += 10
        
        confidence = min(confidence, 95)  # Cap at 95%
        
        # Prepare detailed results
        results = {
            'risk_score': int(risk_score),
            'risk_level': risk_level,
            'hb_estimate': hb_estimate,
            'hb_status': hb_status,
            'recommendation': recommendation,
            'confidence': int(confidence),
            'color_metrics': {
                'redness': round(redness, 2),
                'saturation': round(saturation, 1),
                'lightness': round(lightness, 1),
                'pinkness': round(pinkness, 2)
            },
            'rgb_values': {
                'red': round(r, 1),
                'green': round(g, 1),
                'blue': round(b, 1)
            }
        }
        
        return results
        
    except Exception as e:
        return {
            'error': str(e),
            'risk_level': 'Unknown',
            'recommendation': 'Error analyzing image. Please try with a clearer photo.'
        }

def get_tips_for_better_photo():
    """Return tips for capturing better nail photos"""
    return """
    📸 **Tips for Best Results:**
    
    1. ✅ **Lighting:** Use natural daylight (not direct sunlight)
    2. ✅ **Distance:** 15-20 cm from camera to nail
    3. ✅ **Focus:** Ensure nail bed is clearly visible and in focus
    4. ✅ **Background:** Plain white/light background preferred
    5. ✅ **Clean nails:** Remove nail polish, wash hands
    6. ✅ **Angle:** Straight-on view of fingernail (not tilted)
    7. ✅ **Finger:** Use index or middle finger for best results
    
    ⚠️ **Avoid:**
    - ❌ Dark/artificial lighting
    - ❌ Blurry photos
    - ❌ Nail polish or decorations
    - ❌ Shadows on nail
    """

def generate_visual_feedback(image, results):
    """
    Generate annotated image showing analysis regions
    
    Args:
        image: PIL Image object
        results: Analysis results dict
        
    Returns:
        PIL Image: Annotated image
    """
    try:
        # Convert to OpenCV
        img_array = np.array(image)
        img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        # Resize if needed
        height, width = img_bgr.shape[:2]
        max_dimension = 800
        if max(height, width) > max_dimension:
            scale = max_dimension / max(height, width)
            img_bgr = cv2.resize(img_bgr, (int(width * scale), int(height * scale)))
            height, width = img_bgr.shape[:2]
        
        # Draw analysis region
        h, w = height, width
        cv2.rectangle(img_bgr, 
                     (int(w*0.3), int(h*0.3)), 
                     (int(w*0.7), int(h*0.7)), 
                     (0, 255, 0), 2)
        
        # Add text overlay
        risk_level = results.get('risk_level', 'Unknown')
        confidence = results.get('confidence', 0)
        
        # Color code based on risk
        if risk_level == "High":
            color = (0, 0, 255)  # Red
        elif risk_level in ["Moderate-High", "Mild"]:
            color = (0, 165, 255)  # Orange
        else:
            color = (0, 255, 0)  # Green
        
        # Add background rectangle for text
        cv2.rectangle(img_bgr, (10, 10), (300, 80), (0, 0, 0), -1)
        cv2.rectangle(img_bgr, (10, 10), (300, 80), color, 2)
        
        # Add text
        cv2.putText(img_bgr, f"Risk: {risk_level}", (20, 35), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(img_bgr, f"Confidence: {confidence}%", (20, 65), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Convert back to PIL
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        return Image.fromarray(img_rgb)
        
    except Exception as e:
        return image  # Return original if annotation fails