import logging
from typing import List, Optional
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class RAGService:
    """Service class for handling RAG operations"""
    
    def __init__(self):
        """Initialize the RAG service with default configurations"""
        self.embeddings = OpenAIEmbeddings(model='text-embedding-3-small')
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.6)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, 
            chunk_overlap=200
        )
        self.vector_store = None
        self.retriever = None
        self.chain = None
        self.current_video_id = None
        
        # Initialize the prompt template
        self.prompt = PromptTemplate(
            template="""
            You are a helpful assistant. Answer ONLY from the provided transcript context. 
            If the context is insufficient to answer the query, just say you don't know.
            
            Context: {context}
            Question: {question}
            
            Answer:
            """,
            input_variables=['context', 'question']
        )
        
        logger.info("RAG Service initialized successfully")
    
    def fetch_transcript(self, video_id: str) -> str:
        """
        Fetch transcript from YouTube video
        
        Args:
            video_id (str): YouTube video ID
            
        Returns:
            str: Transcript text
            
        Raises:
            Exception: If transcript fetching fails
        """
        try:
            logger.info(f"Fetching transcript for video ID: {video_id}")
            ytt_api = YouTubeTranscriptApi()
            trans_list = ytt_api.fetch(video_id=video_id, languages=['en'])
            transcript_text = " ".join(snippet.text for snippet in trans_list.snippets)
            
            logger.info(f"Successfully fetched transcript. Length: {len(transcript_text)} characters")
            return transcript_text
            
        except TranscriptsDisabled:
            logger.error(f"Transcripts are disabled for video: {video_id}")
            raise Exception("Transcripts are disabled for this video")
        except Exception as e:
            logger.error(f"Error fetching transcript for video {video_id}: {str(e)}")
            raise Exception(f"Failed to fetch transcript: {str(e)}")
    
    def process_transcript(self, transcript_text: str) -> List[Document]:
        """
        Process transcript text into chunks
        
        Args:
            transcript_text (str): Raw transcript text
            
        Returns:
            List[Document]: List of document chunks
        """
        try:
            logger.info("Processing transcript into chunks")
            chunks = self.text_splitter.create_documents([transcript_text])
            logger.info(f"Created {len(chunks)} chunks from transcript")
            return chunks
        except Exception as e:
            logger.error(f"Error processing transcript: {str(e)}")
            raise Exception(f"Failed to process transcript: {str(e)}")
    
    def create_vector_store(self, chunks: List[Document]) -> None:
        """
        Create vector store from document chunks
        
        Args:
            chunks (List[Document]): List of document chunks
        """
        try:
            logger.info("Creating vector store from chunks")
            self.vector_store = FAISS.from_documents(chunks, self.embeddings)
            self.retriever = self.vector_store.as_retriever(
                search_type="similarity", 
                search_kwargs={"k": 2}
            )
            logger.info("Vector store created successfully")
            self._setup_chain()
        except Exception as e:
            logger.error(f"Error creating vector store: {str(e)}")
            raise Exception(f"Failed to create vector store: {str(e)}")
    
    def _setup_chain(self) -> None:
        """Setup the RAG chain for question answering"""
        try:
            logger.info("Setting up RAG chain")
            
            def format_docs(retrieved_docs):
                """Format retrieved documents for the prompt"""
                return "\n\n".join(doc.page_content for doc in retrieved_docs)
            
            # Create the parallel chain
            parallel_chain = RunnableParallel({
                'context': self.retriever | RunnableLambda(format_docs),
                'question': RunnablePassthrough()
            })
            
            # Create the main chain
            self.chain = parallel_chain | self.prompt | self.llm | StrOutputParser()
            logger.info("RAG chain setup completed")
            
        except Exception as e:
            logger.error(f"Error setting up RAG chain: {str(e)}")
            raise Exception(f"Failed to setup RAG chain: {str(e)}")
    
    def process_video(self, video_id: str) -> dict:
        """
        Process a YouTube video for RAG
        
        Args:
            video_id (str): YouTube video ID
            
        Returns:
            dict: Processing results
        """
        try:
            logger.info(f"Starting video processing for: {video_id}")
            
            # Fetch transcript
            transcript_text = self.fetch_transcript(video_id)
            
            # Process transcript into chunks
            chunks = self.process_transcript(transcript_text)
            
            # Create vector store
            self.create_vector_store(chunks)
            
            # Update current video ID
            self.current_video_id = video_id
            
            result = {
                "message": "Video processed successfully",
                "video_id": video_id,
                "chunks_count": len(chunks),
                "transcript_length": len(transcript_text)
            }
            
            logger.info(f"Video processing completed: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing video {video_id}: {str(e)}")
            raise
    
    def ask_question(self, question: str) -> str:
        """
        Ask a question about the processed video
        
        Args:
            question (str): User's question
            
        Returns:
            str: AI-generated answer
        """
        try:
            if not self.chain:
                raise Exception("No video has been processed yet. Please process a video first.")
            
            logger.info(f"Processing question: {question[:100]}...")
            answer = self.chain.invoke(question)
            logger.info("Question answered successfully")
            
            return answer
            
        except Exception as e:
            logger.error(f"Error answering question: {str(e)}")
            raise Exception(f"Failed to answer question: {str(e)}")
    
    def is_ready(self) -> bool:
        """Check if the service is ready to answer questions"""
        return self.chain is not None and self.current_video_id is not None
    
    def get_current_video_id(self) -> Optional[str]:
        """Get the currently processed video ID"""
        return self.current_video_id
