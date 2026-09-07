from unittest.mock import MagicMock, patch
from src.rag.preprocess import UniversalPreprocessor

def test_pdf_parsing_strategy():
    """Verifies text extraction handling, page isolation, and segmentation limits for PDFs."""
    preprocessor = UniversalPreprocessor(max_words=10)
    
    # Bypass standard disk existence checks and patch the underlying PdfReader engine
    with patch("os.path.exists", return_value=True), \
         patch("src.rag.preprocess.PdfReader") as MockPdfReader:
        
        # Instantiate a mock page that responds with a targeted 11-word text payload string
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Star Trek TNG features Commander Data exploring complex human emotional architectures."
        
        mock_reader = MagicMock()
        mock_reader.pages = [mock_page]
        MockPdfReader.return_value = mock_reader
        
        # Fire the ingestion parser factory
        chunks = preprocessor.chunk_document("starfleet_manifest.pdf")
        
        # 11 words configured against max_words=10 must produce exactly 2 chunk divisions
        assert len(chunks) == 2
        
        # Validate metadata element injection
        assert chunks[0]["metadata"]["source"] == "starfleet_manifest.pdf"
        assert chunks[0]["metadata"]["section"] == "Page_1"
        assert chunks[0]["metadata"]["chunk_segment"] == 0
        assert "Star Trek TNG" in chunks[0]["content"]
        
        # Validate spillover word segment distribution
        assert chunks[1]["metadata"]["chunk_segment"] == 1
        assert chunks[1]["content"] == "architectures."
