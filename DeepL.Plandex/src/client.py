"""
DeepL API client implementation.

This module provides the main DeepLClient class for interacting with the DeepL API,
including methods for all API endpoints with proper authentication, error handling,
and resource management.
"""

import os
import json
import logging
from typing import List, Dict, Optional, Union, Any, BinaryIO, Tuple, cast

import requests

from src.config import get_config
from src.exceptions import (
    DeepLError,
    AuthenticationError,
    InvalidRequestError,
    QuotaExceededError,
    RateLimitError,
    ServerError,
    TooManyRequestsError,
    UnsupportedLanguageError,
    TextTooLargeError,
    DocumentTooLargeError,
    ResourceNotFoundError,
    GlossaryNotFoundError,
    GlossaryLimitExceededError,
    DocumentTranslationError,
    DocumentUploadError,
    DocumentDownloadError,
    DocumentTranslationTimeoutError,
    map_http_error_to_exception,
)
from src.models import (
    SourceLanguage,
    TargetLanguage,
    Formality,
    SplitSentences,
    PreserveFormatting,
    TagHandling,
    OutlineDetection,
    GlossaryFormat,
    TextTranslationRequest,
    TextTranslationResponse,
    TranslatedText,
    LanguageInfo,
    SupportedLanguagesResponse,
    UsageInfo,
    GlossaryInfo,
    GlossaryListResponse,
    GlossaryCreateRequest,
    DocumentTranslationRequest,
    DocumentTranslationResponse,
    DocumentTranslationStatusResponse,
    DocumentTranslationResult,
)
from src.utils import (
    managed_session,
    retry,
    safe_request,
    chunk_text,
    merge_translated_chunks,
    format_glossary_entries,
    parse_glossary_entries,
    clean_memory_resources,
    sanitize_api_key,
    validate_file_size,
    get_file_mime_type,
)

# Setup logging
logger = logging.getLogger("deepl_integration")


