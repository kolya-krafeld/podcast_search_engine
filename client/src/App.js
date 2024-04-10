import "./App.css";
import React, { useState, useEffect } from "react";
import SearchBar from "./components/SearchBar";
import PodcastList from './components/PodcastList';

function App() {
  const [searchTerm, setSearchTerm] = useState("");

  const searchPodcastSnippets = async (searchTerm) => {
    try {
      const response = await fetch("http://127.0.0.1:5000/search?q=" + searchTerm);
      const data = await response.json();
      console.log(data);
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <div className="App">
      <SearchBar
        placeholder={"Search for podcast content..."}
        value={searchTerm}
        handleInput={(e) => setSearchTerm(e.target.value)}
        handleSubmit={(e) => {
          if (e.key === "Enter") {
            searchPodcastSnippets(searchTerm);
            setSearchTerm("");
            e.preventDefault();
          }
        }}
      />
      <PodcastList
        entries={[{name: "Podcast Name", artists: [{name: "Artist Name"}]}]}
        tracks
        loading={false}
      />
    </div>
  );
}

export default App;