import React from "react";

import Paper from "@mui/material/Paper";
import InputBase from "@mui/material/InputBase";
import SearchIcon from "@mui/icons-material/Search";
import Select from "@mui/material/Select";
import MenuItem from "@mui/material/MenuItem";
import Divider from "@mui/material/Divider";
import FormControl from "@mui/material/FormControl";
import IconButton from '@mui/material/IconButton';
import SettingsIcon from '@mui/icons-material/Settings';

const SearchBar = (props) => {
  const {
    handleInput,
    handleSubmit,
    value,
    placeholder,
    snippetLength,
    setSnippetLength,
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
        <IconButton sx={{ p: "2px" , px: "5px"}} aria-label="settings">
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
    </div>
  );
};

export default SearchBar;
