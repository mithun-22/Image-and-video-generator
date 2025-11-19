import google.generativeai as genai
from pathlib import Path
import json
from datetime import datetime
from config import Config
from processors.text_processor import TextExtractor, TextProcessor
from processors.image_generator import ImageGenerator


class ContentGenerator:
    """Main orchestrator for content generation"""
    
    def __init__(self):
        Config.setup_directories()
        
        if not Config.GEMINI_API_KEY:
            raise ValueError("Please set GEMINI_API_KEY in .env file")
        
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')
        self.image_gen = ImageGenerator(Config.GEMINI_API_KEY)
        
    def summarize_text(self, text: str, max_points: int = 8) -> Dict:
        """
        Generate structured summary from text
        
        Returns:
            Dict with title, executive_summary, key_points, sections
        """
        prompt = f"""
        Analyze the following text and create a comprehensive summary in JSON format.
        
        Text: {text[:8000]}
        
        Provide a JSON response with this exact structure:
        {{
            "title": "A clear, descriptive title",
            "executive_summary": "2-3 sentence overview of the main points",
            "key_points": [
                "First key point",
                "Second key point",
                "Third key point"
            ],
            "sections": [
                {{
                    "heading": "Section name",
                    "content": "Detailed section summary",
                    "importance": "high/medium/low"
                }}
            ]
        }}
        
        Limit key_points to {max_points} most important points.
        Provide ONLY the JSON, no additional text.
        """
        
        try:
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if result_text.startswith('```'):
                result_text = result_text.split('```')[1]
                if result_text.startswith('json'):
                    result_text = result_text[4:]
            
            summary = json.loads(result_text)
            return summary
        
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            # Return fallback structure
            return {
                "title": "Document Summary",
                "executive_summary": text[:200] + "...",
                "key_points": ["Summary generation in progress"],
                "sections": []
            }
    
    def process_file(
        self, 
        file_path: str, 
        generate_images: bool = True
    ) -> Dict:
        """
        Complete processing pipeline for a document
        
        Args:
            file_path: Path to input file
            generate_images: Whether to generate visualization images
            
        Returns:
            Dict with processing results
        """
        print(f"\n{'='*60}")
        print(f"Processing: {file_path}")
        print(f"{'='*60}\n")
        
        # Step 1: Extract text
        print("Step 1: Extracting text...")
        text = TextExtractor.extract(file_path)
        clean_text = TextProcessor.clean_text(text)
        
        stats = TextProcessor.get_text_stats(clean_text)
        print(f"Extracted {stats['total_words']} words, "
              f"{stats['total_sentences']} sentences")
        
        # Step 2: Chunk if needed
        print("\nStep 2: Processing chunks...")
        chunks = TextProcessor.chunk_text(clean_text, chunk_size=4000)
        print(f"Created {len(chunks)} chunks")
        
        # Step 3: Summarize
        print("\nStep 3: Generating summary...")
        # For large documents, summarize chunks first
        if len(chunks) > 1:
            chunk_summaries = []
            for i, chunk in enumerate(chunks[:5]):  # Limit to first 5 chunks
                print(f"  Summarizing chunk {i+1}/{min(5, len(chunks))}...")
                summary = self.summarize_text(chunk, max_points=4)
                chunk_summaries.append(summary['executive_summary'])
            
            # Combine chunk summaries
            combined = " ".join(chunk_summaries)
            final_summary = self.summarize_text(combined, max_points=8)
        else:
            final_summary = self.summarize_text(clean_text, max_points=8)
        
        print(f"\nSummary generated:")
        print(f"Title: {final_summary['title']}")
        print(f"Key Points: {len(final_summary['key_points'])}")
        
        # Step 4: Save summary
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_file = Config.SUMMARY_DIR / f"summary_{timestamp}.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(final_summary, f, indent=2, ensure_ascii=False)
        print(f"\nSummary saved: {summary_file}")
        
        # Step 5: Generate images
        image_paths = []
        if generate_images:
            print("\nStep 4: Generating visualization...")
            
            # Main summary image
            main_image = Config.IMAGE_DIR / f"summary_{timestamp}.png"
            self.image_gen.create_summary_visualization(
                summary_data=final_summary,
                output_path=str(main_image),
                template="modern"
            )
            image_paths.append(str(main_image))
            
            # Generate image for each section
            for i, section in enumerate(final_summary.get('sections', [])[:3]):
                section_image = Config.IMAGE_DIR / f"section_{i+1}_{timestamp}.png"
                self.image_gen.generate_text_image(
                    text=section['content'],
                    title=section['heading'],
                    output_path=str(section_image)
                )
                image_paths.append(str(section_image))
        
        print(f"\n{'='*60}")
        print("Processing Complete!")
        print(f"{'='*60}")
        
        return {
            'summary': final_summary,
            'summary_file': str(summary_file),
            'images': image_paths,
            'stats': stats,
            'timestamp': timestamp
        }


