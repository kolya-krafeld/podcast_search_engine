import React from 'react';

import Paper from '@mui/material/Paper';
import InputBase from '@mui/material/InputBase';
import SearchIcon from '@mui/icons-material/Search';

const SearchBar = (props) => {
  const { handleInput, handleSubmit, value, placeholder } = props;

  return (
    <Paper component="form" sx={{
        padding: '5px 6px',
        display: 'flex',
        alignItems: 'center',
        width: '92%',
        marginLeft: '3%',
        marginBottom: '1rem',
        align: 'center',
      }} elevation={0}>
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
    </Paper>
  );
};

export default SearchBar;