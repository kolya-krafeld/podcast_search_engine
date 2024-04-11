import "./App.css";
import React, { useState, useEffect } from "react";
import SearchBar from "./components/SearchBar";
import PodcastList from "./components/PodcastList";

function App() {
  const [searchTerm, setSearchTerm] = useState("");
  const [entries, setEntries] = useState([]);

  const searchPodcastSnippets = async (searchTerm) => {
    try {
      const response = await fetch(
        "http://127.0.0.1:5000/search?q=" + searchTerm
      );
      const data = await response.json();
      console.log(data);
      setEntries(data.unformated_results);
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <div className="App min-h-screen p-6">
        <SearchBar
        placeholder={"Search for podcast content..."}
        value={searchTerm}
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