def main():
    """Main execution function"""
    
    print("\n" + "="*60)
    print("AI Content Generator - Week 1 Implementation")
    print("="*60 + "\n")
    
    # Initialize
    generator = ContentGenerator()
    
    # Example usage with a test file
    # You can replace this with your actual file path
    test_text = """
    Artificial Intelligence and Machine Learning in Healthcare
    
    The healthcare industry is undergoing a revolutionary transformation through 
    the integration of artificial intelligence and machine learning technologies. 
    These advanced systems are enabling healthcare providers to deliver more 
    accurate diagnoses, personalized treatment plans, and improved patient outcomes.
    
    Key Applications:
    1. Medical Imaging Analysis: AI algorithms can detect anomalies in X-rays, 
    MRIs, and CT scans with remarkable accuracy, often surpassing human radiologists.
    
    2. Predictive Analytics: Machine learning models analyze patient data to 
    predict disease progression and identify high-risk patients before symptoms appear.
    
    3. Drug Discovery: AI accelerates the drug development process by identifying 
    promising compounds and predicting their effectiveness.
    
    4. Personalized Medicine: AI systems analyze genetic information to recommend 
    tailored treatment approaches for individual patients.
    
    Challenges and Considerations:
    While AI offers tremendous potential, healthcare organizations must address 
    important concerns including data privacy, algorithmic bias, regulatory 
    compliance, and the need for transparency in AI decision-making processes.
    
    The integration of AI in healthcare requires collaboration between technology 
    experts, medical professionals, and policymakers to ensure these tools enhance 
    rather than replace human expertise.
    
    Future Outlook:
    As AI technologies continue to evolve, we can expect even more sophisticated 
    applications in healthcare, from robotic surgery to mental health support 
    and chronic disease management. The key to success lies in maintaining a 
    human-centered approach while leveraging the power of artificial intelligence.
    """
    
    # Create a test file
    test_file = Config.UPLOAD_DIR / "test_document.txt"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_text)
    
    print(f"Created test file: {test_file}\n")
    
    # Process the file
    result = generator.process_file(
        file_path=str(test_file),
        generate_images=True
    )
    
    # Display results
    print("\n" + "="*60)
    print("RESULTS SUMMARY")
    print("="*60)
    print(f"\nTitle: {result['summary']['title']}")
    print(f"\nExecutive Summary:\n{result['summary']['executive_summary']}")
    print(f"\nKey Points:")
    for i, point in enumerate(result['summary']['key_points'], 1):
        print(f"  {i}. {point}")
    
    print(f"\nGenerated Files:")
    print(f"  Summary: {result['summary_file']}")
    for img in result['images']:
        print(f"  Image: {img}")
    
    print("\n" + "="*60)
    print("To process your own file, replace test_file with your file path")
    print("Supported formats: .txt, .pdf, .docx")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
