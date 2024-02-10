import asyncio
import os
import time
import concurrent.futures
import subprocess
import shlex
from pprint import pformat as pf

class CutterInterface:
	def __init__(self, server):
		self._server = server
		self._mcut_binary = os.path.dirname(__file__) + '/bin/mcut'
		self._reconstruct_apsc_binary = os.path.dirname(__file__) + '/bin/reconstruct_apsc'
		self._ffmpeg_binary = '/usr/bin/ffmpeg'
		self.last_movie = ""
		self.target = ""

	def _long_runtask(self, delay):
		time.sleep(delay)

	def _path_plit(self, movie):
		hlp = movie.locations[0].split('/')
		share = "/".join(hlp[2:3])
		folder = "/".join(hlp[3:-1])
		file = hlp[-1]
		return (share, folder, file)

	def _call(self, exc_lst):
		try:
			res = subprocess.check_output(exc_lst)
			return res
		except subprocess.CalledProcessError as err:
			raise err		

	def _filename(self,movie):
		"""
		the movie filename
		"""
		if len(movie.locations) > 1:
			raise ValueError('cannot handle multiple Files in movie folder')
		else:
			_,_,file = self._path_plit(movie)
			return file

	def _foldername(self,movie):
		"""
		path to the mounted movie folder
		"""
		if len(movie.locations) > 1:
			raise ValueError('cannot handle multiple Files in movie folder')
		else:
			_,path,_ = self._path_plit(movie)
			return os.path.dirname(__file__) + "/mnt/" + path + ("/" if path else "")	

	def _pathname(self,movie):
		"""
		path to the mounted movie file
		"""
		return self._foldername(movie) + self._filename(movie)		

	def _cutfilename(self,movie):
		"""
		the movie cut filename
		"""
		if len(movie.locations) > 1:
			raise ValueError('cannot handle multiple Files in movie folder')
		else:
			return os.path.splitext(self._filename(movie))[0] + ' cut.ts'

	def _cutname(self,movie):
		"""
		path to the mounted movie cut file (inplace = False)
		"""
		return self._foldername(movie) + self._cutfilename(movie)	

	def _tempfilename(self,movie):
		"""
		the movie temp filename @ inplace cutting
		"""
		if len(movie.locations) > 1:
			raise ValueError('cannot handle multiple Files in movie folder')
		else:
			return os.path.splitext(self._filename(movie))[0] + '_.ts'

	def _tempname(self,movie):
		"""
		path to the temporary movie cut file (inplace = true)
		"""
		return self._foldername(movie) + self._tempfilename(movie)

	def _movie_stats(self, movie, cutlist, inplace=False):
		"""
		return TS Progress in percent 
		"""
		self.mount(movie)
		cl = sum([self.cutlength(cut['t0'],cut['t1']) for cut in cutlist])
		ml = (movie.duration / 60000)
		faktor = cl/ml
		moviesize = os.path.getsize(self._pathname(movie))
		targetsize = faktor * moviesize
		if inplace:
			if os.path.exists(self._tempname(movie)):
				progress = os.path.getsize(self._tempname(movie))/targetsize
			else:
				progress = 0
		else:
			if os.path.exists(self._cutname(movie)):
				progress = os.path.getsize(self._cutname(movie))/targetsize
			else:
				progress = 0
		progress = int(progress * 100) if progress < 1.0 else 100
		return progress

	def _apsc_stats(self, movie, cutlist, inplace=False):
		"""
		return AP Progress in percent 
		"""
		self.mount(movie)
		cl = sum([self.cutlength(cut['t0'],cut['t1']) for cut in cutlist])
		ml = (movie.duration / 60000)
		faktor = cl/ml
		moviesize = os.path.getsize(self._pathname(movie))
		targetsize = faktor * moviesize * 0.064 / 1000
		print(f"moviesize: {moviesize} targetsize: {targetsize:.0f} faktor: {faktor:.4f} cl: {cl} ml: {ml:.1f}")
		if inplace:
			if os.path.exists(self._pathname(movie)+'.ap'):
				progress = os.path.getsize(self._pathname(movie)+'.ap')/targetsize
			else:
				progress = 0
		else:
			if os.path.exists(self._cutname(movie)+'.ap'):
				progress = os.path.getsize(self._cutname(movie)+'.ap')/targetsize
			else:
				progress = 0
		progress = int(progress * 100) if progress < 1.0 else 100
		return progress

	def mount(self, movie):
		if len(movie.locations) > 1:
			raise ValueError('cannot cut multiple Files in movie folder')
		else:
			share, path, file = self._path_plit(movie)
			source = f"//{self._server}/{share}"
			target = os.path.dirname(__file__) + "/mnt/"
			mount_lst = ["mount","-t","cifs", "-o", "credentials=/etc/smbcredentials", f"{source}", f"{target}"]
		try:
			if not os.path.exists(self._pathname(movie)):
				# beim ersten mount oder wenn die section sich ändert ...
				print('******remounting necessary')				
				try:
					self.umount()
				except subprocess.CalledProcessError as e:
					print(f'***** neglecting error by intention ****')

				res = subprocess.check_output(mount_lst)
				print(f"{source} mounted.")
				return res
			else:
				pass
				#print('******no mounting needed')
		except subprocess.CalledProcessError as e:
			print(str(e))
			raise e

	def umount(self):
		target = os.path.dirname(__file__) + "/mnt/"
		umount_lst = ["umount","-l",f"{target}"]		
		try:
			res = subprocess.check_output(umount_lst)
			print(f"{target} unmounted.")
			return res
		except subprocess.CalledProcessError as e:
			print(str(e))
			raise e

	def pos2str(self,pos):
		return f"{(pos // 3600):02d}:{((pos % 3600) // 60):02d}:{(pos % 60):02d}"

	def str2pos(self,ps):
		return int(ps[:2])*3600 + int(ps[3:5])*60 + int(ps[-2:])

	def cutlength(self,ss,to):
		return (self.str2pos(to) - self.str2pos(ss)) // 60

	def dstr(self, pos, max, ds):
		val = pos + ds
		val = val if val >=0 else 0
		val = val if val < max else max
		return self.pos2str(val)

	def gen_timeline(self, max, pos, l, r ,step):
		return [self.dstr(pos,max,delta) for delta in range(l*step,(r+1)*step,step)]

	def fname2file(self, ftime):
		if self.target != "":
			return self.target[:-4] + '_' + ftime + self.target[-4:]
		else:
			return ""

	def filter_timelist(self, timelist):
		if self.target == "":
			return timelist
		else: 
			return [ftime for ftime in timelist if not os.path.exists(self.fname2file(ftime))]

	def delete_target_files(self):
		if self.target != "":
			for file in os.listdir(os.path.dirname(self.target)):
				if file.startswith(os.path.basename(self.target)[:-4] + '_'):
					os.remove(os.path.dirname(self.target) + '/' + file)	
		
	def timeline(self, movie, target, size, timelist):
		self.target = target
		if movie.title != self.last_movie: 
			self.delete_target_files()
		#print('Timelist vor dem filtern:')
		#print(pf(timelist))
		timelist = self.filter_timelist(timelist)
		#print('Timelist nach dem filtern:')
		#print(pf(timelist))		
		with concurrent.futures.ThreadPoolExecutor() as executor:
			futures = []
			for ftime in timelist:
				futures.append(executor.submit(self.frame, ftime, size, movie, self.fname2file(ftime)))
			result = []
			for future in concurrent.futures.as_completed(futures):
				result.append(future.result())
		self.last_movie = movie.title
		return 'ok'

	def frame(self, ftime, scale, movie, ftarget):
		t0 = time.time()
		ffstr2 = f"""ffmpeg -ss {ftime} -i "{self._pathname(movie)}" -vframes 1 -q:v 15 \
-vf "scale={scale}:-1, drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf: \
x=(w-text_w)/2: y=(h-text_h)*0.98: fontsize=18: fontcolor=yellow: \
text='{(ftime[:2]+chr(92)+':'+ftime[3:5]+chr(92)+':'+ftime[-2:]).replace('0','O')}':" '{ftarget}' \
-hide_banner -loglevel fatal -max_error_rate 1 -y"""
		exc_lst = shlex.split(ffstr2)
		try:
			subprocess.check_output(exc_lst)
		except subprocess.CalledProcessError as err:
			print(str(err))
			raise(err)
		finally:
			t1 = time.time()
			return f"{(t1-t0):5.2f}"


	def oframe(self,movie, ftime, ftarget = None):
		t0 = time.time()
		#frame_name = 'guid' + PlexInterface.movie_rec(movie)['guid'] + '_' + str(ftime).replace(':','-') + '.jpg'
		frame_name = 'frame.jpg'
		if ftarget == None:
			ftarget = os.path.dirname(__file__) + "/data/"
		ftarget += frame_name
		exc_lst = [self._ffmpeg_binary,"-ss", ftime, "-i", f"{self._pathname(movie)}", 
			"-vframes", "1", "-q:v", "15", "-vf" ,"scale=1024:-1",f"{ftarget}", "-hide_banner", "-loglevel", "fatal", 
			"-max_error_rate","1","-y" ]
		self.mount(movie)
		try:
			res = subprocess.check_output(exc_lst)
			res = res.decode('utf-8')
			print(res)
		except subprocess.CalledProcessError as err:
			print(str(err))
		finally:
			#self.umount()
			t1 = time.time()
			print(f"In frame:{(t1-t0):5.2f} sec.")
			return frame_name

	async def aframe(self,movie, ftime, ftarget = None):
		t0 = time.time()
		#frame_name = 'guid' + PlexInterface.movie_rec(movie)['guid'] + '_' + str(ftime).replace(':','-') + '.jpg'
		frame_name = 'frame.jpg'
		if ftarget == None:
			ftarget = os.path.dirname(__file__) + "/data/"
		ftarget += frame_name
		exc_lst = [self._ffmpeg_binary,"-ss", ftime, "-i", f"{self._pathname(movie)}", 
			"-vframes", "1", "-q:v", "15", "-vf" ,"scale=1024:-1",f"{ftarget}", "-hide_banner", "-loglevel", "fatal", 
			"-max_error_rate","1","-y" ]
		self.mount(movie)
		try:
			res = await subprocess.check_output(exc_lst)
			res = res.decode('utf-8')
			print(res)
		except subprocess.CalledProcessError as err:
			print(str(err))
		finally:
			#self.umount()
			t1 = time.time()
			print(f"\nIn aframe:{(t1-t0):5.2f} sec.")
			return frame_name

	def _apsc(self,movie):
		#check ob .ap und Datei existiert.
		try:
			self.mount(movie)
			return os.path.exists(self._pathname(movie)+'.ap')
		except FileNotFoundError as e:
			print(str(e))
		finally:
			pass
			#self.umount()

	def _apsc_size(self,movie):
		if os.path.exists(self._pathname(movie)+'.ap'):
			return os.path.getsize(self._pathname(movie)+'.ap')
		else:
			return 0

	def _cutfile(self,movie):
		#check ob *_cut.ts Datei existiert.
		try:
			self.mount(movie)
			return os.path.exists(self._cutname(movie))
		except FileNotFoundError as e:
			print(str(e))
		finally:
			pass
			#self.umount()

	def _reconstruct_apsc(self, movie):
		print()
		print(f"'{self._filename(movie)}', *.ap und *.sp Files werden rekonstruiert.")
		exc_lst = [self._reconstruct_apsc_binary,self._pathname(movie)]
		try:
			res = subprocess.check_output(exc_lst)
			res = res.decode('utf-8')
			return res
		except subprocess.CalledProcessError as e:
			raise e
		finally:
			print(f"'{self._filename(movie)}', *.ap und *.sp Files wurden rekonstruiert.")

	def _mcut(self, movie, cutlist, inplace = False):
		print()
		print(f"'{self._filename(movie)}' wird geschnitten. -]+{cutlist}+[- ")
  
		nexc_lst = [self._mcut_binary,"-n",f"'{movie.title}'","-d", f"'{movie.summary}'",f"{self._pathname(movie)}","-c"] + [v for c in cutlist for k,v in c.items()]
		if inplace:
			nexc_lst.insert(1,'-r')
  
		# if inplace:
		# 	nexc_lst = [self._mcut_binary,"-r","-n",f"'{movie.title}'","-d", f"'{movie.summary}'",f"{self._pathname(movie)}","-c"]
		# else:
		# 	nexc_lst = [self._mcut_binary,"-n",f"'{movie.title}'","-d", f"'{movie.summary}'",f"{self._pathname(movie)}","-c"]
   
		# for cut in cutlist:
		# 	for key, value in cut.items():
		# 			nexc_lst.append(value)

		try:
			print("---------------------------------")
			print(f"nexc_lst: {nexc_lst}")
			print("---------------------------------")
			res = subprocess.check_output(nexc_lst)
			res = res.decode('utf-8')
			print(f"'{self._filename(movie)}' wurde geschnitten.")
			return res
		except subprocess.CalledProcessError as e:
			raise e

	def _ffmpegjoin(self, movie, cutlist, inplace = False):
        # ffmpeg -i 'concat:part1.ts|part2.ts' -c copy out.ts
		if len(cutlist) > 1:
			print()
			print(f"'{self._filename(movie)}' wird mit ffmpeg zusammengefügt. -]+{cutlist}+[- ")
			exc_lst = [self._ffmpeg_binary,"-y","-hide_banner","-loglevel","fatal", "-i"]
			file_lst = [f"{self._foldername(movie)}part{i}.ts" for i in range(len(cutlist))]
			exc_lst += [f"concat:" + '|'.join(file_lst),"-c","copy",f"{self._cutname(movie)}.ffmpeg.ts"]
			try:
				print("---------------------------------")
				print(f"exc_lst: {exc_lst}")
				print("---------------------------------")
				res = subprocess.check_output(exc_lst)
				res = res.decode('utf-8')
				print(f"'{self._filename(movie)}' wurde mit ffmeg zusammengefügt.")
				# delete part*.ts files
				for i in range(len(cutlist)):
					os.remove(f"{self._foldername(movie)}part{i}.ts")
				return res
			except subprocess.CalledProcessError as e:
				raise e
		else:
			# rename part0.ts to f"{self._cutname(movie)}.ffmpeg.ts"
			try:
				os.rename(f"{self._foldername(movie)}part0.ts", f"{self._cutname(movie)}.ffmpeg.ts")
				return f"{self._filename(movie)} wurde umbenannt."
			except FileNotFoundError as e:
				raise e

	def _ffmpegcut(self, movie, cutlist, inplace = False):
		print()
		print(f"'{self._filename(movie)}' wird mit ffmpeg geschnitten. -]+{cutlist}+[- ")
		exc_lst = [self._ffmpeg_binary,"-y","-hide_banner","-loglevel","fatal"]
		map_lst = []
		for i, cut  in enumerate(cutlist):
			exc_lst += ["-ss",f"{cut['t0']}","-to",f"{cut['t1']}","-i",f"{self._pathname(movie)}"]
			map_lst += [f"-map",f"{i}:v","-map",f"{i}:a","-map",f"{i}:s?", "-c", "copy", f"{self._foldername(movie)}part{i}.ts"]
		exc_lst += map_lst
		try:
			print("---------------------------------")
			print(f"exc_lst: {exc_lst}")
			print("---------------------------------")
			res = subprocess.check_output(exc_lst)
			res = res.decode('utf-8')
			print(f"'{self._filename(movie)}' wurde mit ffmeg geschnitten.")
			return res
		except subprocess.CalledProcessError as e:
			raise e

	def cut(self, movie, cutlist, inplace=False):
		t0 = time.time()
		t1 = time.time() #initialize t1, in case .ap files already exist ...
		restxt = 'cut started ... \n'
		resdict = {
			'name': movie.title,
			'inplace': inplace
		}
		self.mount(movie)
		#check ob .ap und .sc Dateien existieren, wenn nicht, erzeugen
		restxt += f"{self._filename(movie)} exists ? {os.path.exists(self._pathname(movie))}\n"
		restxt += f"{self._filename(movie)+'.ap'} exists ? {os.path.exists(self._pathname(movie)+'.ap')}\n"
		restxt += f"{self._filename(movie)+'.sc'} exists ? {os.path.exists(self._pathname(movie)+'.sc')}\n\n"

		if ((inplace == False) and (os.path.exists(self._cutname(movie)))):
			try:
				os.remove(self._cutname(movie))
				if os.path.exists(self._cutname(movie)+'.ap'):
					os.remove(self._cutname(movie)+'.ap')
				if os.path.exists(self._cutname(movie)+'.cuts'):
					os.remove(self._cutname(movie)+'.cuts')
				if os.path.exists(self._cutname(movie)+'.sc'):
					os.remove(self._cutname(movie)+'.sc')
				restxt += f"*_cut.ts file existed, deleted ... \n\n"
			except FileNotFoundError as e:
				print(str(e))

		if not os.path.exists(self._pathname(movie)+'.ap'):
			try:
				res = self._reconstruct_apsc(movie)
				t1 = time.time()
				restxt += f"Ergebnis Reconstruct: {res}\n"
				restxt += f"ReSt Zeit: {(t1 - t0):7.0f} sec.\n\n"
				resdict.update({
					'RestApTime': (t1-t0)
				})
			except subprocess.CalledProcessError as e:
				raise e
		
		try:
			res = self._ffmpegcut(movie,cutlist,inplace)
			print("---------------------------------")
			print("FFMPEG cut result: ", res)
			print("---------------------------------")
			res3 = self._ffmpegjoin(movie,cutlist,inplace)
			print("---------------------------------")
			print("FFMPEG cut result: ", res3)
			print("---------------------------------")
			res = self._mcut(movie,cutlist,inplace)
			t2 = time.time()

			if ((inplace == True) and (os.path.exists(self._cutname(movie)))):
				try:
					os.remove(self._cutname(movie))
					if os.path.exists(self._cutname(movie)+'.ap'):
						os.remove(self._cutname(movie)+'.ap')
					if os.path.exists(self._cutname(movie)+'.cuts'):
						os.remove(self._cutname(movie)+'.cuts')
					if os.path.exists(self._cutname(movie)+'.sc'):
						os.remove(self._cutname(movie)+'.sc')
					restxt += f"cut successful, *_cut.ts file deleted.\n"
				except FileNotFoundError as e:
					print(str(e))

			restxt += f"Ergebnis Mcut: {res}\n"
			restxt += f"Mcut Zeit: {(t2 - t1):7.0f} sec.\n"
			restxt += f"Ges. Zeit: {(t2 - t0):7.0f} sec.\n\n"
			resdict.update({
				'McutTime': (t2 - t1),
				'TotalTime': (t2 - t0),
			})
			print(f"elapsed time: {(t2 - t0):7.0f} sec.")
			if self.target != "":
				self.delete_target_files()
				self.target = ""
			#return restxt
			return resdict
		except subprocess.CalledProcessError as e:
			raise e
		finally:
			pass
			#self.umount()
