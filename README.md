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

To index our search index in Elasticsearch we used the Python script in the `indexer` directory.
**Requirements:** Make sure `Python` and `pip`are installed locally.
Make sure to import the following pip modules: `elasticsearch, python-dotenv, os-sys, hashlib`

Run the `indexer.py` script for indexing.


 

