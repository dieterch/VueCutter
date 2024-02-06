from dplexapi.dcut import CutterInterface
from dplexapi.dplex import PlexInterface
import tomllib
from io import BytesIO
from jinja2 import Template

xspf_template = """<?xml version="1.0" encoding="UTF-8"?>
<playlist xmlns="http://xspf.org/ns/0/" xmlns:vlc="http://www.videolan.org/vlc/playlist/ns/0/" version="1">
	<title>Wiedergabeliste</title>
	<trackList>{% for item in data %}
		<track>
            <title>{{ item['title'] }}</title>
			<location>{{ item['url'] }}</location>
			<duration>{{ item['dur'] }}</duration>
			<extension application="http://www.videolan.org/vlc/playlist/0">
				<vlc:id>{{ item['i'] }}</vlc:id>
			</extension>
		</track>{% endfor %}
	</trackList>
	<extension application="http://www.videolan.org/vlc/playlist/0">
		<vlc:item tid="0"/>
	</extension>
</playlist>"""

class Plexdata:
    def __init__(self) -> None:
        with open("config.toml", mode="rb") as fp:
            self.cfg = tomllib.load(fp)
        self.plex = PlexInterface(self.cfg["plexurl"],self.cfg["plextoken"])
        self.cutter = CutterInterface(self.cfg["fileserver"])
        
        # initialization.
        self.initial_section = self.plex.sections[0]
        self.initial_movie_key = 0
        self.initial_series_key = 0
        self.initial_season_key = 0
        self.initial_movie = self.initial_section.recentlyAdded()[self.initial_movie_key]

        self._selection = { 
            'section_type': self.initial_section.type,
            'sections' : [s for s in self.plex.sections if ((s.type == 'movie') or (s.type == 'show'))],
            'section' : self.initial_section,
            'seasons' : None,
            'season' : None,
            'series' : None,
            'serie' : None,
            'movies' : self.initial_section.recentlyAdded(),
            'movie' : self.initial_movie,
            'pos_time' : '00:00:00'
            }

    async def streamsectionall(self):
        sec = self._selection['section']
        mov = sec.all()
        data = []
        for i,m in enumerate(mov):
            data.append({'i':i, 'title':m.title.replace('&','&amp;'), 'url': m.getStreamURL().replace('&','&amp;'), 'dur': m.duration})
        j2_template = Template(xspf_template)
        w = j2_template.render(data=data)    
        b = BytesIO(w.encode('utf-8','xmlcharrefreplace'))
        b.seek(0)
        return b

    async def streamsection(self):
        movies = self._selection['movies']
        data = []
        for i,m in enumerate(movies):
            data.append({'i':i, 'title':m.title.replace('&','&amp;'), 'url': m.getStreamURL().replace('&','&amp;'), 'dur': m.duration})
        j2_template = Template(xspf_template)
        w = j2_template.render(data=data)    
        b = BytesIO(w.encode('utf-8','xmlcharrefreplace'))
        b.seek(0)
        return b
    
    async def streamurl(self):
        m = self._selection['movie']
        data = [{'i':0, 'title':m.title.replace('&','&amp;'), 'url': m.getStreamURL().replace('&','&amp;'), 'dur': m.duration}]
        j2_template = Template(xspf_template)
        w = j2_template.render(data=data)    
        b = BytesIO(w.encode('utf-8','xmlcharrefreplace'))
        b.seek(0)
        return b
    
    def get_selection(self):
        ret = {
                'sections': [s.title for s in self._selection['sections']], 
                'section': self._selection['section'].title,
            }
        if self._selection['section'].type == "movie": #movie sections
            ret.update({ 
                'section_type': 'movie',
                'movies': [m.title for m in self._selection['movies']], 
                'movie': self._selection['movie'].title,
                'pos_time' : self._selection['pos_time']    
            })
        elif self._selection['section'].type == "show": #series section
            ret.update({
                'section_type': 'show',
                'series':[s.title for s in self._selection['series']],
                'serie': self._selection['serie'].title,
                'seasons': [season.title for season in self._selection['serie'].seasons()] if self._selection['section'].type == 'show' else [],
                'season': self._selection['season'].title,
                'movies': [e.title for e in self._selection['season']], 
                'movie': self._selection['movie'].title,
                'pos_time' : self._selection['pos_time']   
            })
        else:
            raise ValueError('Unknown section type')
        return ret
    
    async def _update_section(self, section_name, force=False):
        if ((self._selection['section'].title != section_name) or force):
            section = self.plex.server.library.section(section_name)
            if section.type == 'movie':
                movies = section.recentlyAdded()
                default_movie = movies[self.initial_movie_key]
                self._selection.update({ 
                    'section_type': 'movie',
                    'section' : section,
                    'series' : None,
                    'serie' : None, 
                    'seasons' : None,
                    'season' : None,
                    'movies' : movies, 
                    'movie' : default_movie 
                })
            elif section.type == 'show':
                series = section.all()
                serie = series[self.initial_series_key]
                seasons = serie.seasons()
                season = seasons[self.initial_season_key]
                movies = season.episodes()
                default_movie = movies[self.initial_movie_key]
                self._selection.update({ 
                    'section_type': 'show',
                    'section' : section,
                    'series' : series,
                    'serie' : serie, 
                    'seasons' : seasons,
                    'season' : season,
                    'movies' : movies, 
                    'movie' : default_movie 
                })
            else:
                raise ValueError('Unknown Plex section type.')           
        else:
            pass # no change in section
        return self._selection['section']  
    
    async def _update_serie(self, serie_name, force=False):
        if ((self._selection['serie'].title != serie_name) or force): 
            print('*********** new',serie_name)
            section = self._selection['section']
            serie = [s for s in section.all() if s.title == serie_name][0]
            seasons = serie.seasons()
            season = seasons[self.initial_season_key]
            movies = season.episodes()
            default_movie = movies[self.initial_movie_key]
            self._selection.update({ 
                'serie': serie, 
                'seasons' : seasons,
                'season': season, 
                'movies' : movies, 
                'movie' : default_movie 
            })
        else:
            pass
        return self._selection['serie']
    
    async def _update_season(self, season_name, force=False):
        if ((self._selection['season'].title != season_name) or force): 
            print('*********** new',season_name)
            serie = self._selection['serie']
            season = serie.season(season_name)
            movies = season.episodes()
            default_movie = movies[self.initial_movie_key]
            self._selection.update({ 'season' : season, 'movies' : movies, 'movie' : default_movie })
        else:
            pass
        return self._selection['season']
    
    async def _update_movie(self, movie_name):
        sel_movie = self._selection['movies'][self.initial_movie_key]
        if movie_name != '':
            lmovie = [m for m in self._selection['movies'] if m.title == movie_name]
            if lmovie:
                sel_movie = lmovie[0]
        self._selection['movie'] = sel_movie
        return self._selection['movie']