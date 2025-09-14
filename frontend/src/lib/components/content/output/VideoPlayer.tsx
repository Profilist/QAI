import ReactPlayer from "react-player";
import {
  MediaController,
  MediaControlBar,
  MediaTimeRange,
  MediaTimeDisplay,
  MediaVolumeRange,
  MediaPlaybackRateButton,
  MediaPlayButton,
  MediaSeekBackwardButton,
  MediaSeekForwardButton,
  MediaMuteButton,
  MediaFullscreenButton,
} from "media-chrome/react";

export default function VideoPlayer({ src }: { src: string }) {
  return (
    <MediaController
      style={{
        width: "100%",
        height: "100%",
      }}
    >
      <ReactPlayer
        slot="media"
        src={src}
        controls={false}
        style={{
          width: "100%",
          height: "100%",
        }}
      ></ReactPlayer>
      <MediaControlBar>
        <MediaPlayButton className="px-1"/>
        <MediaSeekBackwardButton seekOffset={10} className="px-1"/>
        <MediaSeekForwardButton seekOffset={10} className="px-1"/>
        <MediaTimeRange className="px-1"/>
        <MediaTimeDisplay showDuration className="px-1"/>
        <MediaMuteButton className="px-1"/>
        <MediaVolumeRange className="px-1"/>
        <MediaPlaybackRateButton className="px-1"/>
        <MediaFullscreenButton className="px-1"/>
      </MediaControlBar>
    </MediaController>
  );
}
