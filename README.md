# Podcast Search Engine 🎧

The podcast search engine allows users to find relevant podcast episodes that discuss topics they are interested in. The search engine presents short podcast clips that contain the topics the user is looking for. The search engine allows users to directly listen to the clips in Spotify.

Users can pick between **30 seconds**, **2 minute** and **5 minute** podcast clips.


## Demo
![Search Engine Demo](https://github.com/kolya-krafeld/podcast_search_engine/assets/91055239/9c00a347-a9f5-4f3c-a0b9-179ac72d92e4)

## Features

Clicking the Settings icon ⚙️ in the search bar the user can choose between multiple settings of the search engine:
- **Show scores**: Shows the tf_idf score for each podcast clip in the UI.
- **Use OpenApi Query Optimization**: Resolves the query by calling the ChatGPT API and improving the query. This allows users to ask full questions that can be resolved. This can increase the query time because the OpenAPI needs to be called.
- **Number of search results**: Number of relevant podcast clips that will be shown. Up to 50. The clips are grouped together by episode, therefore there might be less episodes visible than clips.
  
**Phrase Search**: You can perform phrase search by adding quotes to the start and end of your query: e.g. `"flat earth"`


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

## Middel-ware

The middle-ware was developed with Python and Flask.

**Requirements:** Make sure `Python`, `pip` and `flask` are installed locally.
Make sure to import the following pip modules: `elasticsearch, dotenv, flask, flask_cors, json, requests, openai, langchain`

To start the middle-ware locally run:
````
cd app # go to app directory
flask --app searcher run # start the middleware
````
The middle-ware will be availbale at `http://127.0.0.1:5000`.

## Indexing

To set up and use our indexing script with Elasticsearch, follow these steps:
1. **Prerequisites:**
   - Ensure `Python` and `pip` (Python's package installer) are installed on your computer.
2. **Install Required Libraries:**
   - Install the necessary Python libraries by running `pip install -r requirements.txt` from the `indexer` directory. This command will install the libraries listed in the `requirements.txt` file, including `elasticsearch`, `python-dotenv`, `os-sys`, and `hashlib`.
3. **Set Up Elasticsearch:**
   - Create a [Cloud Elastic account](https://www.elastic.co/).
   - Once your account is set up, create a project and retrieve your Endpoint & API keys.
4. **Configure Environment Variables:**
   - Save your `API_KEY` and the Elasticsearch endpoint `CLOUD_ENDPOINT` in a local `.env`.
5. **Prepare Data:**
   - Place your data files under `data/podcast-transcripts` in preparation for indexing.
6. **Run the Indexer Script:**
   - Execute the script by running `python indexer.py` from the `indexer` directory to start the indexing process.

 

