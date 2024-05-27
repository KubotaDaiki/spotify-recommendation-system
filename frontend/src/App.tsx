import { useState } from 'react';
import Paper from '@mui/material/Paper';
import InputBase from '@mui/material/InputBase';
import IconButton from '@mui/material/IconButton';
import SearchIcon from '@mui/icons-material/Search';
import Box from '@mui/material/Box';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemText from '@mui/material/ListItemText';

function App() {
  const [tracks, setTracks] = useState([]);

  const fetchTracks = async (trackName: string) => {
    try {
      const url = "http://127.0.0.1:8000";
      const params = { track_name: trackName };
      const query = new URLSearchParams(params);
      const response = await fetch(url + "?" + query);
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      const data = await response.json();
      setTracks(data);
    } catch (error) {
      console.error("There was a problem with the fetch operation:", error);
    }
  };

  return (
    <div>
      <SearchBar onClick={(value) => fetchTracks(value)} />
      <BasicList list={tracks.map((t) => { return t["楽曲"] })} />
    </div>
  );
}

function SearchBar({ onClick }: { onClick: (searchValue: string) => void }) {
  const [value, setValue] = useState("");

  return (
    <Paper
      component="form"
      sx={{ p: '2px 4px', display: 'flex', alignItems: 'center', width: 400 }}
    >
      <InputBase
        sx={{ ml: 1, flex: 1 }}
        placeholder="Search"
        onChange={(e) => setValue(e.target.value)}
      />
      <IconButton
        type="button"
        sx={{ p: '10px' }}
        aria-label="search"
        onClick={() => onClick(value)}
      >
        <SearchIcon />
      </IconButton>
    </Paper>
  );
}


function BasicList({ list }: { list: any[] }) {
  return (
    <Box sx={{ width: '100%', maxWidth: 360, bgcolor: 'background.paper', marginTop: "10px" }}>
      <List>
        {list.map((item) => {
          return (
            <ListItem key={item}>
              <ListItemButton>
                <ListItemText primary={item} />
              </ListItemButton>
            </ListItem>
          )
        })}
      </List>
    </Box>
  );
}


export default App;
