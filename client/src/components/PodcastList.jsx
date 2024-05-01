import React from "react";
import PlayArrowIcon from "@mui/icons-material/PlayArrow";
import IconButton from "@mui/material/IconButton";

const toHHMMSS = (secs) => {
  var sec_num = parseInt(secs, 10);
  var hours = Math.floor(sec_num / 3600);
  var minutes = Math.floor(sec_num / 60) % 60;
  var seconds = sec_num % 60;

  return [hours, minutes, seconds]
    .map((v) => (v < 10 ? "0" + v : v))
    .filter((v, i) => v !== "00" || i > 0)
    .join(":");
};

const msToTime = (duration) => {
  var seconds = Math.floor((duration / 1000) % 60),
    minutes = Math.floor((duration / (1000 * 60)) % 60),
    hours = Math.floor((duration / (1000 * 60 * 60)) % 24);

  if (hours > 0) {
    return hours + " hr " + minutes + " min";
  } else if (minutes > 0) {
    return minutes + " min " + seconds + " sec";
  } else {
    return seconds + " sec";
  }
};

// Returns every snippet except the first one and sorts them by start time
const getMoreRelevantClips = (snippets) => {
  return snippets.slice(1).sort((a, b) => a.start_time - b.start_time);
};

const formatTime = (time) => {
  return typeof time === "string" ? time.split(".")[0] : parseInt(time, 10);
};

const PodcastList = (props) => {
  const { entries, showScores } = props;
  return (
    <div>
      {entries
        ? entries.map((entry) => (
            <div>
              <div className="collapse text-white !overflow-visible" toggle={true}>
                <input type="checkbox" name="my-accordion-1" />
                <div className="collapse-title text-xl font-medium">
                  <div className="float-right absolute top-3 right-0">
                    <IconButton
                      className="!overflow-visible play_button hover:bg-slate-500"
                      aria-label="play snippet"
                      color="primary"
                      onClick={() =>
                        window
                          .open(
                            `https://open.spotify.com/episode/${
                              entry.episode_id
                            }?t=${formatTime(entry.snippets[0].start_time)}`,
                            "_blank"
                          )
                          .focus()
                      }
                    >
                      <PlayArrowIcon sx={{ color: "white" }} />
                    </IconButton>
                  </div>
                  <div className="float-left podcast-list-content-left w-9/10">
                    <div className="avatar float-left mr-4">
                      <div className="w-16 rounded">
                        <img
                          src={
                            entry.picture_uri
                              ? entry.picture_uri
                              : "https://i9.ytimg.com/s_p/PLS9KzAlagzUv8W3aaHuOFqt0gudQ9C5-N/maxresdefault.jpg?sqp=CMTc77AGir7X7AMICPG3v8UFEAE=&rs=AOn4CLCRDZREI6ZudEJesoLgw1jCT5zD5Q&v=1487920113"
                          }
                        />
                      </div>
                    </div>
                    <div className="overflow-hidden">
                      <p className="text-lg episode_name">
                        {entry.episode_name}
                      </p>
                      <p className="text-sm text-gray-400">{entry.show_name}</p>
                    </div>
                  </div>
                </div>
                <div className="collapse-content">
                  {entry.release_date && entry.duration_ms ? (
                    <p className="font-medium text-sm mb-2 line-clamp-3">
                      {new Date(entry.release_date).toLocaleString("default", {
                        month: "short",
                      }) +
                        " " +
                        new Date(entry.release_date).getFullYear()}
                      &nbsp;&nbsp;·&nbsp;&nbsp;{msToTime(entry.duration_ms)}
                    </p>
                  ) : null}

                  <p className="text-lg episode_name">
                    {entry.episode_name}
                  </p>
                  <p className="text-gray-400 text-sm mb-7 line-clamp-3 text-justify">
                    {entry.episode_description}
                  </p>
                  {/** Most Relevant Clip */}
                  <p className="font-semibold text-basic mb-1.5 pt-1">
                    Most Relevant Clip
                  </p>
                  <div className="mb-3">
                  {showScores ? <p className="font-medium text-sm mb-1 float-right">{entry.snippets[0].score.toFixed(5)}</p> : null }
                    <p className="font-medium text-sm mb-1 hover:underline cursor-pointer">
                      <a
                        onClick={() =>
                          window
                            .open(
                              `https://open.spotify.com/episode/${
                                entry.episode_id
                              }?t=${formatTime(entry.snippets[0].start_time)}`,
                              "_blank"
                            )
                            .focus()
                        }
                      >
                        {toHHMMSS(formatTime(entry.snippets[0].start_time))}
                      </a>
                    </p>
                    <p className="text-gray-400 text-sm text-justify">
                      {entry.snippets[0].transcript_text}
                    </p>
                  </div>
                  {/** Other relevant clips */}
                  {entry.snippets.length > 1 ? (
                    <>
                      <p className="font-semibold text-basic mb-1.5 pt-2">
                        Other Relevant Clips
                      </p>
                      {getMoreRelevantClips(entry.snippets).map((snippet) => (
                        <div className="mb-3">
                          {showScores ? <p className="font-medium text-sm mb-1 float-right">{snippet.score.toFixed(5)}</p> : null }
                          <p className="font-medium text-sm mb-1 hover:underline cursor-pointer">
                            <a
                              onClick={() =>
                                window
                                  .open(
                                    `https://open.spotify.com/episode/${
                                      entry.episode_id
                                    }?t=${formatTime(snippet.start_time)}`,
                                    "_blank"
                                  )
                                  .focus()
                              }
                            >
                              {toHHMMSS(formatTime(snippet.start_time))}
                            </a>
                          </p>
                          <p className="text-gray-400 text-sm text-justify">
                            {snippet.transcript_text}
                          </p>
                        </div>
                      ))}
                    </>
                  ) : null}
                </div>
              </div>
              <div className="divider my-0 divider before:bg-[#262626] after:bg-[#262626]"></div>
            </div>
          ))
        : null}
    </div>
  );
};

export default PodcastList;
