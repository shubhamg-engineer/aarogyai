import cv2
import numpy as np
from PIL import Image

MIN_IMAGE_SIZE = 50  # Minimum dimension (px) to safely crop center region

def analyze_nail_color(image):
    """
    Analyze fingernail color to detect potential anemia.

    Args:
        image: PIL Image object

    Returns:
        dict: Analysis results with hemoglobin estimate, risk level, and confidence
    """
    try:
        # Validate input type
        if not isinstance(image, Image.Image):
            return {'error': 'Invalid image input. Expected a PIL Image.'}

        # Convert PIL to OpenCV format
        img_array = np.array(image.convert("RGB"))
        img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)

        # Validate image dimensions
        height, width = img_bgr.shape[:2]
        if height < MIN_IMAGE_SIZE or width < MIN_IMAGE_SIZE:
            return {
                'error': f'Image too small ({width}x{height}px). Please upload a clearer, higher-resolution photo.'
            }

        # Resize for faster processing
        max_dimension = 800
        if max(height, width) > max_dimension:
            scale = max_dimension / max(height, width)
            img_bgr = cv2.resize(img_bgr, (int(width * scale), int(height * scale)))

        # Convert to different color spaces for analysis
        img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
        img_lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB)

        # Focus on center region (nail bed area)
        h, w = img_bgr.shape[:2]
        y1, y2 = int(h * 0.3), int(h * 0.7)
        x1, x2 = int(w * 0.3), int(w * 0.7)

        center_region = img_bgr[y1:y2, x1:x2]
        center_hsv   = img_hsv[y1:y2, x1:x2]
        center_lab   = img_lab[y1:y2, x1:x2]

        # Guard: ensure cropped region is not empty
        if center_region.size == 0:
            return {'error': 'Could not isolate nail region. Please ensure the nail fills most of the image.'}

        # ── Color Metrics ──────────────────────────────────────────
        # 1. RGB
        mean_bgr = cv2.mean(center_region)[:3]
        b, g, r = mean_bgr

        # 2. HSV
        mean_hsv = cv2.mean(center_hsv)[:3]
        hue, saturation, value = mean_hsv

        # 3. LAB
        mean_lab = cv2.mean(center_lab)[:3]
        lightness, a_channel, b_channel = mean_lab

        # Redness index (key indicator of blood perfusion)
        redness  = r / (b + g + 1)   # +1 avoids division by zero
        pinkness = (r + 50) / (b + g + 100)

        # ── Anemia Risk Score (0–100) ──────────────────────────────
        risk_score = 0

        # Factor 1: Redness (pale nails → low redness)
        if redness < 0.9:
            risk_score += 30
        elif redness < 1.0:
            risk_score += 20
        elif redness < 1.1:
            risk_score += 10

        # Factor 2: Saturation (washed-out colour)
        if saturation < 30:
            risk_score += 25
        elif saturation < 50:
            risk_score += 15
        elif saturation < 70:
            risk_score += 5

        # Factor 3: Lightness (very pale)
        if lightness > 180:
            risk_score += 25
        elif lightness > 160:
            risk_score += 15
        elif lightness > 140:
            risk_score += 5

        # Factor 4: Pinkness
        if pinkness < 1.0:
            risk_score += 20
        elif pinkness < 1.2:
            risk_score += 10

        # ── Hemoglobin Estimate ────────────────────────────────────
        if risk_score > 70:
            hb_estimate    = "7–9 g/dL"
            hb_status      = "Severely Low"
            risk_level     = "High"
            recommendation = "URGENT: Visit a doctor immediately for a blood test. Severe anemia suspected."
        elif risk_score > 50:
            hb_estimate    = "9–11 g/dL"
            hb_status      = "Low"
            risk_level     = "Moderate-High"
            recommendation = "Visit a clinic within 24 hours for a blood test. Moderate anemia suspected."
        elif risk_score > 30:
            hb_estimate    = "11–12 g/dL"
            hb_status      = "Borderline Low"
            risk_level     = "Mild"
            recommendation = "Schedule a blood test within a week. Mild anemia possible."
        else:
            hb_estimate    = "12–15 g/dL"
            hb_status      = "Normal Range"
            risk_level     = "Low"
            recommendation = "Nail color appears healthy. Routine annual checkup recommended."

        # ── Confidence Score ───────────────────────────────────────
        brightness = float(np.mean(img_bgr))
        contrast   = float(np.std(img_bgr))

        confidence = 60  # Base
        if 80 < brightness < 180:
            confidence += 15   # Good lighting
        if contrast > 40:
            confidence += 15   # Good contrast
        if center_region.size > 10_000:
            confidence += 10   # Good resolution
        confidence = min(confidence, 95)

        # ── Photo Quality Feedback ─────────────────────────────────
        quality_warnings = []
        if brightness < 80:
            quality_warnings.append("⚠️ Image appears too dark — try better lighting.")
        elif brightness > 200:
            quality_warnings.append("⚠️ Image appears overexposed — avoid direct flash.")
        if contrast < 25:
            quality_warnings.append("⚠️ Low contrast detected — try a plain background.")

        return {
            'risk_score':       int(risk_score),
            'risk_level':       risk_level,
            'hb_estimate':      hb_estimate,
            'hb_status':        hb_status,
            'recommendation':   recommendation,
            'confidence':       int(confidence),
            'quality_warnings': quality_warnings,
            'color_metrics': {
                'redness':    round(redness,    2),
                'saturation': round(saturation, 1),
                'lightness':  round(lightness,  1),
                'pinkness':   round(pinkness,   2),
            },
            'rgb_values': {
                'red':   round(r, 1),
                'green': round(g, 1),
                'blue':  round(b, 1),
            },
        }

    except Exception as e:
        return {
            'error': str(e),
            'risk_level': 'Unknown',
            'recommendation': 'Error analyzing image. Please try with a clearer photo.',
        }


