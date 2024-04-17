import React from "react";

import Paper from "@mui/material/Paper";
import InputBase from "@mui/material/InputBase";
import SearchIcon from "@mui/icons-material/Search";
import Select from "@mui/material/Select";
import MenuItem from "@mui/material/MenuItem";
import Divider from "@mui/material/Divider";
import FormControl from "@mui/material/FormControl";
import IconButton from "@mui/material/IconButton";
import SettingsIcon from "@mui/icons-material/Settings";
import Slider from "@mui/material/Slider";

const SearchBar = (props) => {
  const {
    handleInput,
    handleSubmit,
    value,
    placeholder,
    snippetLength,
    setSnippetLength,
    showScores,
    setShowScores,
    useOpenAI,
    setUseOpenAI,
    nrSearchResults,
    setNrSearchResults,
  } = props;

  return (
    <div className="pt-2">
      <Paper
        className="float-left"
        component="form"
        sx={{
          padding: "5px 6px",
          display: "flex",
          alignItems: "center",
          marginBottom: "1rem",
          align: "center",
          width: "calc(100% - 105px);",
        }}
        elevation={0}
      >
        <SearchIcon />
        <InputBase
          sx={{
            marginLeft: "10px",
            flex: 1,
          }}
          placeholder={placeholder}
          value={value}
          onChange={handleInput}
          onKeyPress={handleSubmit}
        />
        <Divider sx={{ height: 20, m: 0.5 }} orientation="vertical" />
        <IconButton
          sx={{ p: "2px", px: "5px" }}
          aria-label="settings"
          onClick={() => document.getElementById("settings_modal").showModal()}
        >
          <SettingsIcon />
        </IconButton>
      </Paper>
      <FormControl
        className="float-right"
        variant="standard"
        sx={{ m: 1, width: 90, margin: 0 }}
      >
        <Select
          labelId="demo-simple-select-standard-label"
          id="demo-simple-select-standard"
          value={snippetLength}
          label="Age"
          className="before:border-none after:border-none hover:border-none focus:border-none"
          sx={{
            backgroundColor: "white",
            borderRadius: "4px",
            padding: "5px 6px",
          }}
          onChange={(e) => setSnippetLength(e.target.value)}
        >
          <MenuItem value={30}>30 s</MenuItem>
          <MenuItem value={120}>2 min</MenuItem>
          <MenuItem value={300}>5 min</MenuItem>
        </Select>
      </FormControl>
      {/* Settings Modal */}
      <dialog id="settings_modal" className="modal text-black">
        <div className="modal-box">
          <form method="dialog">
            {/* if there is a button in form, it will close the modal */}
            <button className="btn btn-sm btn-circle btn-ghost absolute right-2 top-2">
              ✕
            </button>
          </form>
          <h3 className="font-bold text-lg mb-4">Settings</h3>
          <div className="mb-2">
            <label className="font-semibold text-basic mb-1.5 pt-1">
              Show scores
              <input
                type="checkbox"
                value={showScores}
                onChange={() => setShowScores(!showScores)}
                className="checkbox checkbox-sm ml-2 modal-checkbox align-bottom"
              />
            </label>
          </div>
          <div className="mb-4">
            <label className="font-semibold text-basic pt-1">
              Use OpenAI query optimization
              <input
                type="checkbox"
                value={useOpenAI}
                onChange={() => setUseOpenAI(!useOpenAI)}
                className="checkbox checkbox-sm ml-2 align-bottom"
              />
            </label>
            <p className="text-xs">Causes longer query times</p>
          </div>
          <p className="font-semibold text-basic mb-1.5 pt-1">
            Number of search results:
          </p>
          <div className="mx-3">
            <Slider
              aria-label="number of search results"
              value={nrSearchResults}
              onChange={(e, newValue) => setNrSearchResults(newValue)}
              sx={{ color: "#1f2937" }}
              valueLabelDisplay="auto"
              shiftStep={10}
              step={10}
              marks
              min={10}
              max={50}
            />
          </div>
        </div>
      </dialog>
    </div>
  );
};

export default SearchBar;