class DeepLClient:
    """
    Client for interacting with the DeepL API.
    
    This class provides methods for all DeepL API endpoints, including text translation,
    document translation, glossary management, and more.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        api_url: Optional[str] = None,
        timeout: int = 10,
        max_retries: int = 3,
    ):
        """
        Initialize the DeepL API client.
        
        Args:
            api_key: DeepL API key. If not provided, it will be retrieved from the
                environment variable DEEPL_API_KEY.
            api_url: DeepL API URL. If not provided, it will be determined based on
                the API key.
            timeout: Request timeout in seconds.
            max_retries: Maximum number of retries for failed requests.
        """
        # Get configuration
        config = get_config()
        
        # Use provided values or fall back to configuration
        self.api_key = api_key or config["api_key"]
        self.api_url = api_url or config["api_url"]
        self.timeout = timeout or config["timeout"]
        self.max_retries = max_retries or config["max_retries"]
        
        # Log initialization with sanitized API key
        logger.debug(
            f"Initialized DeepL client with API key {sanitize_api_key(self.api_key)} "
            f"and URL {self.api_url}"
        )
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        Handle the API response, raising appropriate exceptions for errors.
        
        Args:
            response: The HTTP response from the API.
            
        Returns:
            The parsed JSON response data.
            
        Raises:
            DeepLError: If the API returns an error.
        """
        try:
            # Try to parse the response as JSON
            response_data = response.json() if response.content else {}
        except json.JSONDecodeError:
            # If the response is not valid JSON, use an empty dict
            response_data = {}
        
        # Check if the response indicates an error
        if not response.ok:
            # Map the HTTP status code to the appropriate exception
            exception = map_http_error_to_exception(response.status_code, response_data)
            
            # Log the error
            logger.error(
                f"API error: {response.status_code} - {exception.__class__.__name__}: "
                f"{exception.message}"
            )
            
            # Raise the exception
            raise exception
        
        return response_data
    
    @retry()
    def translate_text(
        self,
        text: Union[str, List[str]],
        target_lang: Union[str, TargetLanguage],
        source_lang: Optional[Union[str, SourceLanguage]] = None,
        split_sentences: Optional[Union[str, SplitSentences]] = None,
        preserve_formatting: Optional[Union[str, PreserveFormatting]] = None,
        formality: Optional[Union[str, Formality]] = None,
        glossary_id: Optional[str] = None,
        tag_handling: Optional[Union[str, TagHandling]] = None,
        outline_detection: Optional[Union[str, OutlineDetection]] = None,
        non_splitting_tags: Optional[List[str]] = None,
        splitting_tags: Optional[List[str]] = None,
        ignore_tags: Optional[List[str]] = None,
    ) -> TextTranslationResponse:
        """
        Translate text using the DeepL API.
        
        Args:
            text: Text to translate. Can be a single string or a list of strings.
            target_lang: Target language for translation.
            source_lang: Source language of the text. If not provided, DeepL will
                auto-detect the language.
            split_sentences: Controls how the translation engine should split sentences.
            preserve_formatting: Controls whether the translation engine should preserve
                some aspects of the formatting.
            formality: Controls whether the translated text should lean towards formal
                or informal language.
            glossary_id: ID of a glossary to use for the translation.
            tag_handling: Controls how tagged content should be handled.
            outline_detection: Controls whether outline detection should be used.
            non_splitting_tags: List of XML tags that should not be used to split sentences.
            splitting_tags: List of XML tags that should be used to split sentences.
            ignore_tags: List of XML tags that should be ignored.
            
        Returns:
            A TextTranslationResponse object containing the translated text.
            
        Raises:
            DeepLError: If the API returns an error.
        """
        # Convert string enums to their values
        if isinstance(target_lang, str):
            target_lang = TargetLanguage(target_lang)
        
        if source_lang is not None and isinstance(source_lang, str):
            source_lang = SourceLanguage(source_lang)
        
        if split_sentences is not None and isinstance(split_sentences, str):
            split_sentences = SplitSentences(split_sentences)
        
        if preserve_formatting is not None and isinstance(preserve_formatting, str):
            preserve_formatting = PreserveFormatting(preserve_formatting)
        
        if formality is not None and isinstance(formality, str):
            formality = Formality(formality)
        
        if tag_handling is not None and isinstance(tag_handling, str):
            tag_handling = TagHandling(tag_handling)
        
        if outline_detection is not None and isinstance(outline_detection, str):
            outline_detection = OutlineDetection(outline_detection)
        
        # Create the request model
        request = TextTranslationRequest(
            text=text,
            target_lang=target_lang,
            source_lang=source_lang or SourceLanguage.AUTO,
            split_sentences=split_sentences or SplitSentences.ON,
            preserve_formatting=preserve_formatting or PreserveFormatting.OFF,
            formality=formality or Formality.DEFAULT,
            glossary_id=glossary_id,
            tag_handling=tag_handling,
            outline_detection=outline_detection or OutlineDetection.ON,
            non_splitting_tags=non_splitting_tags,
            splitting_tags=splitting_tags,
            ignore_tags=ignore_tags,
        )
        
        # Handle large texts by chunking
        if isinstance(text, str) and len(text) > 5000:
            return self._translate_large_text(request)
        
        # Make the API request
        with managed_session(retries=self.max_retries) as session:
            url = f"{self.api_url}/translate"
            
            # Prepare the request data
            data = {
                "text": request.text if isinstance(request.text, list) else [request.text],
                "target_lang": request.target_lang.value,
            }
            
            # Add optional parameters
            if request.source_lang != SourceLanguage.AUTO:
                data["source_lang"] = request.source_lang.value
            
            if request.split_sentences != SplitSentences.ON:
                data["split_sentences"] = request.split_sentences.value
            
            if request.preserve_formatting != PreserveFormatting.OFF:
                data["preserve_formatting"] = request.preserve_formatting.value
            
            if request.formality != Formality.DEFAULT:
                data["formality"] = request.formality.value
            
            if request.glossary_id:
                data["glossary_id"] = request.glossary_id
            
            if request.tag_handling:
                data["tag_handling"] = request.tag_handling.value
            
            if request.outline_detection != OutlineDetection.ON:
                data["outline_detection"] = request.outline_detection.value
            
            if request.non_splitting_tags:
                data["non_splitting_tags"] = ",".join(request.non_splitting_tags)
            
            if request.splitting_tags:
                data["splitting_tags"] = ",".join(request.splitting_tags)
            
            if request.ignore_tags:
                data["ignore_tags"] = ",".join(request.ignore_tags)
            
            # Set authentication header
            headers = {"Authorization": f"DeepL-Auth-Key {self.api_key}"}
            
            # Make the request
            response = safe_request(
                session=session,
                method="POST",
                url=url,
                headers=headers,
                json=data,
                timeout=self.timeout,
            )
            
            # Handle the response
            response_data = self._handle_response(response)
            
            # Parse the response
            translations = []
            for translation in response_data.get("translations", []):
                translations.append(
                    TranslatedText(
                        text=translation["text"],
                        detected_source_language=SourceLanguage(
                            translation["detected_source_language"]
                        ),
                    )
                )
            
            return TextTranslationResponse(translations=translations)
    
    def _translate_large_text(self, request: TextTranslationRequest) -> TextTranslationResponse:
        """
        Translate a large text by splitting it into smaller chunks.
        
        Args:
            request: The translation request.
            
        Returns:
            A TextTranslationResponse object containing the translated text.
        """
        if isinstance(request.text, list):
            # If the text is already a list, translate each item separately
            all_translations = []
            for text_item in request.text:
                # Create a new request with a single text item
                single_request = TextTranslationRequest(
                    text=text_item,
                    target_lang=request.target_lang,
                    source_lang=request.source_lang,
                    split_sentences=request.split_sentences,
                    preserve_formatting=request.preserve_formatting,
                    formality=request.formality,
                    glossary_id=request.glossary_id,
                    tag_handling=request.tag_handling,
                    outline_detection=request.outline_detection,
                    non_splitting_tags=request.non_splitting_tags,
                    splitting_tags=request.splitting_tags,
                    ignore_tags=request.ignore_tags,
                )
                
                # Translate the single text item
                response = self._translate_large_text(single_request)
                all_translations.extend(response.translations)
            
            return TextTranslationResponse(translations=all_translations)
        
        # Split the text into smaller chunks
        text = cast(str, request.text)  # We know it's a string at this point
        chunks = chunk_text(text, max_chunk_size=5000)
        
        # Translate each chunk separately
        translated_chunks = []
        detected_source_language = None
        
        for chunk in chunks:
            # Create a new request with the chunk
            chunk_request = TextTranslationRequest(
                text=chunk,
                target_lang=request.target_lang,
                source_lang=request.source_lang,
                split_sentences=request.split_sentences,
                preserve_formatting=request.preserve_formatting,
                formality=request.formality,
                glossary_id=request.glossary_id,
                tag_handling=request.tag_handling,
                outline_detection=request.outline_detection,
                non_splitting_tags=request.non_splitting_tags,
                splitting_tags=request.splitting_tags,
                ignore_tags=request.ignore_tags,
            )
            
            # Translate the chunk
            response = self.translate_text(
                text=chunk_request.text,
                target_lang=chunk_request.target_lang,
                source_lang=chunk_request.source_lang,
                split_sentences=chunk_request.split_sentences,
                preserve_formatting=chunk_request.preserve_formatting,
                formality=chunk_request.formality,
                glossary_id=chunk_request.glossary_id,
                tag_handling=chunk_request.tag_handling,
                outline_detection=chunk_request.outline_detection,
                non_splitting_tags=chunk_request.non_splitting_tags,
                splitting_tags=chunk_request.splitting_tags,
                ignore_tags=chunk_request.ignore_tags,
            )
            
            # Store the translated chunk
            if response.translations:
                translated_chunks.append(response.translations[0].text)
                
                # Use the detected source language from the first chunk
                if detected_source_language is None:
                    detected_source_language = response.translations[0].detected_source_language
        
        # Merge the translated chunks
        merged_text = merge_translated_chunks(translated_chunks)
        
        # Create a single translation response
        return TextTranslationResponse(
            translations=[
                TranslatedText(
                    text=merged_text,
                    detected_source_language=detected_source_language or SourceLanguage.AUTO,
                )
            ]
        )
    
    @retry()
    def get_usage(self) -> UsageInfo:
        """
        Get the usage information for the DeepL API account.
        
        Returns:
            A UsageInfo object containing the character count and character limit.
            
        Raises:
            DeepLError: If the API returns an error.
        """
        with managed_session(retries=self.max_retries) as session:
            url = f"{self.api_url}/usage"
            
            # Set authentication header
            headers = {"Authorization": f"DeepL-Auth-Key {self.api_key}"}
            
            # Make the request
            response = safe_request(
                session=session,
                method="GET",
                url=url,
                headers=headers,
                timeout=self.timeout,
            )
            
            # Handle the response
            response_data = self._handle_response(response)
            
            # Parse the response
            return UsageInfo(
                character_count=response_data.get("character_count", 0),
                character_limit=response_data.get("character_limit", 0),
            )
    
    @retry()
    def get_supported_languages(
        self, target: bool = False
    ) -> SupportedLanguagesResponse:
        """
        Get the list of supported languages for the DeepL API.
        
        Args:
            target: Whether to get the list of supported target languages.
                If False, get the list of supported source languages.
                
        Returns:
            A SupportedLanguagesResponse object containing the list of supported languages.
            
        Raises:
            DeepLError: If the API returns an error.
        """
        with managed_session(retries=self.max_retries) as session:
            url = f"{self.api_url}/languages"
            
            # Set authentication header
            headers = {"Authorization": f"DeepL-Auth-Key {self.api_key}"}
            
            # Prepare query parameters
            params = {"type": "target" if target else "source"}
            
            # Make the request
            response = safe_request(
                session=session,
                method="GET",
                url=url,
                headers=headers,
                params=params,
                timeout=self.timeout,
            )
            
            # Handle the response
            response_data = self._handle_response(response)
            
            # Parse the response
            languages = []
            for language in response_data:
                languages.append(
                    LanguageInfo(
                        language=language["language"],
                        name=language["name"],
                        supports_formality=language.get("supports_formality", False),
                    )
                )
            
            # Create the response object
            if target:
                return SupportedLanguagesResponse(
                    source_languages=[],
                    target_languages=languages,
                )
            else:
                return SupportedLanguagesResponse(
                    source_languages=languages,
                    target_languages=[],
                )
    
    @retry()
    def get_all_supported_languages(self) -> SupportedLanguagesResponse:
        """
        Get the list of all supported languages for the DeepL API.
        
        Returns:
            A SupportedLanguagesResponse object containing the list of all supported languages.
            
        Raises:
            DeepLError: If the API returns an error.
        """
        # Get source languages
        source_languages_response = self.get_supported_languages(target=False)
        
        # Get target languages
        target_languages_response = self.get_supported_languages(target=True)
        
        # Combine the responses
        return SupportedLanguagesResponse(
            source_languages=source_languages_response.source_languages,
            target_languages=target_languages_response.target_languages,
        )
    
    @retry()
    def create_glossary(
        self,
        name: str,
        source_lang: Union[str, SourceLanguage],
        target_lang: Union[str, TargetLanguage],
        entries: Union[str, Dict[str, str]],
        entries_format: Optional[Union[str, GlossaryFormat]] = None,
    ) -> GlossaryInfo:
        """
        Create a glossary for the DeepL API.
        
        Args:
            name: Name of the glossary.
            source_lang: Source language of the glossary.
            target_lang: Target language of the glossary.
            entries: Glossary entries. Can be a string in the specified format or a
                dictionary of source terms (keys) and target terms (values).
            entries_format: Format of the entries if provided as a string.
                
        Returns:
            A GlossaryInfo object containing information about the created glossary.
            
        Raises:
            DeepLError: If the API returns an error.
        """
        # Convert string enums to their values
        if isinstance(source_lang, str):
            source_lang = SourceLanguage(source_lang)
        
        if isinstance(target_lang, str):
            target_lang = TargetLanguage(target_lang)
        
        if entries_format is not None and isinstance(entries_format, str):
            entries_format = GlossaryFormat(entries_format)
        
        # Format entries if provided as a dictionary
        if isinstance(entries, dict):
            entries_str = format_glossary_entries(
                entries, format_type=(entries_format or GlossaryFormat.CSV).value
            )
        else:
            entries_str = entries
        
        with managed_session(retries=self.max_retries) as session:
            url = f"{self.api_url}/glossaries"
            
            # Set authentication header
            headers = {
                "Authorization": f"DeepL-Auth-Key {self.api_key}",
                "Content-Type": "application/json",
            }
            
            # Prepare the request data
            data = {
                "name": name,
                "source_lang": source_lang.value,
                "target_lang": target_lang.value,
                "entries": entries_str,
                "entries_format": (entries_format or GlossaryFormat.CSV).value,
            }
            
            # Make the request
            response = safe_request(
                session=session,
                method="POST",
                url=url,
                headers=headers,
                json=data,
                timeout=self.timeout,
            )
            
            # Handle the response
            response_data = self._handle_response(response)
            
            # Parse the response
            return GlossaryInfo(
                glossary_id=response_data.get("glossary_id", ""),
                name=response_data.get("name", ""),
                source_lang=SourceLanguage(response_data.get("source_lang", "")),
                target_lang=TargetLanguage(response_data.get("target_lang", "")),
                creation_time=response_data.get("creation_time", ""),
                entry_count=response_data.get("entry_count", 0),
            )
    
    @retry()
    def get_glossary(self, glossary_id: str) -> GlossaryInfo:
        """
        Get information about a glossary.
        
        Args:
            glossary_id: ID of the glossary.
                
        Returns:
            A GlossaryInfo object containing information about the glossary.
            
        Raises:
            DeepLError: If the API returns an error.
        """
        with managed_session(retries=self.max_retries) as session:
            url = f"{self.api_url}/glossaries/{glossary_id}"
            
            # Set authentication header
            headers = {"Authorization": f"DeepL-Auth-Key {self.api_key}"}
            
            # Make the request
            response = safe_request(
                session=session,
                method="GET",
                url=url,
                headers=headers,
                timeout=self.timeout,
            )
            
            # Handle the response
            response_data = self._handle_response(response)
            
            # Parse the response
            return GlossaryInfo(
                glossary_id=response_data.get("glossary_id", ""),
                name=response_data.get("name", ""),
                source_lang=SourceLanguage(response_data.get("source_lang", "")),
                target_lang=TargetLanguage(response_data.get("target_lang", "")),
                creation_time=response_data.get("creation_time", ""),
                entry_count=response_data.get("entry_count", 0),
            )
    
    @retry()
    def get_glossary_entries(
        self, glossary_id: str, entries_format: Optional[Union[str, GlossaryFormat]] = None
    ) -> Dict[str, str]:
        """
        Get the entries of a glossary.
        
        Args:
            glossary_id: ID of the glossary.
            entries_format: Format of the entries in the response.
                
        Returns:
            A dictionary of source terms (keys) and target terms (values).
            
        Raises:
            DeepLError: If the API returns an error.
        """
        # Convert string enum to its value
        if entries_format is not None and isinstance(entries_format, str):
            entries_format = GlossaryFormat(entries_format)
        
        with managed_session(retries=self.max_retries) as session:
            url = f"{self.api_url}/glossaries/{glossary_id}/entries"
            
            # Set authentication header
            headers = {"Authorization": f"DeepL-Auth-Key {self.api_key}"}
            
            # Prepare query parameters
            params = {}
            if entries_format:
                params["format"] = entries_format.value
            
            # Make the request
            response = safe_request(
                session=session,
                method="GET",
                url=url,
                headers=headers,
                params=params,
                timeout=self.timeout,
            )
            
            # Handle the response
            if not response.ok:
                self._handle_response(response)  # This will raise an exception
            
            # Parse the response
            return parse_glossary_entries(
                response.text, format_type=(entries_format or GlossaryFormat.CSV).value
            )
    
    @retry()
    def list_glossaries(self) -> GlossaryListResponse:
        """
        List all glossaries.
        
        Returns:
            A GlossaryListResponse object containing the list of glossaries.
            
        Raises:
            DeepLError: If the API returns an error.
        """
        with managed_session(retries=self.max_retries) as session:
            url = f"{self.api_url}/glossaries"
            
            # Set authentication header
            headers = {"Authorization": f"DeepL-Auth-Key {self.api_key}"}
            
            # Make the request
            response = safe_request(
                session=session,
                method="GET",
                url=url,
                headers=headers,
                timeout=self.timeout,
            )
            
            # Handle the response
            response_data = self._handle_response(response)
            
            # Parse the response
            glossaries = []
            for glossary in response_data.get("glossaries", []):
                glossaries.append(
                    GlossaryInfo(
                        glossary_id=glossary.get("glossary_id", ""),
                        name=glossary.get("name", ""),
                        source_lang=SourceLanguage(glossary.get("source_lang", "")),
                        target_lang=TargetLanguage(glossary.get("target_lang", "")),
                        creation_time=glossary.get("creation_time", ""),
                        entry_count=glossary.get("entry_count", 0),
                    )
                )
            
            return GlossaryListResponse(glossaries=glossaries)
    
    @retry()
    def delete_glossary(self, glossary_id: str) -> None:
        """
        Delete a glossary.
        
        Args:
            glossary_id: ID of the glossary.
            
        Raises:
            DeepLError: If the API returns an error.
        """
        with managed_session(retries=self.max_retries) as session:
            url = f"{self.api_url}/glossaries/{glossary_id}"
            
            # Set authentication header
            headers = {"Authorization": f"DeepL-Auth-Key {self.api_key}"}
            
            # Make the request
            response = safe_request(
                session=session,
                method="DELETE",
                url=url,
                headers=headers,
                timeout=self.timeout,
            )
            
            # Handle the response
            if not response.ok:
                self._handle_response(response)  # This will raise an exception
    
    @retry()
    def translate_document(
        self,
        input_file: Union[str, BinaryIO],
        target_lang: Union[str, TargetLanguage],
        source_lang: Optional[Union[str, SourceLanguage]] = None,
        formality: Optional[Union[str, Formality]] = None,
        glossary_id: Optional[str] = None,
        output_file: Optional[Union[str, BinaryIO]] = None,
    ) -> DocumentTranslationResult:
        """
        Translate a document using the DeepL API.
        
        Args:
            input_file: Path to the input file or a file-like object.
            target_lang: Target language for translation.
            source_lang: Source language of the document. If not provided, DeepL will
                auto-detect the language.
            formality: Controls whether the translated text should lean towards formal
                or informal language.
            glossary_id: ID of a glossary to use for the translation.
            output_file: Path to the output file or a file-like object. If not provided,
                the translated document will not be saved to a file.
                
        Returns:
            A DocumentTranslationResult object containing information about the
            translated document.
            
        Raises:
            DeepLError: If the API returns an error.
        """
        # Convert string enums to their values
        if isinstance(target_lang, str):
            target_lang = TargetLanguage(target_lang)
        
        if source_lang is not None and isinstance(source_lang, str):
            source_lang = SourceLanguage(source_lang)
        
        if formality is not None and isinstance(formality, str):
            formality = Formality(formality)
        
        # Upload the document
        document_handle = self.upload_document(
            input_file=input_file,
            target_lang=target_lang,
            source_lang=source_lang,
            formality=formality,
            glossary_id=glossary_id,
        )
        
        # Wait for the translation to complete
        document_status = self.wait_for_document(
            document_id=document_handle.document_id,
            document_key=document_handle.document_key,
        )
        
        # Download the translated document
        if output_file:
            self.download_document(
                document_id=document_handle.document_id,
                document_key=document_handle.document_key,
                output_file=output_file,
            )
        
        return DocumentTranslationResult(
            document_id=document_handle.document_id,
            document_key=document_handle.document_key,
        )
    
    @retry()
    def upload_document(
        self,
        input_file: Union[str, BinaryIO],
        target_lang: Union[str, TargetLanguage],
        source_lang: Optional[Union[str, SourceLanguage]] = None,
        formality: Optional[Union[str, Formality]] = None,
        glossary_id: Optional[str] = None,
    ) -> DocumentTranslationResponse:
        """
        Upload a document for translation.
        
        Args:
            input_file: Path to the input file or a file-like object.
            target_lang: Target language for translation.
            source_lang: Source language of the document. If not provided, DeepL will
                auto-detect the language.
            formality: Controls whether the translated text should lean towards formal
                or informal language.
            glossary_id: ID of a glossary to use for the translation.
                
        Returns:
            A DocumentTranslationResponse object containing the document ID and key.
            
        Raises:
            DeepLError: If the API returns an error.
        """
        # Convert string enums to their values
        if isinstance(target_lang, str):
            target_lang = TargetLanguage(target_lang)
        
        if source_lang is not None and isinstance(source_lang, str):
            source_lang = SourceLanguage(source_lang)
        
        if formality is not None and isinstance(formality, str):
            formality = Formality(formality)
        
        # Create the request model
        request = DocumentTranslationRequest(
            target_lang=target_lang,
            source_lang=source_lang or SourceLanguage.AUTO,
            formality=formality or Formality.DEFAULT,
            glossary_id=glossary_id,
        )
        
        # Prepare the file
        if isinstance(input_file, str):
            # Check if the file exists
            if not os.path.exists(input_file):
                raise FileNotFoundError(f"File not found: {input_file}")
            
            # Check if the file size is valid
            if not validate_file_size(input_file):
                raise DocumentTooLargeError(
                    "The document is too large. Maximum size is 50 MB."
                )
            
            # Open the file
            file_obj = open(input_file, "rb")
            file_name = os.path.basename(input_file)
        else:
            # Use the provided file-like object
            file_obj = input_file
            file_name = getattr(input_file, "name", "document")
        
        try:
            with managed_session(retries=self.max_retries) as session:
                url = f"{self.api_url}/document"
                
                # Set authentication header
                headers = {"Authorization": f"DeepL-Auth-Key {self.api_key}"}
                
                # Prepare the request data
                data = {
                    "target_lang": request.target_lang.value,
                }
                
                # Add optional parameters
                if request.source_lang != SourceLanguage.AUTO:
                    data["source_lang"] = request.source_lang.value
                
                if request.formality != Formality.DEFAULT:
                    data["formality"] = request.formality.value
                
                if request.glossary_id:
                    data["glossary_id"] = request.glossary_id
                
                # Prepare the file
                files = {"file": (file_name, file_obj)}
                
                # Make the request
                response = safe_request(
                    session=session,
                    method="POST",
                    url=url,
                    headers=headers,
                    data=data,
                    files=files,
                    timeout=self.timeout,
                )
                
                # Handle the response
                response_data = self._handle_response(response)
                
                # Parse the response
                return DocumentTranslationResponse(
                    document_id=response_data.get("document_id", ""),
                    document_key=response_data.get("document_key", ""),
                )
        finally:
            # Close the file if we opened it
            if isinstance(input_file, str) and file_obj:
                file_obj.close()
    
    @retry()
    def get_document_status(
        self, document_id: str, document_key: str
    ) -> DocumentTranslationStatusResponse:
        """
        Get the status of a document translation.
        
        Args:
            document_id: ID of the document.
            document_key: Key of the document.
                
        Returns:
            A DocumentTranslationStatusResponse object containing the status of the
            document translation.
            
        Raises:
            DeepLError: If the API returns an error.
        """
        with managed_session(retries=self.max_retries) as session:
            url = f"{self.api_url}/document/{document_id}"
            
            # Set authentication header
            headers = {"Authorization": f"DeepL-Auth-Key {self.api_key}"}
            
            # Prepare query parameters
            params = {"document_key": document_key}
            
            # Make the request
            response = safe_request(
                session=session,
                method="GET",
                url=url,
                headers=headers,
                params=params,
                timeout=self.timeout,
            )
            
            # Handle the response
            response_data = self._handle_response(response)
            
            # Parse the response
            return DocumentTranslationStatusResponse(
                document_id=document_id,
                status=response_data.get("status", ""),
                seconds_remaining=response_data.get("seconds_remaining"),
                billed_characters=response_data.get("billed_characters"),
            )
    
    def wait_for_document(
        self,
        document_id: str,
        document_key: str,
        interval: int = 5,
        timeout: int = 300,
    ) -> DocumentTranslationStatusResponse:
        """
        Wait for a document translation to complete.
        
        Args:
            document_id: ID of the document.
            document_key: Key of the document.
            interval: Interval in seconds between status checks.
            timeout: Maximum time in seconds to wait for the translation to complete.
                
        Returns:
            A DocumentTranslationStatusResponse object containing the status of the
            document translation.
            
        Raises:
            DeepLError: If the API returns an error.
            DocumentTranslationTimeoutError: If the translation times out.
        """
        import time
        
        start_time = time.time()
        
        while True:
            # Check if we've exceeded the timeout
            if time.time() - start_time > timeout:
                raise DocumentTranslationTimeoutError(
                    f"Document translation timed out after {timeout} seconds."
                )
            
            # Get the document status
            status = self.get_document_status(
                document_id=document_id, document_key=document_key
            )
            
            # Check if the translation is done
            if status.status == "done":
                return status
            
            # Check if the translation failed
            if status.status == "error":
                raise DocumentTranslationError(
                    f"Document translation failed with status: {status.status}"
                )
            
            # Wait for the next check
            time.sleep(interval)
    
    @retry()
    def download_document(
        self,
        document_id: str,
        document_key: str,
        output_file: Union[str, BinaryIO],
    ) -> None:
        """
        Download a translated document.
        
        Args:
            document_id: ID of the document.
            document_key: Key of the document.
            output_file: Path to the output file or a file-like object.
                
        Raises:
            DeepLError: If the API returns an error.
        """
        with managed_session(retries=self.max_retries) as session:
            url = f"{self.api_url}/document/{document_id}/result"
            
            # Set authentication header
            headers = {"Authorization": f"DeepL-Auth-Key {self.api_key}"}
            
            # Prepare query parameters
            params = {"document_key": document_key}
            
            # Make the request
            response = safe_request(
                session=session,
                method="GET",
                url=url,
                headers=headers,
                params=params,
                timeout=self.timeout,
                stream=True,
            )
            
            # Handle the response
            if not response.ok:
                self._handle_response(response)  # This will raise an exception
            
            # Save the document
            if isinstance(output_file, str):
                # Create the directory if it doesn't exist
                os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
                
                # Open the file
                with open(output_file, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
            else:
                # Use the provided file-like object
                for chunk in response.iter_content(chunk_size=8192):
                    output_file.write(chunk)
    
    def close(self) -> None:
        """
        Close the client and clean up resources.
        
        This method should be called when the client is no longer needed.
        """
        clean_memory_resources()
    
    def __enter__(self) -> "DeepLClient":
        """
        Enter the context manager.
        
        Returns:
            The client instance.
        """
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Exit the context manager.
        
        Args:
            exc_type: Exception type.
            exc_val: Exception value.
            exc_tb: Exception traceback.
        """
        self.close()