def get_tips_for_better_photo():
    """Return tips for capturing better nail photos."""
    return """
📸 **Tips for Best Results:**

1. ✅ **Lighting:** Use natural daylight (not direct sunlight)
2. ✅ **Distance:** 15–20 cm from camera to nail
3. ✅ **Focus:** Ensure nail bed is clearly visible and sharp
4. ✅ **Background:** Plain white/light background preferred
5. ✅ **Clean nails:** Remove nail polish, wash hands first
6. ✅ **Angle:** Straight-on view of fingernail (not tilted)
7. ✅ **Finger:** Use index or middle finger for best results

⚠️ **Avoid:**
- ❌ Dark or artificial yellow lighting
- ❌ Blurry / shaky photos
- ❌ Nail polish or decorations
- ❌ Shadows falling across the nail
"""


def generate_visual_feedback(image, results):
    """
    Generate an annotated image showing analysis regions and result overlay.

    Args:
        image:   PIL Image object
        results: Analysis results dict

    Returns:
        PIL Image: Annotated image
    """
    try:
        img_array = np.array(image.convert("RGB"))
        img_bgr   = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)

        height, width = img_bgr.shape[:2]
        max_dimension = 800
        if max(height, width) > max_dimension:
            scale  = max_dimension / max(height, width)
            img_bgr = cv2.resize(img_bgr, (int(width * scale), int(height * scale)))
            height, width = img_bgr.shape[:2]

        h, w = height, width

        # Draw analysis bounding box
        cv2.rectangle(img_bgr,
                      (int(w * 0.3), int(h * 0.3)),
                      (int(w * 0.7), int(h * 0.7)),
                      (0, 255, 0), 2)

        risk_level = results.get('risk_level', 'Unknown')
        confidence = results.get('confidence', 0)

        # Colour-code by risk
        color_map = {
            "High":          (0,   0,   255),  # Red
            "Moderate-High": (0,   165, 255),  # Orange
            "Mild":          (0,   215, 255),  # Yellow
            "Low":           (0,   255, 0),    # Green
        }
        color = color_map.get(risk_level, (200, 200, 200))

        # Semi-transparent overlay panel
        overlay = img_bgr.copy()
        cv2.rectangle(overlay, (8, 8), (310, 90), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, img_bgr, 0.4, 0, img_bgr)
        cv2.rectangle(img_bgr, (8, 8), (310, 90), color, 2)

        cv2.putText(img_bgr, f"Risk:       {risk_level}", (18, 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
        cv2.putText(img_bgr, f"Confidence: {confidence}%", (18, 65),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)

        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        return Image.fromarray(img_rgb)

    except Exception:
        return image  # Safe fallback — return original image