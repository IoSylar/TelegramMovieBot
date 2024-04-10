# TelegramMovieBot
A Telegram bot that suggests movies based on user input. The system recommends films based on genre, cast, year, and similar movies. It was developed using a RAG (Retrieval Augumented Generation) with llamaindex.

# Data
Data was extracted from the Wikipedia repository, which contains film metadata from 1960 to 2023. The metadata is stored in the movie.json file.

# Indexing
The data will be retrieved, chunked, and indexed into a VectorStore on storage using llamaindex primitives.

# Retrieval
When a user query is received, cosine similarity is calculated between the entries in the vector store. The most similar text chunk is then passed to the LLMs (OpenAI GPT-3.5 in this case).

# Streaming Movies
Once one or more film recommendations are determined by the LLMS, another prompt is used to extract the title(s) of the recommended films. This list of films is then sent as the request body to the streaming-availability API. The API determines streaming links for the film titles on major video content providers such as Amazon Prime Video, Netflix, Now TV, and Apple TV.

# Telegram: 
A Telegram channel was created, utilizing the telegram.ext library to create the Telegram context and actions (e.g., /start and /query) for optimal chatbot usage.

# Screen
![Screenshot](images/telegram2.jpg)
