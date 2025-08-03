#!/usr/bin/env python3
"""
Extract Module - OCR and Document Field Extraction
Uses Tesseract OCR to extract text and structured fields from images
"""

import json
import os
import re
import sys
from PIL import Image
import pytesseract
from pathlib import Path


class DocumentExtractor:
    def __init__(self):
        """Initialize the document extractor with field patterns"""
        self.field_patterns = {
            # Common ID/License patterns
            "name": [
                r"name[:\s]+([a-zA-Z\s,]+)",
                r"full\s+name[:\s]+([a-zA-Z\s,]+)",
                r"^([A-Z][a-zA-Z]+\s+[A-Z][a-zA-Z]+)",  # First Last pattern
            ],
            "date_of_birth": [
                r"(?:date\s+of\s+birth|dob|birth\s+date)[:\s]+(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})",
                r"born[:\s]+(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})",
                r"(\d{1,2}[-/]\d{1,2}[-/]\d{4})",  # Generic date pattern
            ],
            "id_number": [
                r"(?:id|license|card)\s*(?:number|no|#)[:\s]*([A-Z0-9-]+)",
                r"(?:number|no|#)[:\s]*([A-Z0-9-]+)",
                r"([A-Z]{1,3}\d{6,12})",  # Pattern like ABC123456
            ],
            "address": [
                r"address[:\s]+([^\n]+)",
                r"(?:street|addr)[:\s]+([^\n]+)",
                r"(\d+\s+[A-Za-z\s]+(?:street|st|avenue|ave|road|rd|lane|ln|drive|dr))",
            ],
            "phone": [
                r"(?:phone|tel|mobile)[:\s]*([0-9\-\(\)\s]+)",
                r"(\(\d{3}\)\s*\d{3}-\d{4})",  # (123) 456-7890
                r"(\d{3}-\d{3}-\d{4})",  # 123-456-7890
            ],
            "email": [
                r"(?:email|e-mail)[:\s]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})",
                r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})",
            ],
            "expiry_date": [
                r"(?:expires?|exp|expiry)[:\s]*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})",
                r"valid\s+until[:\s]*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})",
            ],
            "issuer": [
                r"issued\s+by[:\s]*([A-Za-z\s]+)",
                r"(?:state|country|authority)[:\s]*([A-Za-z\s]+)",
            ]
        }
    
    def preprocess_image(self, image_path):
        """
        Preprocess image for better OCR results
        
        Args:
            image_path: Path to input image
            
        Returns:
            PIL.Image: Preprocessed image
        """
        try:
            # Open and convert image
            image = Image.open(image_path)
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Basic preprocessing - could be enhanced
            # For now, just ensure good quality
            width, height = image.size
            if width < 1000:  # Upscale small images
                scale_factor = 1000 / width
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            return image
            
        except Exception as e:
            print(f"Error preprocessing image: {e}")
            return None
    
    def extract_text_from_image(self, image_path):
        """
        Extract raw text from image using OCR
        
        Args:
            image_path: Path to input image
            
        Returns:
            str: Extracted text
        """
        try:
            # Preprocess image
            image = self.preprocess_image(image_path)
            if image is None:
                return None
            
            # Perform OCR
            print(f"Extracting text from: {image_path}")
            
            # Try different OCR configurations
            custom_config = r'--oem 3 --psm 6'  # Treat as uniform block of text
            raw_text = pytesseract.image_to_string(image, config=custom_config)
            
            if not raw_text.strip():
                # Try alternative configuration
                custom_config = r'--oem 3 --psm 4'  # Single column of text
                raw_text = pytesseract.image_to_string(image, config=custom_config)
            
            print(f"Extracted text:\n{raw_text}")
            return raw_text.strip()
            
        except Exception as e:
            print(f"Error extracting text: {e}")
            return None
    
    def extract_structured_fields(self, text):
        """
        Extract structured fields from raw text
        
        Args:
            text: Raw OCR text
            
        Returns:
            dict: Extracted fields
        """
        if not text:
            return {}
        
        extracted_fields = {}
        text_lines = text.split('\n')
        full_text = ' '.join(text_lines).lower()
        
        # Try to extract each field type
        for field_name, patterns in self.field_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, full_text, re.IGNORECASE | re.MULTILINE)
                if match:
                    value = match.group(1).strip()
                    # Clean up the extracted value
                    value = re.sub(r'\s+', ' ', value)  # Normalize whitespace
                    value = value.title() if field_name == 'name' else value
                    extracted_fields[field_name] = value
                    break  # Use first successful match
        
        # Post-process and validate fields
        extracted_fields = self._clean_extracted_fields(extracted_fields)
        
        return extracted_fields
    
    def _clean_extracted_fields(self, fields):
        """Clean and validate extracted fields"""
        cleaned = {}
        
        for key, value in fields.items():
            if value and len(value.strip()) > 0:
                # Remove common OCR artifacts
                value = re.sub(r'[|@#$%^&*]', '', value)
                value = value.strip()
                
                # Validate field format
                if key == 'date_of_birth' or key == 'expiry_date':
                    # Normalize date format
                    date_match = re.search(r'(\d{1,2})[-/](\d{1,2})[-/](\d{2,4})', value)
                    if date_match:
                        month, day, year = date_match.groups()
                        if len(year) == 2:
                            year = '20' + year if int(year) < 50 else '19' + year
                        value = f"{month.zfill(2)}/{day.zfill(2)}/{year}"
                
                elif key == 'phone':
                    # Clean phone number
                    phone_digits = re.sub(r'[^\d]', '', value)
                    if len(phone_digits) == 10:
                        value = f"({phone_digits[:3]}) {phone_digits[3:6]}-{phone_digits[6:]}"
                
                elif key == 'name':
                    # Ensure proper name format
                    value = ' '.join(word.capitalize() for word in value.split())
                
                if len(value) > 2:  # Only keep non-trivial values
                    cleaned[key] = value
        
        return cleaned
    
    def process_document(self, image_path, output_path="outputs/fields.json"):
        """
        Process document image and extract structured fields
        
        Args:
            image_path: Path to input image
            output_path: Path to save extracted fields JSON
            
        Returns:
            dict: Extracted fields result
        """
        try:
            # Extract text using OCR
            raw_text = self.extract_text_from_image(image_path)
            
            if not raw_text:
                print("No text extracted from image")
                return None
            
            # Extract structured fields
            fields = self.extract_structured_fields(raw_text)
            
            # Prepare result
            result = {
                "source_image": str(image_path),
                "raw_text": raw_text,
                "extracted_fields": fields,
                "field_count": len(fields)
            }
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Save result
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print(f"Extraction results saved to: {output_path}")
            print(f"Extracted {len(fields)} fields:")
            for key, value in fields.items():
                print(f"  {key}: {value}")
            
            return result
            
        except Exception as e:
            print(f"Error processing document: {e}")
            return None


def main():
    """CLI interface for document extraction module"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Extract structured fields from document image")
    parser.add_argument("image_file", help="Path to document image")
    parser.add_argument("--output", "-o", default="outputs/fields.json", 
                       help="Output JSON file path")
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not os.path.exists(args.image_file):
        print(f"Error: Image file not found: {args.image_file}")
        sys.exit(1)
    
    # Initialize extractor and process
    extractor = DocumentExtractor()
    result = extractor.process_document(args.image_file, args.output)
    
    if result and result.get('field_count', 0) > 0:
        print("✅ Document extraction completed successfully")
    else:
        print("⚠️  Document extraction completed but no fields found")


if __name__ == "__main__":
    main()