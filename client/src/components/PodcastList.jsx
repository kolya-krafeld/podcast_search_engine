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

const PodcastList = (props) => {
  const { entries } = props;
  return (
    <div>
      {entries
        ? entries.map((entry) => (
            <div>
              <div className="collapse text-white !overflow-visible">
                <input type="checkbox" name="my-accordion-1" />
                <div className="collapse-title text-xl font-medium">
                  <div className="float-left">
                    <div className="avatar float-left">
                      <div className="w-16 rounded">
                        <img src="https://daisyui.com/images/stock/photo-1534528741775-53994a69daeb.jpg" />
                      </div>
                    </div>
                    <div className="float-left ml-4">
                      <p className="text-lg">{entry.episode_name}</p>
                      <p className="text-sm text-gray-400">{entry.show_name}</p>
                    </div>
                  </div>
                  <div className="float-right">
                    <IconButton
                      className="!overflow-visible play_button hover:bg-slate-500"
                      aria-label="play snippet"
                      color="primary"
                      onClick={() =>
                        window
                          .open(
                            `https://open.spotify.com/episode/${
                              entry.episode_id
                            }?t=${entry.start_time.split(".")[0]}`,
                            "_blank"
                          )
                          .focus()
                      }
                    >
                      <PlayArrowIcon sx={{ color: "white" }} />
                    </IconButton>
                  </div>
                </div>
                <div className="collapse-content ">
                  <p className="text-gray-400 text-sm mb-5 line-clamp-3">
                    {entry.episode_description}
                  </p>
                  <p className="font-semibold text-basic mb-1.5">Transcript</p>
                  {entry.snippets.map((snippet) => (
                    <div className="mb-3">
                      <p className="font-medium text-sm mb-1 hover:underline cursor-pointer">
                        <a
                          onClick={() =>
                            window
                              .open(
                                `https://open.spotify.com/episode/${
                                  entry.episode_id
                                }?t=${snippet.start_time.split(".")[0]}`,
                                "_blank"
                              )
                              .focus()
                          }
                        >
                          {toHHMMSS(snippet.start_time.split(".")[0])}
                        </a>
                      </p>
                      <p className="text-gray-400 text-sm">
                        {snippet.transcript_text}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
              <div className="divider my-0"></div>
            </div>
          ))
        : null}
    </div>
  );
};

export default PodcastList;
