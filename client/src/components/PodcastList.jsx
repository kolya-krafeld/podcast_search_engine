import React from "react";

import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import ListItemSecondaryAction from "@mui/material/ListItemSecondaryAction";
import ListItemText from "@mui/material/ListItemText";
import ListItemAvatar from "@mui/material/ListItemAvatar";
import Checkbox from "@mui/material/Checkbox";
import Avatar from "@mui/material/Avatar";
import Skeleton from "@mui/material/Skeleton";

const PodcastList = (props) => {
  const { entries, tracks, toggleSelection, loading } = props;

  const getArtistsList = (artists) => {
    return artists.map((artist) => artist.name).join(", ");
  };
  return (
    <div>
      {loading ? (
        //Loading Skeleton
        <List
          dense
          sx={{
            marginBottom: "6rem",
          }}
        >
          {[0, 1, 2, 3, 4, 5].map((item) => (
            <ListItem key={item}>
              <ListItemAvatar>
                <Skeleton
                  variant={tracks ? "rect" : "circle"}
                  width={40}
                  height={40}
                  animation="pulse"
                  sx={{ backgroundColor: "#252020" }}
                />
              </ListItemAvatar>
              <ListItemText>
                <Skeleton
                  variant="text"
                  animation="pulse"
                  sx={{ backgroundColor: "#252020" }}
                />

                <Skeleton
                  variant="text"
                  animation="pulse"
                  sx={{ backgroundColor: "#252020" }}
                />
              </ListItemText>
            </ListItem>
          ))}
        </List>
      ) : (
        <List
          dense
          sx={{
            marginBottom: "6rem",
          }}
        >
          {entries
            ? entries.map((entry) => {
                return (
                  <ListItem
                    key={entry.id}
                    button
                    onClick={() => toggleSelection(entry)}
                  >
                    <ListItemAvatar>
                      {/* <Avatar
                        src={entry?.images[2]?.url}
                        variant={tracks ? "square" : null}
                      /> */}
                    </ListItemAvatar>
                    <ListItemText
                      primary={entry.name}
                      secondary={tracks ? getArtistsList(entry.artists) : null}
                    />
                    <ListItemSecondaryAction
                      onClick={() => toggleSelection(entry)}
                    >
                      <Checkbox edge="end" checked={entry.selected} />
                    </ListItemSecondaryAction>
                  </ListItem>
                );
              })
            : ""}
        </List>
      )}
    </div>
  );
};

export default PodcastList;
