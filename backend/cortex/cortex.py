# knowledge_ingestion.py

import logging
import os
from typing import List, Tuple, Dict, Any

import openai
import pytesseract
import soundfile as sf
import textract
from deeplake.core.vectorstore import VectorStore
from PIL import Image

from interfaces.voice_interface import VoiceInterface  # Ensure this module exists and is correctly implemented

# Configure Logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('logs/knowledge_ingestion.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class KnowledgeIngestion:
    def __init__(self, user_id: str):
        """
        Initializes the KnowledgeIngestion instance.

        Args:
            user_id (str): Unique identifier for the user.
        """
        self.user_id = user_id
        self.vector_store_path = f'vector_store_{user_id}'
        
        # Initialize Deep Lake Vector Store with ActiveLoop Token
        active_loop_token = os.getenv('ACTIVELOOP_TOKEN')
        if not active_loop_token:
            raise ValueError("ACTIVELOOP_TOKEN environment variable is not set")
        
        self.vector_store = VectorStore(
            path=self.vector_store_path,
            token=active_loop_token
        )
        
        self.voice_interface = VoiceInterface()
        
        # Set up OpenAI API key
        openai.api_key = os.getenv('OPENAI_API_KEY')
        if not openai.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")

    def embedding_function(self, texts: List[str], model: str = "text-embedding-ada-002") -> List[List[float]]:
        """
        Generates embeddings for a list of texts using OpenAI's API.

        Args:
            texts (List[str]): List of text strings to embed.
            model (str, optional): OpenAI model to use for embeddings. Defaults to "text-embedding-ada-002".

        Returns:
            List[List[float]]: List of embeddings.
        """
        try:
            if isinstance(texts, str):
                texts = [texts]
            texts = [t.replace("\n", " ") for t in texts]
            response = openai.Embedding.create(input=texts, model=model)
            embeddings = [data['embedding'] for data in response['data']]
            logger.debug("Generated embeddings for texts.")
            return embeddings
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise

    def ingest_text(self, text: str, metadata: Dict[str, Any] = None):
        """
        Ingests a single text entry into the vector store.

        Args:
            text (str): Text to ingest.
            metadata (Dict[str, Any], optional): Metadata associated with the text. Defaults to None.
        """
        try:
            if metadata is None:
                metadata = {}
            self.vector_store.add(
                text=[text],
                embedding_function=self.embedding_function,
                embedding_data=[text],
                metadata=[metadata]
            )
            logger.info("Text ingested successfully.")
        except Exception as e:
            logger.error(f"Error ingesting text: {e}")

    def ingest_document(self, file_path: str, metadata: Dict[str, Any] = None):
        """
        Ingests a document (e.g., PDF, DOCX) into the vector store.

        Args:
            file_path (str): Path to the document file.
            metadata (Dict[str, Any], optional): Metadata associated with the document. Defaults to None.
        """
        try:
            text = textract.process(file_path).decode('utf-8')
            if metadata is None:
                metadata = {}
            metadata['source'] = file_path
            self.ingest_text(text, metadata)
            logger.info(f"Document '{file_path}' ingested successfully.")
        except Exception as e:
            logger.error(f"Error ingesting document '{file_path}': {e}")

    def ingest_audio(self, audio_path: str, metadata: Dict[str, Any] = None):
        """
        Ingests an audio file by transcribing it and storing the transcript.

        Args:
            audio_path (str): Path to the audio file.
            metadata (Dict[str, Any], optional): Metadata associated with the audio. Defaults to None.
        """
        try:
            audio, sample_rate = sf.read(audio_path)
            transcription = self.voice_interface.pipe(audio)["text"]
            if metadata is None:
                metadata = {}
            metadata['source'] = audio_path
            self.ingest_text(transcription, metadata)
            logger.info(f"Audio '{audio_path}' ingested successfully.")
        except Exception as e:
            logger.error(f"Error ingesting audio '{audio_path}': {e}")

    def ingest_image(self, image_path: str, metadata: Dict[str, Any] = None):
        """
        Ingests an image by extracting text from it and storing the extracted text.

        Args:
            image_path (str): Path to the image file.
            metadata (Dict[str, Any], optional): Metadata associated with the image. Defaults to None.
        """
        try:
            image = Image.open(image_path)
            extracted_text = pytesseract.image_to_string(image)
            if metadata is None:
                metadata = {}
            metadata['source'] = image_path
            self.ingest_text(extracted_text, metadata)
            logger.info(f"Image '{image_path}' ingested successfully.")
        except Exception as e:
            logger.error(f"Error ingesting image '{image_path}': {e}")

    def ingest_batch(self, data_items: List[Tuple[str, str, Dict[str, Any]]]):
        """
        Ingests a batch of data items into the vector store.

        Args:
            data_items (List[Tuple[str, str, Dict[str, Any]]]): List of tuples containing data type, path, and metadata.
        """
        for data_type, data_path, metadata in data_items:
            if data_type == 'text':
                self.ingest_text(data_path, metadata)
            elif data_type == 'document':
                self.ingest_document(data_path, metadata)
            elif data_type == 'audio':
                self.ingest_audio(data_path, metadata)
            elif data_type == 'image':
                self.ingest_image(data_path, metadata)
            else:
                logger.warning(f"Unsupported data type '{data_type}' for path '{data_path}'")

    def search_knowledge(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """
        Searches the vector store for the most relevant entries to the query.

        Args:
            query (str): The search query.
            limit (int, optional): Number of top results to return. Defaults to 5.

        Returns:
            Dict[str, Any]: Search results containing text, scores, ids, and metadata.
        """
        try:
            search_results = self.vector_store.search(
                embedding_data=query,
                embedding_function=self.embedding_function,
                k=limit
            )
            logger.info(f"Search completed for query: '{query}' with limit: {limit}")
            return search_results
        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            return {}

    def listen_and_ingest(self, duration: int = 5, sample_rate: int = 16000, metadata: Dict[str, Any] = None):
        """
        Listens to audio input, transcribes it, and ingests the transcription.

        Args:
            duration (int, optional): Duration to listen in seconds. Defaults to 5.
            sample_rate (int, optional): Sampling rate for audio. Defaults to 16000.
            metadata (Dict[str, Any], optional): Metadata associated with the audio. Defaults to None.
        """
        try:
            transcription = self.voice_interface.listen(duration, sample_rate)
            if transcription:
                self.ingest_text(transcription, metadata)
                logger.info("Voice input ingested successfully.")
            else:
                logger.warning("No speech detected or recognition failed.")
        except Exception as e:
            logger.error(f"Error in listen_and_ingest: {e}")

    def speak_search_results(self, query: str, limit: int = 1):
        """
        Searches the vector store and speaks out the top search result.

        Args:
            query (str): The search query.
            limit (int, optional): Number of top results to consider. Defaults to 1.
        """
        try:
            search_results = self.search_knowledge(query, limit)
            if search_results and 'text' in search_results and len(search_results['text']) > 0:
                text_to_speak = search_results['text'][0]
                self.voice_interface.speak(text_to_speak)
                logger.info(f"Spoke search result: {text_to_speak}")
            else:
                self.voice_interface.speak("No relevant information found.")
                logger.info("No relevant information found to speak.")
        except Exception as e:
            logger.error(f"Error in speak_search_results: {e}")


class Cortex:
    def __init__(self, user_id: str):
        """
        Initializes the Cortex instance, managing user memory and interactions.

        Args:
            user_id (str): Unique identifier for the user.
        """
        self.user_id = user_id
        self.ki = KnowledgeIngestion(user_id=user_id)
        self.memory_store_path = f'memory_store_{user_id}'
        
        # Initialize Deep Lake Vector Store for memory
        active_loop_token = os.getenv('ACTIVELOOP_TOKEN')
        if not active_loop_token:
            raise ValueError("ACTIVELOOP_TOKEN environment variable is not set")
        
        self.memory_store = VectorStore(
            path=self.memory_store_path,
            token=active_loop_token
        )
        
        # Optionally, you can use a separate embedding model for memory
        self.embedding_model = "text-embedding-ada-002"

    def add_to_memory(self, text: str, metadata: Dict[str, Any] = None):
        """
        Adds a text entry to the user's memory.

        Args:
            text (str): Text to add to memory.
            metadata (Dict[str, Any], optional): Metadata associated with the memory entry. Defaults to None.
        """
        try:
            if metadata is None:
                metadata = {}
            self.memory_store.add(
                text=[text],
                embedding_function=lambda texts: self.ki.embedding_function(texts, model=self.embedding_model),
                embedding_data=[text],
                metadata=[metadata]
            )
            logger.info("Added to memory successfully.")
        except Exception as e:
            logger.error(f"Error adding to memory: {e}")

    def retrieve_memory(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """
        Retrieves relevant memory entries based on the query.

        Args:
            query (str): The search query.
            limit (int, optional): Number of top memory entries to retrieve. Defaults to 5.

        Returns:
            Dict[str, Any]: Retrieved memory entries.
        """
        try:
            results = self.memory_store.search(
                embedding_data=query,
                embedding_function=lambda texts: self.ki.embedding_function(texts, model=self.embedding_model),
                k=limit
            )
            logger.info(f"Retrieved {limit} memory entries for query: '{query}'")
            return results
        except Exception as e:
            logger.error(f"Error retrieving memory: {e}")
            return {}

    def rank_search_results(self, query: str, search_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Ranks search results based on relevance to the query.

        Args:
            query (str): The search query.
            search_results (Dict[str, Any]): Raw search results from the vector store.

        Returns:
            List[Dict[str, Any]]: Ranked list of search results.
        """
        try:
            # For simplicity, assuming search_results contains a 'score' key for each entry
            ranked_results = sorted(
                zip(search_results.get('text', []), search_results.get('score', []), search_results.get('metadata', [])),
                key=lambda x: x[1],
                reverse=True
            )
            ranked_list = [{'text': text, 'score': score, 'metadata': metadata} for text, score, metadata in ranked_results]
            logger.info(f"Ranked {len(ranked_list)} search results for query: '{query}'")
            return ranked_list
        except Exception as e:
            logger.error(f"Error ranking search results: {e}")
            return []

    def handle_query(self, query: str, memory_limit: int = 5, search_limit: int = 5) -> List[Dict[str, Any]]:
        """
        Handles a user query by searching both knowledge base and memory, then ranking the results.

        Args:
            query (str): The user's query.
            memory_limit (int, optional): Number of memory entries to retrieve. Defaults to 5.
            search_limit (int, optional): Number of knowledge entries to retrieve. Defaults to 5.

        Returns:
            List[Dict[str, Any]]: Combined and ranked search results from knowledge and memory.
        """
        try:
            # Search knowledge base
            knowledge_results = self.ki.search_knowledge(query, limit=search_limit)
            ranked_knowledge = self.rank_search_results(query, knowledge_results)
            
            # Search memory
            memory_results = self.retrieve_memory(query, limit=memory_limit)
            ranked_memory = self.rank_search_results(query, memory_results)
            
            # Combine results
            combined_results = ranked_memory + ranked_knowledge
            logger.info(f"Handled query: '{query}' with combined results.")
            return combined_results
        except Exception as e:
            logger.error(f"Error handling query '{query}': {e}")
            return []

    def respond_to_query(self, query: str):
        """
        Responds to a user query by retrieving and speaking the most relevant information.

        Args:
            query (str): The user's query.
        """
        try:
            results = self.handle_query(query)
            if results:
                # Assuming the top result is the most relevant
                top_result = results[0]['text']
                self.ki.voice_interface.speak(top_result)
                logger.info(f"Responded to query: '{query}' with top result.")
            else:
                self.ki.voice_interface.speak("I'm sorry, I couldn't find any relevant information.")
                logger.info(f"No results found for query: '{query}'")
        except Exception as e:
            logger.error(f"Error responding to query '{query}': {e}")


# Example Usage
if __name__ == "__main__":
    user_id = "user123"
    cortex = Cortex(user_id=user_id)
    
    # Ingest various data types
    cortex.ki.ingest_text("Hello, this is a sample text for ingestion.", metadata={"category": "greeting"})
    cortex.ki.ingest_document("documents/sample_doc.pdf", metadata={"category": "document"})
    cortex.ki.ingest_audio("audio/sample_audio.wav", metadata={"category": "audio"})
    cortex.ki.ingest_image("images/sample_image.png", metadata={"category": "image"})
    
    # Batch ingestion
    data_items = [
        ('text', "Another sample text.", {"category": "greeting"}),
        ('document', "documents/another_doc.pdf", {"category": "document"}),
        ('audio', "audio/another_audio.wav", {"category": "audio"}),
        ('image', "images/another_image.png", {"category": "image"}),
        ('unsupported', "unsupported/data.xyz", {"category": "unknown"}),
    ]
    cortex.ki.ingest_batch(data_items)
    
    # Add to memory
    cortex.add_to_memory("Remember that the meeting is at 10 AM tomorrow.", metadata={"context": "meeting_reminder"})
    
    # Handle a user query
    user_query = "What is the meeting schedule?"
    cortex.respond_to_query(user_query)

