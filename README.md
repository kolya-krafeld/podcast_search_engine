# Podcast Search Engine 🎧

The podcast search engine allows users to find relevant podcast episodes that discuss topics they are interested in. The search engine presents short podcast clips that contain the topics the user is looking for. The search engine allows users to directly listen to the clips in Spotify.

Users can either put in the exact term they are looking for, or make a request in natural language under the activation of the OpenAI Query Optimization. 

Users can pick between **30 seconds**, **2 minute** and **5 minute** podcast clips.


## Demo
![Search Engine Demo](https://github.com/kolya-krafeld/podcast_search_engine/assets/91055239/9c00a347-a9f5-4f3c-a0b9-179ac72d92e4)

## Features

### Settings

Clicking the Settings icon ⚙️ in the search bar the user can choose between multiple settings of the search engine:
- **Show scores**: Shows the tf_idf score for each podcast clip in the UI.
- **Use OpenAI Query Optimization**: Resolves the query by calling a OpenAI API and improving the query. This allows users to ask requests in natural language form, e.g. `Recommend me something about Kendrick`. It can increase the query time because the OpenAPI needs to be called.
- **Number of search results**: Number of relevant podcast clips that will be shown. Up to 50. The clips are grouped together by episode, therefore there might be less episodes visible than clips.

### Lexical Search  

When LLM query optimization is turned off, the search engine performs a lexical search. The search engine then supports the following types of search:

- **Intersection Search**: Default input.

- **Phrase Search**: By adding quotes to the start and end of your query: e.g. `"flat earth", "climate change"`.

- **Wildcard Search**: `*` will match alternative of any length, and `?` will match alternative of one character. e.g. `flat eart*`. Default as union search.


## Set Up the Elastic Cloud \& Index Your Data

To set up and use our indexing script with Elasticsearch, follow these steps:
1. **Prerequisites:**
   - Ensure `Python` and `pip` (Python's package installer) are installed on your computer.
2. **Install Required Libraries:**
   - Install the necessary Python libraries by running `pip install -r requirements.txt` from the `indexer` directory. This command will install the libraries listed in the `requirements.txt` file, including `elasticsearch`, `python-dotenv`, `os-sys`, and `hashlib`.
3. **Set Up Elasticsearch:**
   - Create a [Cloud Elastic account](https://www.elastic.co/).
   - Once your account is set up, create a project and retrieve your Cloud_id, Endpoint & API keys.
     - Remember to open the privileges for your API key.
4. **Configure Environment Variables:**
   - Save your Elastic Cloud Instance id `CLOUD_ID`, the Elasticsearch endpoint `CLOUD_ENDPOINT` and `API_KEY` in a local `.env`.
5. **Prepare Data:**
   - Place your data files under `data/podcast-transcripts` in preparation for indexing.
6. **Configure Indexing Parameters:**
   - Modify variables in the `indexer.py` script before running it. Set `allow_overlap` to determine if podcast snippets can overlap, adjust `document_size` to control the snippet length in seconds, and specify `index_name` to name the Elasticsearch index where your data will be stored. These settings allow for customization based on your specific indexing needs.
8. **Run the Indexer Script:**
   - Execute the script by running `python indexer.py` from the `indexer` directory to start the indexing process.


## Run the search engine

### Front-end

The front-end was developed with React and JavaScript.

**Requirements:** Make sure `Node.js` and `npm` are installed on your machine.

To start the UI locally run:
````
cd client # go to client directory
npm install # install all required node modules
npm start # start the React frontend
````
The front-end will be available at `localhost:3000`.

### Middle-ware

The middle-ware was developed with Python and Flask.

**Requirements:** Make sure `Python`, `pip` and `flask` are installed locally.
Make sure to import the following pip modules: `elasticsearch, dotenv, flask, flask_cors, json, requests, openai, langchain`

To start the middle-ware locally run:
````
cd app # go to app directory
flask --app searcher run # start the middleware
````
The middle-ware will be availbale at `http://127.0.0.1:5000`.

### OpenAI Query Optimization

The OpenAI Query Optimization is developed based on Lang-Chain, currently utilizing gpt-3.5-turbo model.

1. **Environment:** Make sure `langchain-cli` are installed locally.
2. **Config:** Adding your `OPENAI_API_KEY` to a `.env` file. In the `chain.py` file, adding the name of your indices to `INCLUDE_INDICES`.

You can turn on the LLM Query Optimization in the settings of the search engine.

NOTICE: The program will have to automatically query for the cloud, so please make sure the privileges of the Cloud API key are set as open.

