from plexapi.server import PlexServer
from plexapi.exceptions import NotFound
from plexapi.video import Episode, Show, Season
import ffmpeg
from whisper_grpc.utils.logging_config import *


class ClientPlexServer:
    def __init__(self, plex_url, plex_token, title: str, show: str, season: str, episode):
        try:
            self.plex = PlexServer(plex_url, plex_token)
            self._logger = logging.getLogger(self.__class__.__name__)
            self._logger.debug('ClientPlexServer initialized')
            self._logger.debug('Plex URL:' + plex_url)
            self._logger.debug('Plex Token:' + plex_token)
            self.show: Show = self.plex.library.section("TV Shows").get(show)
            self.title = title
            self._logger.debug(f'Found show {show}')
            self.season: Season = self.show.season(season)
            self._logger.debug(f'Found season {season}')
            self.episode: Episode = self.season.episode(episode)
            self._logger.debug(f'Found episode {episode}')
        except NotFound:
            self._logger.error(f'No media found with title "{title}"')
            raise NotFound
        except Exception as e:
            self._logger.error(f'Error: {e}')
            raise e
        
    def get_episode(self):
        if self.episode is None:
            raise ValueError('No episode set')
        return self.episode
    
    def get_episode_location(self):
        if self.episode is None:
            raise ValueError('No episode set')
        return self.episode.locations[0]

    def set_next_episode(self):
        if self.episode is None:
            raise ValueError('No episode set')
        episodes = self.show.episodes()
        season_number = self.episode.parentIndex
        episode_number = self.episode.index
        try:
            index = next(i for i, ep in enumerate(episodes) if ep.seasonNumber ==
                         season_number and ep.episodeNumber == episode_number)
            self._logger.debug(f'Found next episode {episodes[index + 1]}')
            self.episode = episodes[index + 1]
            return episodes[index + 1]
        except StopIteration:
            self._logger.error(f'No more episodes found')
            raise NotFound
        except IndexError:
            self._logger.error(f'No more episodes found')
            raise NotFound
        except Exception as e:
            self._logger.error(f'Error: {e}')
            raise e

    def is_anime(self):
        if self.episode is None:
            raise ValueError('No episode set')
        video_file = ffmpeg.probe(self.get_episode_location())
        if any(
            stream["codec_type"] == "audio" and stream["tags"]["language"] == "jpn"
            for stream in video_file["streams"]
        ):
            self._logger.debug(f'Found Japanese audio track')
            return True
        else:
            self._logger.info(
                f'Skipping {self.title} - not an anime TV show')
            return False
