import "./App.css";
import React, { useState, useEffect } from "react";
import SearchBar from "./components/SearchBar";
import PodcastList from "./components/PodcastList";

function App() {
  const [searchTerm, setSearchTerm] = useState("");
  const [snippetLength, setSnippetLength] = useState(30);
  const [entries, setEntries] = useState([]);

  const searchPodcastSnippets = async (searchTerm) => {
    try {
      const response = await fetch(
        "http://127.0.0.1:5000/search?q=" + searchTerm
      );
      const data = await response.json();
      console.log(data);
      setEntries(data.episodes);
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <div className="App min-h-screen p-6 max-w-4xl container mx-auto">
        <h1 className="text-3xl text-center font-bold text-white mb-7 mt-4">🎧&nbsp;&nbsp;Podcast Search</h1>
        <SearchBar
        placeholder={"Search for podcast content..."}
        value={searchTerm}
        snippetLength={snippetLength}
        setSnippetLength={setSnippetLength}
        handleInput={(e) => setSearchTerm(e.target.value)}
        handleSubmit={(e) => {
          if (e.key === "Enter") {
            searchPodcastSnippets(searchTerm);
            //setSearchTerm("");
            e.preventDefault();
          }
        }}
      />
      <PodcastList
        entries={entries}
      />
    </div>
  );
}

export default App;
